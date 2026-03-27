# MiniMax MCP Voice

基于 [MiniMax 官方 MCP](https://github.com/MiniMax-AI/MiniMax-MCP) 修改，仅保留**语音/音频**相关功能。

支持 MCP 客户端（如 [Claude Desktop](https://www.anthropic.com/claude)、[Cursor](https://www.cursor.so)、[Windsurf](https://codeium.com/windsurf)、[OpenAI Agents](https://github.com/openai/openai-agents-python) 等）进行文本转语音、声音克隆、声音设计、音频播放等操作。

---

## 可用工具

| 工具 | 描述 | 收费 |
|---|---|---|
| `text_to_audio` | 文本转语音 — 支持多种声音、语速/音量/音调/情感调节、24种语言 | 是 |
| `list_voices` | 列出所有可用声音（系统声音 + 克隆声音） | 否 |
| `voice_clone` | 声音克隆 — 上传音频文件克隆新声音 | 是 |
| `play_audio` | 本地播放音频文件（WAV/MP3），依赖 ffplay | 否 |
| `voice_design` | 声音设计 — 用自然语言描述生成自定义声音并预览 | 是 |

---

## 环境变量

| 变量名 | 说明 | 必填 | 默认值 |
|---|---|---|---|
| `MINIMAX_API_KEY` | MiniMax API 密钥 | 是 | - |
| `MINIMAX_API_HOST` | API 地址 | 是 | - |
| `MINIMAX_MCP_BASE_PATH` | 输出文件保存路径 | 否 | `~/Desktop` |
| `MINIMAX_API_RESOURCE_MODE` | 资源模式：`url` 返回链接，`local` 下载到本地 | 否 | `url` |

**API 地区对照**（Key 和 Host 必须匹配同一地区，否则会报 `invalid api key`）：

| 地区 | MINIMAX_API_KEY | MINIMAX_API_HOST |
|---|---|---|
| 国际版 | [MiniMax 国际版获取](https://www.minimax.io/platform/user-center/basic-information/interface-key) | `https://api.minimax.io` |
| 国内版 | [MiniMax 国内版获取](https://platform.minimaxi.com/user-center/basic-information/interface-key) | `https://api.minimaxi.com` |

---

## 传输方式

支持 `stdio` 和 `SSE` 两种传输模式：

| stdio | SSE |
|---|---|
| 本地运行 | 可本地或云端部署 |
| 通过 stdout 通信 | 通过网络通信 |
| 输入：支持本地文件或 URL | 输入：云端部署建议使用 URL |

---

## 使用方式

### 方式一：本地使用（从源码运行）

适合你修改了代码、想直接用本地版本的场景。

#### 1. 克隆项目并安装依赖

```bash
git clone https://github.com/upseem/MiniMax-MCP-Voice.git
cd MiniMax-MCP-Voice
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e .
```

#### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
MINIMAX_API_KEY=你的API密钥
MINIMAX_API_HOST=https://api.minimaxi.com
MINIMAX_MCP_BASE_PATH=~/Desktop
MINIMAX_API_RESOURCE_MODE=url
```

#### 3. 在 MCP 客户端中配置

**Claude Desktop**

前往 `Claude > Settings > Developer > Edit Config > claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "MiniMax-Voice": {
      "command": "/你的项目路径/MiniMax-MCP-Voice/.venv/bin/python",
      "args": [
        "-m", "minimax_mcp.server"
      ],
      "env": {
        "MINIMAX_API_KEY": "你的API密钥",
        "MINIMAX_API_HOST": "https://api.minimaxi.com",
        "MINIMAX_MCP_BASE_PATH": "~/Desktop",
        "MINIMAX_API_RESOURCE_MODE": "url"
      }
    }
  }
}
```

> 将 `/你的项目路径/` 替换为你实际的项目路径。可通过 `which python`（在虚拟环境中）获取完整路径。

**Cursor**

前往 `Cursor -> Preferences -> Cursor Settings -> MCP -> Add new global MCP Server`，添加同样的配置。

#### 4. 直接运行 stdio 模式（调试用）

```bash
source .venv/bin/activate
python -m minimax_mcp.server
```

#### 5. 以 SSE 模式运行（本地网络服务）

```bash
source .venv/bin/activate
python -m minimax_mcp.server --transport sse --port 8000
```

然后在 MCP 客户端中配置 SSE 地址：

```json
{
  "mcpServers": {
    "MiniMax-Voice": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

### 方式二：线上使用（通过 uvx 直接安装原版）

如果你不需要修改代码，可以直接使用 PyPI 上的原版包（注意：原版包含视频/图片/音乐等全部功能）。

#### 1. 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 在 MCP 客户端中配置

**Claude Desktop**

```json
{
  "mcpServers": {
    "MiniMax": {
      "command": "uvx",
      "args": [
        "minimax-mcp"
      ],
      "env": {
        "MINIMAX_API_KEY": "你的API密钥",
        "MINIMAX_API_HOST": "https://api.minimaxi.com",
        "MINIMAX_MCP_BASE_PATH": "~/Desktop",
        "MINIMAX_API_RESOURCE_MODE": "url"
      }
    }
  }
}
```

> 如果 `uvx` 命令找不到，请运行 `which uvx` 获取绝对路径，然后将 `"command": "uvx"` 替换为 `"command": "/绝对路径/uvx"`。

---

### 方式三：云端部署（SSE 模式）

适合团队共享或部署到服务器的场景。

#### 1. 在服务器上安装并运行

```bash
git clone https://github.com/upseem/MiniMax-MCP-Voice.git
cd MiniMax-MCP-Voice
uv venv && source .venv/bin/activate
uv pip install -e .

# 设置环境变量
export MINIMAX_API_KEY="你的API密钥"
export MINIMAX_API_HOST="https://api.minimaxi.com"
export MINIMAX_MCP_BASE_PATH="/data/output"
export MINIMAX_API_RESOURCE_MODE="url"

# 启动 SSE 服务
python -m minimax_mcp.server --transport sse --host 0.0.0.0 --port 8000
```

#### 2. 客户端连接

在 MCP 客户端中配置远程 SSE 地址：

```json
{
  "mcpServers": {
    "MiniMax-Voice": {
      "url": "https://你的服务器地址:8000/sse"
    }
  }
}
```

> 建议在云端部署时将 `MINIMAX_API_RESOURCE_MODE` 设为 `url`，这样生成的音频以 URL 形式返回，无需下载到服务器本地。

---

## 工具详细说明

### text_to_audio — 文本转语音

将文本转换为音频文件，支持丰富的参数控制。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `text` | str | 是 | - | 要转换的文本 |
| `voice_id` | str | 否 | `female-shaonv` | 语音 ID |
| `model` | str | 否 | `speech-2.6-hd` | 语音模型 |
| `speed` | float | 否 | `1.0` | 语速 (0.5~2.0) |
| `vol` | float | 否 | `1.0` | 音量 (0~10) |
| `pitch` | int | 否 | `0` | 音调 (-12~12) |
| `emotion` | str | 否 | `happy` | 情感：happy/sad/angry/fearful/disgusted/surprised/neutral |
| `sample_rate` | int | 否 | `32000` | 采样率：8000/16000/22050/24000/32000/44100 |
| `bitrate` | int | 否 | `128000` | 比特率：32000/64000/128000/256000 |
| `channel` | int | 否 | `1` | 声道数：1/2 |
| `format` | str | 否 | `mp3` | 格式：pcm/mp3/flac |
| `language_boost` | str | 否 | `auto` | 语言增强（支持24种语言） |
| `output_directory` | str | 否 | 基础路径 | 输出目录 |

### list_voices — 列出可用声音

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `voice_type` | str | 否 | `all` | 筛选类型：all/system/voice_cloning |

### voice_clone — 声音克隆

使用提供的音频文件克隆新声音，分三步：上传文件 -> 克隆声音 -> 生成演示音频。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `voice_id` | str | 是 | - | 新克隆声音的 ID |
| `file` | str | 是 | - | 音频文件路径或 URL |
| `text` | str | 是 | - | 演示音频文本 |
| `is_url` | bool | 否 | `false` | 文件是否为 URL |
| `output_directory` | str | 否 | 基础路径 | 输出目录 |

### play_audio — 播放音频

本地播放音频文件，依赖 `ffplay`（需安装 [ffmpeg](https://ffmpeg.org/)）。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `input_file_path` | str | 是 | - | 音频文件路径 |
| `is_url` | bool | 否 | `false` | 是否为 URL |

### voice_design — 声音设计

用自然语言描述想要的声音特征，自动生成对应声音并预览。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | str | 是 | - | 声音描述提示词 |
| `preview_text` | str | 是 | - | 预览文本 |
| `voice_id` | str | 否 | - | 基础声音 ID（可选） |
| `output_directory` | str | 否 | 基础路径 | 输出目录 |

---

## FAQ

### 1. invalid api key
请确保 API Key 和 API Host 来自同一地区：
- 国际版：Key 从 [MiniMax 国际版](https://www.minimax.io/platform/user-center/basic-information/interface-key) 获取，Host 为 `https://api.minimax.io`
- 国内版：Key 从 [MiniMax 国内版](https://platform.minimaxi.com/user-center/basic-information/interface-key) 获取，Host 为 `https://api.minimaxi.com`

### 2. spawn uvx ENOENT
在终端运行以下命令获取 uvx 的绝对路径：
```bash
which uvx
```
然后将配置中的 `"command": "uvx"` 替换为完整路径，如 `"command": "/usr/local/bin/uvx"`。

### 3. play_audio 无法播放
请确保已安装 ffmpeg：
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载并添加到 PATH
```

---

## 许可证

[MIT License](LICENSE)
