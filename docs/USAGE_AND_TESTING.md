# VideoCut 使用和测试说明

这份文档面向日常使用者：你不需要理解所有代码，也可以验证当前项目是否能跑通。

当前版本是 **MVP 框架**，重点验证 `Skill + Gates + Multi-Agent Harness` 流程。它还不是最终真实剪辑系统：Whisper 转写、FFmpeg 合成、Auto-Editor 自动剪辑后面会接入。现在的 `--dry-run` 会生成占位视频文件、字幕、manifest、质量门禁报告和复盘文件，用来确认流程完整。

## 1. 项目现在能做什么

当前已经能跑通这条链路：

1. 读取任务 brief。
2. 扫描 `inputs/videos/` 和 `inputs/audio/`。
3. 生成占位语音转写。
4. 规划多条同题材短片。
5. 给每条短片选择素材片段。
6. 生成占位 `.mp4`、`.srt` 字幕和 manifest。
7. 跑质量门禁。
8. 生成复盘文件。

## 2. 准备环境

进入项目目录：

```bash
cd /Users/zzy/Documents/VideoCut
```

推荐使用 Codex 自带 Python，因为你本机系统 `python3` 可能会被 Xcode Command Line Tools 卡住：

```bash
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 --version
```

如果这个命令能输出 Python 版本，就可以继续。

## 3. 一键跑通 MVP

### 方式 A：网页入口

最简单方式：打开项目里的入口文件夹：

```text
/Users/zzy/Documents/VideoCut/VideoCutApp/
```

双击：

```text
启动VideoCut.command
```

然后打开：

```text
http://127.0.0.1:8765
```

如果你想用命令行启动，也可以继续看下面。

启动本地网页控制台：

```bash
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m webapp.server
```

打开：

```text
http://127.0.0.1:8765
```

在页面里填写题材、平台、生成数量、时长，并从下拉框选择字幕风格和开头策略。然后点击“选择视频文件 / 选择视频文件夹”或“选择音频文件 / 选择音频文件夹”导入素材。页面会把素材复制到项目默认目录，再点击“开始执行”。执行完成后，右侧会显示 gate 状态、门禁检查和产物路径。

如果浏览器页面打不开，先确认启动命令窗口里出现了：

```text
VideoCut web UI: http://127.0.0.1:8765
```

浏览器为了安全不会把 Finder 里选择文件夹的真实本机路径自动交给服务端；页面现在采用“选择并复制素材”的方式。你可以直接选择单个/多个视频文件，也可以选择整个文件夹。

被选择的素材会复制到项目默认目录：

```text
inputs/videos/
inputs/audio/
```

页面会自动填好这两个默认路径。

### 方式 B：命令行

执行 dry-run：

```bash
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m harness.run --brief inputs/brief.example.json --dry-run
```

成功时你会看到类似：

```text
VideoCut run complete: gates=pass
Summary: /Users/zzy/Documents/VideoCut/outputs/artifacts/gate-report.json
```

这表示完整流程已经跑完，并且当前基础门禁通过。

## 4. 跑测试

执行单元测试：

```bash
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests
```

成功时你会看到类似：

```text
Ran 3 tests in 0.02s

OK
```

## 5. 看进度和产物

dry-run 后主要看这些文件：

| 路径 | 作用 |
| --- | --- |
| `outputs/artifacts/run-summary.json` | 本次运行总摘要 |
| `outputs/artifacts/assets.json` | 素材扫描结果 |
| `outputs/artifacts/transcripts.json` | 转写结果，目前是占位转写 |
| `outputs/artifacts/plans.json` | 短片故事规划 |
| `outputs/artifacts/selections.json` | 每条短片选了哪些素材片段 |
| `outputs/artifacts/assembly.json` | 组装输出记录 |
| `outputs/artifacts/gate-report.json` | 门禁检查结果 |
| `outputs/renders/short_01.mp4` | 占位成片文件 |
| `outputs/subtitles/short_01.srt` | 字幕文件 |
| `outputs/manifests/short_01.json` | 单条短片 manifest |
| `logs/retrospective.md` | 本次运行复盘 |

注意：当前 `.mp4` 是占位文件，不是真正可播放的视频。真实视频合成会在后续 FFmpeg/MoviePy 适配器接入后实现。

## 6. 修改任务 brief

任务配置在：

```text
inputs/brief.example.json
```

常用字段：

```json
{
  "project": "sample-short-video-batch",
  "topic": "productivity tips",
  "platform": "douyin",
  "target_count": 2,
  "duration_seconds": {
    "min": 15,
    "max": 60
  },
  "aspect_ratio": "9:16",
  "resolution": {
    "width": 1080,
    "height": 1920
  }
}
```

你可以先改这几个：

- `topic`：短片题材。
- `platform`：目标平台。
- `target_count`：要生成几条短片。
- `duration_seconds.min/max`：期望时长范围。

改完再执行 dry-run 命令即可。

## 7. 放入真实素材

素材目录：

```text
inputs/videos/
inputs/audio/
```

支持的扩展名：

- 视频：`.mp4`、`.mov`、`.mkv`、`.webm`
- 音频：`.wav`、`.mp3`、`.m4a`、`.aac`、`.flac`

当前版本会扫描这些文件并写入 `outputs/artifacts/assets.json`，但还不会真正解析视频时长、分辨率、编码，也不会真正转写音频。这些能力会在下一阶段通过 FFmpeg/ffprobe 和 Whisper 接入。

## 8. 如何判断项目有没有停住

项目没有停住。当前状态是：

- 第一版 agent/harness/gate 框架已完成。
- dry-run 可以跑通。
- 单元测试可以通过。
- 代码已推送到 GitHub。
- 下一阶段要做的是把占位适配器替换成真实能力。

你可以用这两个命令验证当前进度：

```bash
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m harness.run --brief inputs/brief.example.json --dry-run
```

## 9. Git 查看方式

查看本地是否和 GitHub 同步：

```bash
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/git status -sb
```

如果看到：

```text
## main...origin/main
```

表示当前本地分支和 GitHub 分支同步。

查看最近提交：

```bash
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/git log --oneline --decorate -5
```

## 10. 常见问题

### 系统 `python3` 不能用

如果你运行：

```bash
python3 -m unittest discover -s tests
```

看到 Xcode Command Line Tools 报错，就改用 Codex 自带 Python：

```bash
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests
```

### 为什么输出的 `.mp4` 不能播放

当前是 dry-run MVP，`.mp4` 文件只是占位产物，用来验证文件流、manifest、字幕和门禁。真实可播放视频需要后续接入 FFmpeg/MoviePy。

### 为什么 `outputs/` 和 `logs/` 不提交到 GitHub

这些是运行产物，会不断变化。项目已经在 `.gitignore` 里忽略它们，避免把大量临时文件和生成视频推到仓库。

### 怎么回滚

先看提交历史：

```bash
/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/git log --oneline --decorate -10
```

已经推送到 GitHub 的提交，优先用 `git revert <commit>` 生成回滚提交，不直接改历史。

## 11. 下一阶段建议

下一步优先级建议：

1. 接入 `ffprobe`，让 `asset-ingest-agent` 读取真实时长、分辨率、编码。
2. 接入 Whisper，让 `transcript-agent` 生成真实转写和字幕。
3. 接入 FFmpeg/MoviePy，让 `edit-assembly-agent` 生成可播放视频。
4. 增强 gate，检查黑屏、静音、字幕安全区和真实视频比例。
5. 加入人工反馈入口，把重复问题沉淀进 Skill 和 Gate。
