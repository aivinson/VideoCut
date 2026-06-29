# VideoCutApp 入口

这是 VideoCut 的普通用户入口文件夹。你以后只需要打开这个文件夹，不用记住后端模块路径。

## 最简单使用

双击：

```text
启动VideoCut.command
```

启动后浏览器打开：

```text
http://127.0.0.1:8765
```

如果浏览器没有自动打开，手动复制上面的地址到浏览器。

## 测试是否正常

双击：

```text
测试VideoCut.command
```

正常会看到：

```text
Ran 8 tests
OK
```

以及：

```text
VideoCut run complete: gates=pass
```

## 常用文件在哪里改

页面结构：

```text
../webapp/static/index.html
```

页面样式：

```text
../webapp/static/styles.css
```

页面交互：

```text
../webapp/static/app.js
```

后端服务：

```text
../webapp/server.py
```

Agent 流程：

```text
../agents/
../harness/
../gates/
```

## 素材和产物

导入的视频素材会进入：

```text
../inputs/videos/
```

导入的音频素材会进入：

```text
../inputs/audio/
```

运行结果会进入：

```text
../outputs/
../logs/
```

这些运行产物默认不会提交到 GitHub。

## 注意

不要直接双击 `../webapp/static/index.html`。直接打开 HTML 只能看页面，不能选择素材并执行任务。

