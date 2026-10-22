# NetGraph

NetGraph discovers devices on the computer's local IPv4 network and displays them as a graph. It includes a browser-based interface and an interactive terminal interface, with graph traversal and path-finding algorithms.

## Design document

[Design Document - NetGraph](https://canva.link/3e6842a4e4ykxtc)

## Features

- Detects the local IPv4 address, network interface, subnet, and default gateway on Windows and Linux.
- Finds responding devices using ICMP ping and the operating system's ARP or neighbour table.
- Builds a weighted graph from discovered devices. The gateway is used as a hub; the application does not infer actual device-to-device links.
- Runs breadth-first search (BFS), depth-first search (DFS), Dijkstra's shortest-distance algorithm, and A* path search.
- Provides device search and sorting in the terminal and web interfaces.
- The terminal interface can render the graph and show network statistics.
- The web interface displays and highlights graph results, and lets you choose start and goal nodes.

## Requirements

- Python 3.10 or newer
- Windows or Linux
- Web interface dependencies from `requirements.txt` (FastAPI, Uvicorn, and Jinja2)
- Network scanning utilities available on the operating system: `ping` and ARP/neighbour-table access

## Installation

From the project directory, create and activate a virtual environment, then install the dependencies.

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

## Run the web interface

```bash
python web_app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), start a scan, then select graph nodes and run an algorithm. The server binds to the local computer; API requests from non-loopback clients are rejected.

## Run the terminal interface

```bash
python main.py
```

Choose **Analyze my network** and follow the prompts to inspect the graph, run an algorithm, or search and sort the discovered devices.

## Search and sorting

Both interfaces can search by IP address, MAC address, name, or device type. The web interface also searches vendor and displayed device role where available. Devices can be sorted by IP, name, type, or MAC address.

## Network scope and limitations

- Scanning is limited to the automatically detected private IPv4 subnet; the application does not accept a manually entered range.
- Scans are rejected when the subnet contains more than 4094 usable hosts.
- Devices that do not respond to ping and are absent from the local ARP/neighbour table may not be discovered.
- The graph represents discovered devices and a gateway-centred topology. It does not map physical links or measure network latency. Live graph edges use a weight of 1, so path costs describe the graph model rather than real latency.
- Use the scanner only on a network you own or are authorized to inspect.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Project layout

```text
NetGraph/
|-- discovery.py          # Device discovery and ARP/neighbour parsing
|-- graph.py              # Graph data structure and algorithms
|-- main.py               # Interactive terminal interface
|-- models.py             # Shared device and connection models
|-- network.py            # Local network configuration
|-- network_graph.py      # Builds a graph from discovered devices
|-- search.py             # Device search helpers
|-- sorting.py            # Device sorting helpers
|-- terminal_graph.py     # Terminal graph renderer
|-- web_app.py            # FastAPI application
|-- templates/
|   `-- index.html         # Web interface template
|-- static/
|   |-- css/style.css      # Web interface styles
|   `-- js/app.js          # Web interface behavior
|-- tests/                 # unittest suite
|-- requirements.txt
`-- README.md
```
