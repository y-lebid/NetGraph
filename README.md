# NetGraph

NetGraph discovers responding devices on the computer's detected private IPv4 subnet and displays them as a graph. It offers a browser interface and an interactive terminal interface, with graph traversal and path-finding algorithms.

## Features

- Detects the active IPv4 address, interface, subnet, and default gateway on Windows and Linux.
- Finds devices that respond to ICMP ping or appear in the local ARP/neighbour table.
- Builds an undirected, gateway-centred graph. The graph is a model and does not infer physical links between devices.
- Runs breadth-first search (BFS), depth-first search (DFS), Dijkstra's algorithm, and A*.
- Searches and sorts discovered devices in the web and terminal interfaces.
- Shows graph statistics and algorithm results; web algorithm runs produce Markdown benchmark reports in `test log/`.

## Requirements

- Python 3.10 or newer
- Windows or Linux
- `ping` and ARP/neighbour-table utilities provided by the operating system
- Python packages in `requirements.txt` for the web interface (FastAPI, Uvicorn, Jinja2)

## Installation

Run these commands from the repository directory.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the web interface

```bash
python web_app.py
```

Open <http://127.0.0.1:8000>. The server binds to loopback, and API requests are restricted to loopback clients.

## Run the terminal interface

```bash
python main.py
```

Choose **Analyze my network** and follow the menu prompts.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Network scope and limitations

- The scanner uses the automatically detected private IPv4 subnet; it has no manual range option.
- Subnets with more than 4094 usable hosts are rejected by the web scanner.
- A host may be missed if it neither responds to ping nor appears in the local ARP/neighbour table.
- The gateway-centred graph is not a physical topology map. Live edges have weight 1; path costs are graph-model costs, not latency measurements.
- Network detection depends on `ip` on Linux and PowerShell networking cmdlets on Windows.
- Scan only networks you own or are authorized to inspect.

## Documentation

- [Architecture and algorithms](docs/architecture.md)
- [Screenshots](docs/screenshots/README.md)
- [Changelog](CHANGELOG.md)
- [Citation metadata](CITATION.cff)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
