import ipaddress
import json
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from discovery import discover_devices
from network import get_network_info
from network_graph import create_network_graph
from models import Device
from search import search_devices
from sorting import sort_devices


BASE_DIR = Path(__file__).resolve().parent
MAX_SCAN_HOSTS = 4094
app = FastAPI(title="NetGraph", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="netgraph-scan")
_lock = threading.Lock()
_network_cache_lock = threading.Lock()
_scan = {"status": "idle", "devices": [], "new_devices": [], "error": None}
_known_device_ids = None
_network_info = None
_network = None
_network_cache_time = 0.0
_graph = None
NETWORK_CACHE_SECONDS = 30


def _network_snapshot():
    """Read the OS network configuration once and reuse it briefly."""
    global _network_info, _network, _network_cache_time
    with _network_cache_lock:
        if (
            _network_info is not None
            and time.monotonic() - _network_cache_time < NETWORK_CACHE_SECONDS
        ):
            return _network_info, _network

        info = get_network_info()
        local_ip = info["local_ip"]
        subnet_mask = info.get("subnet_mask")
        network = ipaddress.ip_network(
            f"{local_ip}/{subnet_mask or '24'}", strict=False
        )
        _network_info, _network = info, network
        _network_cache_time = time.monotonic()
        return info, network


def _is_loopback(request: Request) -> bool:
    host = request.client.host if request.client else ""
    try:
        return ipaddress.ip_address(host.split("%", 1)[0]).is_loopback
    except ValueError:
        return False


@app.middleware("http")
async def local_only(request: Request, call_next):
    if request.url.path.startswith("/api/") and not _is_loopback(request):
        return HTMLResponse("Local access only", status_code=403)
    return await call_next(request)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/network")
def network_endpoint(request: Request):
    if not _is_loopback(request):
        raise HTTPException(403, "Local access only")
    try:
        info, network = _network_snapshot()
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        raise HTTPException(503, f"Could not read local network: {error}") from error
    _network_info, _network = info, network
    return {**info, "subnet": str(network), "scan_limit": MAX_SCAN_HOSTS}


def _device_id(device):
    return (device.get("mac") or device.get("ip") or "").strip().lower()


def _run_scan():
    global _graph, _known_device_ids
    try:
        info, network = _network_snapshot()
        if not network.is_private or ipaddress.ip_address(info["local_ip"]) not in network:
            raise ValueError("Scanning is limited to the detected private IPv4 subnet.")
        if network.num_addresses - 2 > MAX_SCAN_HOSTS:
            raise ValueError(
                f"Detected subnet {network} is too large for a local scan "
                f"(limit: {MAX_SCAN_HOSTS} hosts)."
            )
        devices = discover_devices(network)
        devices = [
            Device.from_dict({
                **item,
                "device_type": (
                    "computer" if item.get("ip") == info.get("local_ip")
                    else "router" if item.get("ip") == info.get("gateway")
                    else item.get("device_type", "unknown")
                ),
            }).to_dict()
            for item in devices
        ]
        graph = create_network_graph(devices, info.get("local_ip"), info.get("gateway"))
        with _lock:
            current_ids = {_device_id(device) for device in devices if _device_id(device)}
            new_devices = [] if _known_device_ids is None else [
                device for device in devices
                if _device_id(device) and _device_id(device) not in _known_device_ids
            ]
            _known_device_ids = current_ids
            _scan.update(status="complete", devices=devices, new_devices=new_devices, error=None)
            _graph = graph
    except Exception as error:
        with _lock:
            _scan.update(status="error", error=str(error))


@app.post("/api/scan", status_code=202)
async def start_scan(request: Request):
    if not _is_loopback(request):
        raise HTTPException(403, "Local access only")
    with _lock:
        if _scan["status"] == "running":
            raise HTTPException(409, "A scan is already running")
        _scan.update(status="running", error=None)
    _executor.submit(_run_scan)
    return {"status": "running"}


