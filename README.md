# NetGraph

NetGraph is a local network analyzer and graph algorithms project. It detects the computer's network configuration, discovers responding devices on the local IPv4 subnet, and presents the results as a graph. The project includes both a browser interface and an interactive command-line interface.

## Current features

- Detects the local IPv4 address, network interface, default gateway, and subnet information where supported by the operating system.
- Scans the detected private IPv4 subnet using ICMP ping and supplements results with the system ARP table.
- Limits web scans to the detected private subnet and rejects subnets larger than 4094 usable hosts.
- Builds an undirected weighted graph from discovered device addresses, the local address, and the gateway. The current live-network graph connects the local address to the gateway; it does not infer links between other devices.
- Implements breadth-first search (BFS), depth-first search (DFS), Dijkstra's shortest-path distances, and A* path search.
- Shows graph statistics and a terminal graph view in the CLI.
- Provides a FastAPI web panel for scanning, viewing devices and the graph, and running graph algorithms. The web interface supports selecting nodes and visualizing the graph.
- Includes a fixed sample graph for trying the graph algorithms without scanning a network.
- Includes unit tests written with Python's `unittest` framework.

## Requirements

- Python 3.10 or newer
- Windows or Linux
- For the web panel: FastAPI, Uvicorn, and Jinja2 (listed in `requirements.txt`)
- Network scanning depends on the operating system's `ping` and ARP/neighbour-table utilities.

## Setup

Create and activate a virtual environment, then install the dependencies:

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the web application

```bash
python web_app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The server binds to the loopback interface. API requests from non-loopback clients are rejected. A scan runs in a background worker; start it from the web page and wait for the results to appear.

The application scans only the automatically detected private IPv4 subnet. It does not accept a user-provided scan range. A subnet with more than 4094 usable hosts is rejected.

## Run the CLI

```bash
python main.py
```

The CLI can analyze the local network or load the built-in sample graph. Its “Generate test network” menu option currently loads the same fixed sample graph; it does not generate a random graph.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
NetGraph/
├── discovery.py          # ICMP scanning and ARP table parsing
├── graph.py              # Graph data structure and graph algorithms
├── main.py               # Interactive CLI
├── network.py            # Local network configuration and subnet detection
├── network_graph.py      # Builds a graph from discovered devices
├── sample_graph.py       # Fixed sample graph
├── terminal_graph.py     # Text-based graph renderer for the CLI
├── web_app.py            # FastAPI application and API routes
├── templates/
│   └── index.html        # Web interface template
├── static/
│   ├── css/style.css     # Web interface styles
│   └── js/app.js         # Web interface behavior
├── tests/                # unittest test modules
├── requirements.txt
└── README.md
```

## Known limitations

- On Linux, `network.py` currently falls back to a `/24` subnet because the Linux network configuration code does not retrieve the interface subnet mask.
- Device discovery relies on ping responses and the local ARP/neighbour table. Devices that do not respond to ping and are absent from that table may not appear.
- The live graph currently represents discovered devices as vertices and adds a local-computer-to-gateway edge. It does not discover the physical or logical links between all devices.
- Graph vertex and edge add operations are available in the graph implementation; dedicated remove operations and an independently generated random test graph are not currently implemented.
- The shortest-path algorithms operate on the graph's edge weights. Live network edges currently use a weight of 1, so these results describe graph cost rather than measured network latency.

## Scope

NetGraph is intended for educational analysis of a local network that the user owns or is authorized to inspect. Scanning is restricted to the automatically detected private subnet.
