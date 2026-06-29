const form = document.querySelector("#runForm");
const runButton = document.querySelector("#runButton");
const analyzeButton = document.querySelector("#analyzeButton");
const runStatus = document.querySelector("#runStatus");
const rootPath = document.querySelector("#rootPath");
const gateStatus = document.querySelector("#gateStatus");
const briefPath = document.querySelector("#briefPath");
const gateList = document.querySelector("#gateList");
const artifactList = document.querySelector("#artifactList");
const errorBox = document.querySelector("#errorBox");
const lastRun = document.querySelector("#lastRun");
const analysisBox = document.querySelector("#analysisBox");
const videoFilePicker = document.querySelector("#videoFilePicker");
const videoFolderPicker = document.querySelector("#videoFolderPicker");
const audioFilePicker = document.querySelector("#audioFilePicker");
const audioFolderPicker = document.querySelector("#audioFolderPicker");
const videoUploadStatus = document.querySelector("#videoUploadStatus");
const audioUploadStatus = document.querySelector("#audioUploadStatus");
const assetCounts = document.querySelector("#assetCounts");
const fileModeWarning = document.querySelector("#fileModeWarning");

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
    requirements: data.get("requirements"),
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

function renderAnalysis(analysis) {
  const env = analysis.environment || {};
  const suggestions = (analysis.suggestions || []).map((item) => `<li>${item}</li>`).join("");
  analysisBox.innerHTML = `
    <div class="analysis-metrics">
      <span>视频：${analysis.videos.length}</span>
      <span>音频：${analysis.audio.length}</span>
      <span>渲染：${env.can_render ? "可渲染 MP4" : "缺少依赖"}</span>
    </div>
    <ul>${suggestions}</ul>
  `;
}

async function loadStatus() {
  const response = await fetch("/api/status");
  const status = await response.json();
  rootPath.textContent = status.root;
  document.querySelector("#videosDir").value = status.default_videos_dir;
  document.querySelector("#audioDir").value = status.default_audio_dir;
  document.querySelector("#outputsDir").value = status.default_outputs_dir;
  document.querySelector("#logsDir").value = status.default_logs_dir;
  assetCounts.textContent = `当前默认目录：视频 ${status.asset_counts.videos} 个，音频 ${status.asset_counts.audio} 个`;
}

async function uploadFiles(kind, files, statusElement) {
  if (!files.length) {
    statusElement.textContent = "未选择";
    return;
  }

  statusElement.textContent = `上传中：${files.length} 个文件`;
  runStatus.textContent = "上传中";
  const body = new FormData();
  for (const file of files) {
    body.append("files", file, file.webkitRelativePath || file.name);
  }

  const response = await fetch(`/api/upload?kind=${kind}`, {
    method: "POST",
    body,
  });
  const result = await response.json();
  if (!result.ok) {
    throw new Error(result.error || "上传失败");
  }

  const skipped = result.skipped.length ? `，跳过 ${result.skipped.length} 个` : "";
  statusElement.textContent = `已导入 ${result.saved.length} 个${skipped}`;
  runStatus.textContent = "就绪";
  await loadStatus();
}

async function analyzeCurrentAssets() {
  analyzeButton.disabled = true;
  runStatus.textContent = "分析中";
  errorBox.textContent = "无";
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formPayload()),
    });
    const result = await response.json();
    if (!result.ok) {
      throw new Error(result.error || "分析失败");
    }
    renderAnalysis(result.analysis);
    runStatus.textContent = "分析完成";
  } catch (error) {
    runStatus.textContent = "失败";
    errorBox.textContent = error.message;
  } finally {
    analyzeButton.disabled = false;
  }
}

if (window.location.protocol === "file:") {
  fileModeWarning.hidden = false;
  runStatus.textContent = "需启动服务";
}

async function handlePickerChange(kind, picker, statusElement) {
  try {
    errorBox.textContent = "无";
    await uploadFiles(kind, [...picker.files], statusElement);
    picker.value = "";
  } catch (error) {
    runStatus.textContent = "失败";
    errorBox.textContent = error.message;
  }
}

videoFilePicker.addEventListener("change", () => handlePickerChange("video", videoFilePicker, videoUploadStatus));
videoFolderPicker.addEventListener("change", () => handlePickerChange("video", videoFolderPicker, videoUploadStatus));
audioFilePicker.addEventListener("change", () => handlePickerChange("audio", audioFilePicker, audioUploadStatus));
audioFolderPicker.addEventListener("change", () => handlePickerChange("audio", audioFolderPicker, audioUploadStatus));
analyzeButton.addEventListener("click", analyzeCurrentAssets);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  runButton.disabled = true;
  runStatus.textContent = "执行中";
  errorBox.textContent = "无";

  try {
    const response = await fetch("/api/produce", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formPayload()),
    });
    const result = await response.json();
    if (!result.ok) {
      throw new Error(result.error || "执行失败");
    }

    gateStatus.textContent = result.render.status;
    briefPath.textContent = result.brief_path;
    lastRun.textContent = new Date().toLocaleString();
    renderAnalysis(result.manifest.analysis);
    gateList.innerHTML = "";
    const gate = document.createElement("div");
    gate.className = `gate ${result.render.status === "complete" ? "pass" : "fail"}`;
    gate.innerHTML = `<strong>hyperframes-render: ${result.render.status}</strong><span>${result.render.message || result.render.output || "已执行"}</span>`;
    gateList.appendChild(gate);
    artifactList.textContent = JSON.stringify(
      {
        hyperframes_project: result.manifest.project_dir,
        index_html: result.manifest.index_html,
        design: result.manifest.design,
        final_mp4: result.render.output,
        render_status: result.render.status,
      },
      null,
      2
    );
    runStatus.textContent = result.render.status === "complete" ? "完成" : "待安装依赖";
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
