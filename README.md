# FramePacker Local

**视频转序列帧 / GIF / 帧动画 — 完全离线可用**

[FramePacker.cn](https://www.framepacker.cn/) 的本地复刻版。纯 Python CLI + Vue 3 前端双模式，所有处理在本地完成，无需网络。

## 功能

| 功能 | CLI | 前端 |
|------|-----|------|
| 视频抽帧 | `fp extract` | 拖拽上传 + 参数设置 |
| GIF 导出 | `fp gif` | 帧率/循环设置 |
| 精灵表导出 | `fp sprite` | 行列/排列设置 |
| 帧去重 | `fp dedup` | 阈值滑块 + 一键去重 |
| 批量抠图 | `fp remove-bg` | 调用 CLI 指令 |
| 批量编辑(缩放/裁剪/旋转/灰度) | `fp edit` | 调用 CLI 指令 |
| 多步流水线自动化 | `fp pipeline` | YAML 配置文件 |

## 快速开始

### 前置依赖

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) (需加入 PATH)
- Node.js 18+ (仅前端)

### 安装 CLI

```powershell
pip install -e cli/
```

### 启动前端

```powershell
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### CLI 使用

```powershell
# 从视频提取帧
fp extract input.mp4 --fps 12 --output ./frames

# 帧序列转 GIF
fp gif ./frames --fps 10 --output animation.gif

# 创建精灵表
fp sprite ./frames --cols 8 --output sprite.png

# 去重相似帧
fp dedup ./frames --threshold 0.92

# 批量抠图
fp remove-bg ./frames

# 多步流水线 (YAML 配置)
fp pipeline workflow.yaml
```

### 流水线配置示例

```yaml
# workflow.yaml
steps:
  - command: extract
    args:
      fps: 12
      output: ./frames
  - command: dedup
    args:
      threshold: 0.92
  - command: gif
    args:
      fps: 10
      output: result.gif
```

## 前后端联调

前端通过 Flask 后端代理调用 CLI (端口 5080)：

```powershell
# 终端 1: 启动后端
pip install flask flask-cors
python cli/backend/app.py

# 终端 2: 启动前端
cd frontend && npm run dev
```

## 项目结构

```
framepacker/
├── cli/                    # Python CLI 核心
│   ├── framepacker/        # 包源码
│   │   ├── cli.py          # 入口 (click)
│   │   ├── extract.py      # 视频抽帧
│   │   ├── gif.py          # GIF 生成
│   │   ├── sprite.py       # 精灵表
│   │   ├── dedup.py        # 去重
│   │   ├── removebg.py     # 抠图
│   │   ├── edit.py         # 批量编辑
│   │   └── pipeline.py     # 流水线
│   └── backend/app.py      # Flask 包装 (前端联调)
├── frontend/               # Vue 3 前端
│   └── src/
│       ├── views/          # 页面
│       ├── components/     # 组件
│       ├── stores/         # Pinia 状态
│       └── api/            # API 桥接
└── docs/                   # 文档
```

## 许可证

MIT
