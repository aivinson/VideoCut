# VideoCut

VideoCut is a scaffold for a reusable short-video production agent system.

Repository: `https://github.com/aivinson/VideoCut.git`

The first version focuses on the operating model:

- Skills capture reusable editing knowledge.
- Agents own one module each.
- Gates convert repeated failures into automated checks.
- A harness coordinates the workflow, artifacts, logs, and retrospectives.

## Quick start

```bash
python3 -m harness.run --brief inputs/brief.example.json --dry-run
python3 -m unittest discover -s tests
```

Dry-run mode writes placeholder renders and full manifests so the workflow can be
validated before Whisper, FFmpeg, Auto-Editor, or MoviePy are installed.

## Web UI

```bash
python3 -m webapp.server
```

Open `http://127.0.0.1:8765` to fill in the brief, material folders, and run
the harness from a browser.

For a simpler local entry, open `VideoCutApp/` and double-click
`启动VideoCut.command`.

For Chinese step-by-step usage and testing instructions, see
[`docs/USAGE_AND_TESTING.md`](docs/USAGE_AND_TESTING.md).
