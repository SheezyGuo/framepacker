# FramePacker 本地化设计文档

## 概述

本地复刻 [FramePacker.cn](https://www.framepacker.cn/) 的全部功能，构建一个离线可用的视频→序列帧/GIF/帧动画一站式工具。核心目标是为「图片→固定视角角色动作视频→提取序列帧」的自动化工作流提供抽帧/编辑/导出环节。

## 架构

**方案：Python CLI 核心 + Vue 3 Web 前端**

```
用户输入 (视频文件)
  │
  ├──→ [Python CLI] extract / dedup / remove-bg / gif / sprite / edit / pipeline
  │        │
  │        └──→ 输出：序列帧目录 / GIF / 精灵表
  │
  └──→ [Vue 3 前端] 可视化操作界面
           │
           ├── 视频上传与预览
           ├── 帧率/时长/分辨率设置
           ├── 帧列表管理 (排序/删除/多选)
           ├── 帧编辑 (Canvas 精修/批量操作)
           └── 导出 (GIF/PNG/精灵表)
```

## Python CLI 核心

### 命令结构

使用 `click` 库实现，入口命令名 `fp` (可配置为 `framepacker`)。

| 命令 | 参数 | 功能 |
|------|------|------|
| `fp extract <video>` | `--fps`, `--output`, `--start`, `--duration`, `--resize` | 从视频提取帧 |
| `fp gif <frames>` | `--fps`, `--output`, `--resize`, `--loop`, `--delay` | 帧序列→GIF |
| `fp sprite <frames>` | `--cols`, `--output`, `--padding`, `--resize` | 帧序列→精灵表 |
| `fp dedup <frames>` | `--threshold` (0.0~1.0), `--output` | 去除相似帧 |
| `fp remove-bg <frames>` | `--model`, `--output` | 批量移除背景 |
| `fp edit <frames>` | `--resize`, `--crop`, `--rotate`, `--grayscale`, `--output` | 批量图像处理 |
| `fp pipeline <config>` | `--config` (YAML/JSON) | 执行预设多步流水线 |

### 依赖

- `ffmpeg` (系统安装，视频处理)
- `Pillow` (图像处理)
- `opencv-python` (帧对比、去重)
- `rembg` (抠图，ONNX 模型离线运行)
- `numpy` (数值计算)
- `click` (CLI 框架)
- `PyYAML` (配置解析)

### pipeline 配置示例

```yaml
# pipeline.yaml
steps:
  - command: extract
    args:
      fps: 12
      output: ./frames
  - command: dedup
    args:
      threshold: 0.92
  - command: remove-bg
    args: {}
  - command: gif
    args:
      fps: 10
      resize: 512x512
      output: result.gif
```

## Vue 3 前端

### 路由

| 路由 | 页面 | 功能 |
|------|------|------|
| `/` | 首页 | 功能介绍 + 快速开始 |
| `/extract` | 视频抽帧 | 上传视频，选帧率/时长，提取帧 |
| `/editor` | 帧编辑器 | 帧列表、逐帧预览、批量操作、去重、抠图 |
| `/export` | 导出 | GIF / 序列帧 / 精灵表，自定义分辨率 |

### 组件树

```
App.vue
├── Header.vue (导航 + Dark Mode)
├── Home.vue
├── VideoUpload.vue (拖拽上传 + 预览)
├── FrameExtractor.vue (参数设置 + Canvas 抽帧)
├── FrameEditor.vue
│   ├── FrameList.vue (多选/排序/删除)
│   ├── FramePreview.vue (缩放预览)
│   ├── BatchToolbar.vue (去重/抠图/换背景/调色)
│   └── FrameCanvas.vue (逐帧精修)
└── ExportPanel.vue (设置 + 进度 + 下载)
```

### 技术选型

- Vue 3 + Vite + Vue Router
- Pinia 状态管理
- fabric.js (帧画布编辑)
- 前端直接调用 Python CLI (通过 `child_process` / 或 Flask 包装)

### CLI ↔ 前端通信

- 初期：通过 `child_process.spawn` 直接调用 Python CLI
- 可选：Flask 包装为 REST API，便于前端调用和进度推送
- 可选：WebSocket 实时推送处理进度

## 目录结构

```
framepacker/
├── cli/                          # Python CLI 核心
│   ├── framepacker/              # Python 包源码
│   │   ├── __init__.py
│   │   ├── cli.py                # Click 入口
│   │   ├── extract.py            # 视频抽帧
│   │   ├── gif.py                # GIF 生成
│   │   ├── sprite.py             # 精灵表合图
│   │   ├── dedup.py              # 去重
│   │   ├── removebg.py           # 抠图
│   │   ├── edit.py               # 批量编辑
│   │   └── pipeline.py           # 流水线执行
│   ├── pyproject.toml
│   └── .venv/
├── frontend/                     # Vue 3 前端
│   ├── src/
│   │   ├── views/                # 页面组件
│   │   ├── components/           # UI 组件
│   │   ├── stores/               # Pinia stores
│   │   ├── api/                  # API 调用层
│   │   └── router/               # 路由定义
│   ├── package.json
│   └── vite.config.js
├── docs/superpowers/specs/       # 设计文档
└── README.md
```

## 用户工作流

### 纯 GUI 模式
1. 打开前端 → 拖入视频 → 设置帧率/时长 → 提取帧
2. 在帧编辑器中预览、排序、去重、抠图、精修
3. 选择导出格式 (GIF/PNG序列/精灵表) → 设置分辨率 → 下载

### 自动化 CLI 模式
```powershell
fp extract input.mp4 --fps 12 --output ./frames
fp dedup ./frames --threshold 0.92
fp remove-bg ./frames
fp gif ./frames --fps 10 --output animation.gif
```

### pipeline 模式
```powershell
fp pipeline workflow.yaml
```

## 约束与原则

- **完全离线**：核心功能不依赖网络 API，rembg 使用本地 ONNX 模型
- **免费**：无需支付第三方服务费用
- **模块化**：CLI 可独立使用，前端只做可视化壳层
- **可扩展**：CLI 命令可组合成任意流水线
