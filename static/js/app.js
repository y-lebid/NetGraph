const $ = (selector) => document.querySelector(selector);


let graph = { vertices: [], edges: [] };
let network = {};
let highlightedPath = [];
let canvasAnimId = null;
let nodePositions = new Map();
let draggedNode = null;
let scanState = "IDLE"; 
let scanProgress = 0;


let camera = { x: 0, y: 0, zoom: 1 };
let isPanning = false;
let startPan = { x: 0, y: 0 };

const api = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail || body.error || `Request failed (${response.status})`);
  }
  return body;
};

async function loadNetwork() {
  try {
    network = await api("/api/network");
    $("#local-ip").textContent = network.local_ip || "—";
    $("#subnet").textContent = network.subnet || "—";
    $("#gateway").textContent = network.gateway || "NOT_FOUND";
    $("#scan-status").textContent = `> Interface online. Subnet ${network.subnet || "ready"}.`;
    
    
    initCanvasGraph();
  } catch (error) {
    $("#scan-status").textContent = `> Network initialization failed: ${error.message}`;
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ 
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" 
  })[char]);
}

function renderDevices(devices) {
  $("#device-count").textContent = devices.length;
  $("#header-node-count").textContent = devices.length;

  const local = network.local_ip;
  const ordered = [...devices].sort((a, b) => 
    (a.ip === local ? -1 : b.ip === local ? 1 : a.ip.localeCompare(b.ip, undefined, { numeric: true }))
  );

  $("#device-list").innerHTML = ordered.length ? ordered.map((device) => {
    const isSelf = device.ip === local;
    const isRouter = device.ip === network.gateway;
    const tag = isSelf ? "[TARGET_PC]" : isRouter ? "[GATEWAY]" : "[ACTIVE_NODE]";

    return `
      <div class="device-row-term" onclick="focusNode('${device.ip}')">
        <div>
          <span class="dev-ip">${escapeHtml(device.ip)}</span>
          <span class="dev-type">${tag} ${device.name ? `· ${escapeHtml(device.name)}` : ''}</span>
        </div>
        <div class="text-right">
          <span class="dev-mac">${device.mac ? escapeHtml(device.mac) : "MAC: N/A"}</span>
        </div>
      </div>`;
  }).join("") : '<div class="term-empty-state">[!] No active nodes detected in subnet.</div>';
}

function enableAlgorithms() {
  const start = $("#start-node"), goal = $("#goal-node");
  const options = graph.vertices.map((ip) => `<option value="${escapeHtml(ip)}">${escapeHtml(ip)}</option>`).join("");
  start.innerHTML = options; 
  goal.innerHTML = options;

  const hasVertices = graph.vertices.length > 0;
  start.disabled = goal.disabled = !hasVertices;
  
  document.querySelectorAll("[data-algorithm]").forEach((button) => button.disabled = !hasVertices);
  $("#algorithm-count").textContent = graph.vertices.length;
  $("#vertex-count").textContent = `[ ${graph.vertices.length} VERTICES ]`;
}

function calculateStructuredLayout(width, height) {
  const vertices = graph.vertices;
  if (!vertices.length) return;

  const gateway = network.gateway;
  const selfIp = network.local_ip;

  const routerNodes = vertices.filter(ip => ip === gateway);
  const selfNodes = vertices.filter(ip => ip === selfIp && ip !== gateway);
  const otherNodes = vertices.filter(ip => ip !== gateway && ip !== selfIp);

  nodePositions.clear();

  routerNodes.forEach((id) => {
    nodePositions.set(id, { id, x: width * 0.5, y: height * 0.2, vx: 0, vy: 0 });
  });

  selfNodes.forEach((id) => {
    nodePositions.set(id, { id, x: width * 0.35, y: height * 0.45, vx: 0, vy: 0 });
  });

  const count = otherNodes.length;
  const minSpacing = 110;
  const totalWidthNeeded = Math.max(width * 0.85, count * minSpacing);
  const startX = (width - totalWidthNeeded) / 2 + minSpacing / 2;

  otherNodes.forEach((id, idx) => {
    const isEven = idx % 2 === 0;
    const xPos = count > 1 ? startX + (idx * (totalWidthNeeded / (count - 1 || 1))) : width / 2;
    const yPos = isEven ? height * 0.72 : height * 0.88;

    nodePositions.set(id, {
      id,
      x: xPos + (Math.random() * 20 - 10),
      y: yPos,
      vx: 0,
      vy: 0
    });
  });
}

