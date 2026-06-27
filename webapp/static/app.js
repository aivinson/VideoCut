const form = document.querySelector("#runForm");
const runButton = document.querySelector("#runButton");
const runStatus = document.querySelector("#runStatus");
const rootPath = document.querySelector("#rootPath");
const gateStatus = document.querySelector("#gateStatus");
const briefPath = document.querySelector("#briefPath");
const gateList = document.querySelector("#gateList");
const artifactList = document.querySelector("#artifactList");
const errorBox = document.querySelector("#errorBox");
const lastRun = document.querySelector("#lastRun");

function formPayload() {
  const data = new FormData(form);
  return {
    project: data.get("project"),
    topic: data.get("topic"),
    platform: data.get("platform"),
    target_count: Number(data.get("target_count")),
    duration_min: Number(data.get("duration_min")),
    duration_max: Number(data.get("duration_max")),
    width: Number(data.get("width")),
    height: Number(data.get("height")),
    aspect_ratio: data.get("aspect_ratio"),
    pace: data.get("pace"),
    subtitle_style: data.get("subtitle_style"),
    opening: data.get("opening"),
    videos_dir: data.get("videos_dir"),
    audio_dir: data.get("audio_dir"),
    outputs_dir: data.get("outputs_dir"),
    logs_dir: data.get("logs_dir"),
    dry_run: data.get("dry_run") === "on",
    avoid_repeated_opening: data.get("avoid_repeated_opening") === "on",
    human_review_required: data.get("human_review_required") === "on",
  };
}

function renderGates(gates) {
  gateList.innerHTML = "";
  for (const check of gates.checks || []) {
    const item = document.createElement("div");
    item.className = `gate ${check.status === "pass" ? "pass" : "fail"}`;
    item.innerHTML = `<strong>${check.name}: ${check.status}</strong><span>${check.message}</span>`;
    gateList.appendChild(item);
  }
}

function renderArtifacts(summary) {
  artifactList.textContent = JSON.stringify(summary.artifacts || {}, null, 2);
}

async function loadStatus() {
  const response = await fetch("/api/status");
  const status = await response.json();
  rootPath.textContent = status.root;
  document.querySelector("#videosDir").value = status.default_videos_dir;
  document.querySelector("#audioDir").value = status.default_audio_dir;
  document.querySelector("#outputsDir").value = status.default_outputs_dir;
  document.querySelector("#logsDir").value = status.default_logs_dir;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  runButton.disabled = true;
  runStatus.textContent = "执行中";
  errorBox.textContent = "无";

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formPayload()),
    });
    const result = await response.json();
    if (!result.ok) {
      throw new Error(result.error || "执行失败");
    }

    gateStatus.textContent = result.summary.gate_status;
    briefPath.textContent = result.brief_path;
    lastRun.textContent = new Date().toLocaleString();
    renderGates(result.gates);
    renderArtifacts(result.summary);
    runStatus.textContent = "完成";
  } catch (error) {
    runStatus.textContent = "失败";
    errorBox.textContent = error.message;
  } finally {
    runButton.disabled = false;
  }
});

loadStatus().catch((error) => {
  rootPath.textContent = "状态读取失败";
  errorBox.textContent = error.message;
});