@app.get("/api/devices")
async def devices_endpoint(
    request: Request, q: str = "", sort_by: str = "ip", reverse: bool = False
):
    if not _is_loopback(request):
        raise HTTPException(403, "Local access only")
    with _lock:
        devices = list(_scan["devices"])
        result = {
            "status": _scan["status"],
            "new_devices": list(_scan.get("new_devices", [])),
            "error": _scan["error"],
        }
    try:
        result["devices"] = sort_devices(search_devices(devices, q), sort_by, reverse)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    return result


@app.get("/api/graph")
async def graph_endpoint(request: Request):
    if not _is_loopback(request):
        raise HTTPException(403, "Local access only")
    with _lock:
        graph = _graph
    if graph is None:
        return {"vertices": [], "edges": []}
    return {
        "vertices": graph.get_vertices(),
        "edges": [{"source": source, "target": target, "weight": weight}
                  for source, target, weight in graph.get_edges()],
    }


def _get_graph(request: Request):
    if not _is_loopback(request):
        raise HTTPException(403, "Local access only")
    with _lock:
        if _graph is None:
            raise HTTPException(409, "Run a scan before using graph algorithms")
        return _graph


def _vertex(graph, value):
    if value not in graph.adjacency:
        raise HTTPException(422, f"Unknown vertex: {value}")
    return value


def _run_algorithm(name, operation):
    started = time.perf_counter()
    result = operation()
    elapsed_ms = (time.perf_counter() - started) * 1000
    log_dir = BASE_DIR / "test log"
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S-%f")
    report = log_dir / f"{timestamp}_{name}.md"
    report.write_text(
        f"# {name} benchmark\n\n"
        f"- Date and time: {datetime.now().astimezone().isoformat(timespec='milliseconds')}\n"
        f"- Algorithm: {name}\n"
        f"- Runtime: {elapsed_ms:.6f} ms\n\n"
        f"## Result\n\n```json\n{json.dumps(result, ensure_ascii=False, indent=2, default=str)}\n```\n",
        encoding="utf-8",
    )
    return {"result": result, "runtime_ms": elapsed_ms, "report": report.name}


@app.post("/api/algorithms/bfs")
async def bfs(request: Request, payload: dict):
    graph = _get_graph(request)
    outcome = _run_algorithm("bfs", lambda: graph.bfs(_vertex(graph, payload.get("start"))))
    return {"order": outcome["result"], "runtime_ms": outcome["runtime_ms"], "report": outcome["report"]}


@app.post("/api/algorithms/dfs")
async def dfs(request: Request, payload: dict):
    graph = _get_graph(request)
    outcome = _run_algorithm("dfs", lambda: graph.dfs(_vertex(graph, payload.get("start"))))
    return {"order": outcome["result"], "runtime_ms": outcome["runtime_ms"], "report": outcome["report"]}


@app.post("/api/algorithms/dijkstra")
async def dijkstra(request: Request, payload: dict):
    graph = _get_graph(request)
    outcome = _run_algorithm("dijkstra", lambda: graph.dijkstra(_vertex(graph, payload.get("start"))))
    distances = outcome["result"]
    return {"distances": {vertex: distance if math.isfinite(distance) else None
                           for vertex, distance in distances.items()},
            "runtime_ms": outcome["runtime_ms"], "report": outcome["report"]}


@app.post("/api/algorithms/a-star")
async def a_star(request: Request, payload: dict):
    graph = _get_graph(request)
    start = _vertex(graph, payload.get("start"))
    goal = _vertex(graph, payload.get("goal"))
    outcome = _run_algorithm("a-star", lambda: graph.a_star(start, goal))
    path, cost = outcome["result"]
    return {"path": path, "cost": cost if math.isfinite(cost) else None,
            "runtime_ms": outcome["runtime_ms"], "report": outcome["report"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="127.0.0.1", port=8000, reload=False)