function initCanvasGraph() {
  const container = $("#graph-canvas");
  container.innerHTML = `
    <canvas id="topology-canvas" class="w-full h-full cursor-grab active:cursor-grabbing"></canvas>
    <div class="absolute bottom-2 right-3 text-[10px] text-neutral-500 font-mono pointer-events-none select-none bg-black/60 px-2 py-1 rounded border border-neutral-800">
      [ DRAG BACKGROUND TO PAN // SCROLL TO ZOOM // DRAG NODES ]
    </div>
  `;
  
  const canvas = $("#topology-canvas");
  const ctx = canvas.getContext("2d");

  function resizeCanvas() {
    canvas.width = container.clientWidth * window.devicePixelRatio;
    canvas.height = container.clientHeight * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }
  resizeCanvas();

  const width = container.clientWidth;
  const height = container.clientHeight;

  if (scanState === "COMPLETE" && graph.vertices.length && nodePositions.size === 0) {
    calculateStructuredLayout(width, height);
  }

  let frameTime = 0;

  function renderFrame() {
    frameTime += 0.03;
    ctx.clearRect(0, 0, width, height);

    ctx.save();
    ctx.translate(camera.x, camera.y);
    ctx.scale(camera.zoom, camera.zoom);

    ctx.strokeStyle = "#161616";
    ctx.lineWidth = 1 / camera.zoom;
    const gridSize = 30;
    
    const startX = Math.floor((-camera.x / camera.zoom) / gridSize) * gridSize - gridSize;
    const endX = Math.ceil((width - camera.x) / camera.zoom / gridSize) * gridSize + gridSize;
    const startY = Math.floor((-camera.y / camera.zoom) / gridSize) * gridSize - gridSize;
    const endY = Math.ceil((height - camera.y) / camera.zoom / gridSize) * gridSize + gridSize;

    for (let x = startX; x < endX; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, startY);
      ctx.lineTo(x, endY);
      ctx.stroke();
    }
    for (let y = startY; y < endY; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(startX, y);
      ctx.lineTo(endX, y);
      ctx.stroke();
    }

    if (scanState === "IDLE" || !graph.vertices.length) {
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.fillStyle = "#ffffff";
      ctx.textAlign = "center";
      ctx.fillText("[ SYSTEM IDLE // AWAITING NETWORK SCAN ]", width / 2, height / 2 - 10);
      
      ctx.fillStyle = "#555555";
      ctx.fillText("Press [ EXECUTE SCAN ] to map topology", width / 2, height / 2 + 15);

      const cx = width / 2;
      const cy = height / 2;
      const scanRadius = (Math.sin(frameTime * 2) * 0.5 + 0.5) * 80 + 30;

      ctx.strokeStyle = "#333333";
      ctx.beginPath();
      ctx.arc(cx, cy, scanRadius, 0, Math.PI * 2);
      ctx.stroke();

      ctx.restore();
      canvasAnimId = requestAnimationFrame(renderFrame);
      return;
    }

    if (scanState === "SCANNING") {
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.fillStyle = "#ffffff";
      ctx.textAlign = "center";
      ctx.fillText(`[ SCANNING LOCAL SUBNET... ${Math.min(100, Math.floor(scanProgress))}% ]`, width / 2, height / 2);

      const scanX = (frameTime * 150) % width;
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(scanX, 0);
      ctx.lineTo(scanX, height);
      ctx.stroke();

      ctx.restore();
      canvasAnimId = requestAnimationFrame(renderFrame);
      return;
    }

    
    nodePositions.forEach((nodeA) => {
      nodePositions.forEach((nodeB) => {
        if (nodeA.id !== nodeB.id) {
          const dx = nodeA.x - nodeB.x;
          const dy = nodeA.y - nodeB.y;
          const dist = Math.hypot(dx, dy) || 1;
          const minDist = 95; 

          if (dist < minDist) {
            const force = (minDist - dist) / dist * 0.08;
            if (nodeA !== draggedNode) {
              nodeA.x += dx * force;
              nodeA.y += dy * force;
            }
            if (nodeB !== draggedNode) {
              nodeB.x -= dx * force;
              nodeB.y -= dy * force;
            }
          }
        }
      });
    });

    
    graph.edges.forEach((edge) => {
      const sourceNode = nodePositions.get(edge.source);
      const targetNode = nodePositions.get(edge.target);
      if (!sourceNode || !targetNode) return;

      const isHighlighted = isEdgeInPath(edge.source, edge.target);

      ctx.beginPath();
      ctx.moveTo(sourceNode.x, sourceNode.y);
      ctx.lineTo(targetNode.x, targetNode.y);

      if (isHighlighted) {
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 3 / camera.zoom;
        ctx.shadowColor = "#ffffff";
        ctx.shadowBlur = 10;
      } else {
        ctx.strokeStyle = "#282828";
        ctx.lineWidth = 1 / camera.zoom;
        ctx.shadowBlur = 0;
      }
      ctx.stroke();
      ctx.shadowBlur = 0;

      
      const pulsePos = (frameTime * 0.5) % 1;
      const px = sourceNode.x + (targetNode.x - sourceNode.x) * pulsePos;
      const py = sourceNode.y + (targetNode.y - sourceNode.y) * pulsePos;

      ctx.beginPath();
      ctx.arc(px, py, isHighlighted ? 3 : 2, 0, Math.PI * 2);
      ctx.fillStyle = isHighlighted ? "#ffffff" : "#555555";
      ctx.fill();
    });

    
    nodePositions.forEach((node) => {
      const isSelf = node.id === network.local_ip;
      const isRouter = node.id === network.gateway;
      const isInPath = highlightedPath.includes(node.id);

      const size = 12;

      ctx.fillStyle = "#000000";
      ctx.strokeStyle = isInPath ? "#ffffff" : "#888888";
      ctx.lineWidth = (isInPath ? 2 : 1) / camera.zoom;

      if (isRouter) {
        
        ctx.beginPath();
        ctx.moveTo(node.x, node.y - size);
        ctx.lineTo(node.x + size, node.y);
        ctx.lineTo(node.x, node.y + size);
        ctx.lineTo(node.x - size, node.y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      } else if (isSelf) {
        
        ctx.fillRect(node.x - size, node.y - size, size * 2, size * 2);
        ctx.strokeRect(node.x - size, node.y - size, size * 2, size * 2);
        ctx.strokeRect(node.x - size + 3, node.y - size + 3, (size - 3) * 2, (size - 3) * 2);
      } else {
        
        ctx.beginPath();
        ctx.arc(node.x, node.y, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
      }

      
      if (isInPath) {
        ctx.strokeStyle = "#ffffff";
        ctx.strokeRect(node.x - size - 4, node.y - size - 4, (size + 4) * 2, (size + 4) * 2);
      }

      
      const ipText = node.id;
      ctx.font = "11px 'JetBrains Mono', monospace";
      const textWidth = ctx.measureText(ipText).width;

      ctx.fillStyle = "#0a0a0a";
      ctx.fillRect(node.x - textWidth / 2 - 4, node.y + 16, textWidth + 8, 16);
      ctx.strokeStyle = isInPath ? "#ffffff" : "#222222";
      ctx.lineWidth = 1 / camera.zoom;
      ctx.strokeRect(node.x - textWidth / 2 - 4, node.y + 16, textWidth + 8, 16);

      ctx.fillStyle = isInPath ? "#ffffff" : "#cccccc";
      ctx.textAlign = "center";
      ctx.fillText(ipText, node.x, node.y + 28);
    });

    ctx.restore();
    canvasAnimId = requestAnimationFrame(renderFrame);
  }

  cancelAnimationFrame(canvasAnimId);
  renderFrame();

  
  function toWorldCoords(screenX, screenY) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: (screenX - rect.left - camera.x) / camera.zoom,
      y: (screenY - rect.top - camera.y) / camera.zoom
    };
  }

  
  canvas.addEventListener("mousedown", (e) => {
    const world = toWorldCoords(e.clientX, e.clientY);

    
    let clickedNode = null;
    nodePositions.forEach((node) => {
      if (Math.hypot(node.x - world.x, node.y - world.y) < 22) {
        clickedNode = node;
      }
    });

    if (clickedNode) {
      draggedNode = clickedNode;
    } else {
      isPanning = true;
      startPan = { x: e.clientX - camera.x, y: e.clientY - camera.y };
    }
  });

  window.addEventListener("mousemove", (e) => {
    if (draggedNode) {
      const world = toWorldCoords(e.clientX, e.clientY);
      draggedNode.x = world.x;
      draggedNode.y = world.y;
    } else if (isPanning) {
      camera.x = e.clientX - startPan.x;
      camera.y = e.clientY - startPan.y;
    }
  });

  window.addEventListener("mouseup", () => {
    draggedNode = null;
    isPanning = false;
  });

  
  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    const newZoom = Math.min(Math.max(0.4, camera.zoom * zoomFactor), 3);

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    camera.x = mouseX - (mouseX - camera.x) * (newZoom / camera.zoom);
    camera.y = mouseY - (mouseY - camera.y) * (newZoom / camera.zoom);
    camera.zoom = newZoom;
  }, { passive: false });
}

