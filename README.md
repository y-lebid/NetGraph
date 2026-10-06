# NetGraph

**NetGraph** is a Python-based local network analyzer and graph algorithms laboratory.

The project is designed to analyze the local network of the computer on which it is running and represent the discovered network as a graph. It also provides a practical environment for applying graph and data structure algorithms.

> **Project status:** In development

## Features

### Currently implemented

- Detect local IP address
- Detect active network interface
- Detect default gateway
- Display basic local network information

### Planned

- Detect local subnet
- Discover devices on the local network
- Represent network devices as a graph
- Add and remove devices and connections
- Search for devices
- BFS traversal
- DFS traversal
- Dijkstra shortest-path algorithm
- Network statistics
- Sample network datasets
- Generated test networks
- CLI interface

## How It Works

NetGraph uses the network configuration of the computer running the program.

```text
┌──────────────────────┐
│       NetGraph       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Local Network Config │
└──────────┬───────────┘
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
    IP   Interface Gateway
     │
     ▼
┌──────────────────────┐
│   Local Network      │
│      Discovery       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Network Graph     │
└──────────┬───────────┘
           │
      ┌────┼────┐
      ▼    ▼    ▼
     BFS  DFS  Dijkstra
```

The project does **not** require the user to enter an arbitrary external IP address. Its primary purpose is analyzing the local network of the machine where NetGraph is running.

## Technologies

- Python 3
- Linux networking utilities
- Graph data structures
- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Dijkstra's algorithm
- Hash tables
- Searching and sorting algorithms

## Project Structure

```text
NetGraph/
├── main.py
├── network.py
├── README.md
└── .gitignore
```

The structure will evolve as new features are implemented.

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd NetGraph
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Run the application:

```bash
python main.py
```

## Example

Currently NetGraph displays basic network information:

```text
╔══════════════════════════╗
║         NetGraph         ║
║  Local Network Analyzer  ║
╚══════════════════════════╝

Local IP Address: 192.168.0.000
Network Interface: enp4s0
Default Gateway: 192.168.0.0
```

## Design Document

The detailed project design and architecture are available in the project design document:

**[Read the Design Document](https://docs.google.com/document/d/15bUXavpJfSmnrsn5froGI-F037A09icnTEvuxfHQL1Q/edit?usp=sharing)**

## Educational Purpose

NetGraph was created as a practical Python project for studying and applying algorithms and data structures.

The project combines theoretical concepts with a real-world networking problem:

```text
Data Structures
       +
Graph Algorithms
       +
Linux Networking
       ↓
     NetGraph
```

The project will demonstrate how algorithms such as BFS, DFS, and Dijkstra can be applied to a network represented as a graph.

## Scope

NetGraph is intended for analyzing networks that the user owns or is authorized to analyze.

The project is focused on local network analysis rather than scanning arbitrary external systems.

## License

This project is currently intended as an educational project.
