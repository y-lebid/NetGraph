# Architecture and algorithms

## Application flow

1. `network.py` identifies the active interface, local IPv4 address, prefix, and default gateway. Linux uses `ip` JSON output; Windows queries PowerShell network configuration.
2. `discovery.py` pings usable addresses in the detected IPv4 subnet with a bounded thread pool, then merges responses with entries in the operating system's ARP/neighbour table. The web scanner rejects non-private networks and subnets exceeding 4094 usable hosts.
3. `models.py` normalizes device and connection records. `network_graph.py` creates vertices for discovered IP addresses and connects them to the gateway with undirected edges of weight 1.
4. `graph.py` implements the graph data structure and algorithms.
5. `main.py` provides the interactive terminal workflow. `web_app.py` serves `templates/index.html` and static assets, exposes loopback-only API endpoints, and runs scans in a single-worker executor. It caches network information for 30 seconds and writes algorithm timing reports to `test log/`.

The graph describes the application's gateway-centred model. It does not measure or discover actual links between devices.

## Algorithms

- **BFS** visits vertices in queue order from a start vertex. Time complexity is O(V + E).
- **DFS** recursively visits reachable vertices from a start vertex. Time complexity is O(V + E); recursion depth can become a constraint on very large graphs.
- **Dijkstra** computes shortest path costs from a start vertex using repeated minimum-distance selection. This implementation is O(V² + E) and rejects negative edge weights.
- **A\*** uses a priority queue and relaxes edges as in uniform-cost search. Its default heuristic is zero, so current calls behave like Dijkstra for a single destination. A custom heuristic is accepted by the graph API; shortest-path guarantees depend on using a suitable heuristic.

Here, V is the number of vertices and E the number of edges. Current discovered-network edges all have weight 1, so path cost counts graph edges rather than network delay or physical distance.

## Operational limits

- Discovery only considers the automatically selected local IPv4 subnet; web scans are limited to 4094 usable hosts.
- Ping filtering, host firewalls, network isolation, and incomplete neighbour tables can hide devices.
- Windows and Linux use different system commands, so availability and permissions of those utilities affect detection.
- The web API checks that API clients connect over loopback. The app is intended for local use.
- A scan is an active network operation; use it only where you have authorization.

## Screenshots

See [the screenshots directory](screenshots/README.md) for the location and format used for UI captures.