function isEdgeInPath(u, v) {
  if (highlightedPath.length < 2) return false;
  for (let i = 0; i < highlightedPath.length - 1; i++) {
    if ((highlightedPath[i] === u && highlightedPath[i+1] === v) ||
        (highlightedPath[i] === v && highlightedPath[i+1] === u)) {
      return true;
    }
  }
  return false;
}

function focusNode(ip) {
  highlightedPath = [ip];
  triggerPathAnimation();
}

function triggerPathAnimation() {
  initCanvasGraph();
}

async function refreshScan() {
  const result = await api("/api/devices");

  if (result.status === "running") {
    scanState = "SCANNING";
    scanProgress = Math.min(95, scanProgress + 15);
    $("#scan-status").textContent = `> Scanning ARP/ICMP table... ${scanProgress}%`;
    $("#header-status").textContent = "SCANNING";
    window.setTimeout(refreshScan, 800);
    return;
  }

  if (result.status === "error") throw new Error(result.error || "Scan failed");
  if (result.status !== "complete") return;

  scanState = "COMPLETE";
  scanProgress = 100;
  graph = await api("/api/graph");
  
  renderDevices(result.devices);
  enableAlgorithms();
  initCanvasGraph();

  $("#scan-status").textContent = `> Scan complete. Discovered ${result.devices.length} active nodes.`;
  $("#header-status").textContent = "ACTIVE";
}

$("#scan-button").addEventListener("click", async () => {
  const button = $("#scan-button");
  button.disabled = true;
  scanState = "SCANNING";
  scanProgress = 10;
  
  $("#scan-status").textContent = "> Initializing socket scanner...";
  $("#header-status").textContent = "INIT";
  initCanvasGraph();

  try {
    await api("/api/scan", { method: "POST", body: "{}" });
    await refreshScan();
  } catch (error) {
    scanState = "IDLE";
    $("#scan-status").textContent = `> Scan error: ${error.message}`;
    $("#header-status").textContent = "ERROR";
  } finally {
    button.disabled = false;
  }
});

document.querySelectorAll("[data-algorithm]").forEach((button) => {
  button.addEventListener("click", async () => {
    const algorithm = button.dataset.algorithm;
    const payload = { 
      start: $("#start-node").value,
      goal: $("#goal-node").value 
    };

    $("#algorithm-result").textContent = `[ EXECUTING ${algorithm.toUpperCase()} ALGORITHM... ]`;

    try {
      const result = await api(`/api/algorithms/${algorithm}`, { 
        method: "POST", 
        body: JSON.stringify(payload) 
      });

      $("#algorithm-result").textContent = JSON.stringify(result, null, 2);

      if (result.path && Array.isArray(result.path)) {
        highlightedPath = result.path;
        triggerPathAnimation();
      }
    } catch (error) {
      $("#algorithm-result").textContent = `> Algorithm execution error: ${error.message}`;
    }
  });
});

window.addEventListener("resize", () => {
  if (graph.vertices.length) initCanvasGraph();
});


window.addEventListener("DOMContentLoaded", () => {
  loadNetwork();
});
