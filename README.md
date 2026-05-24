# 🎮 2D 游戏素材生成工具 - MVP v0.2

## 📋 项目概述

这是一个**高效、低成本、风格一致的 AI 游戏素材生成系统**，使用 Stable Diffusion + LCM 快速生成各类 2D 游戏素材。

### 核心特性
- ✅ **快速生成** - LCM 加速，2-5 秒生成一张高质量素材
- ✅ **多类型素材** - 角色、背景、瓦片地图、UI 图标等
- ✅ **风格控制** - 像素风、卡通风、手绘风等多种预设
- ✅ **自动抠图** - 一键移除背景，生成透明素材
- ✅ **快速/高级模式** - 新手友好的快速模式和强大的高级模式
- ✅ **种子锁定** - 锁定满意的种子快速复现风格
- ✅ **引擎集成指南** - 游戏引擎 (Unity/Godot) 导入参数建议
- ✅ **易用界面** - Gradio 网页界面，无需命令行
- ✅ **本地离线** - 完全本地化部署，无云服务依赖

---

## ⚠️ 当前 MVP 限制 (v0.2)

### 已实现功能
- ✅ 快速/高级模式切换
- ✅ 5 种素材类型、4 种美术风格
- ✅ 自动背景移除
- ✅ **种子锁定** - 快速复现风格 (新增)
- ✅ 参数调优和反向提示词
- ✅ 动态提示词建议 (新增)
- ✅ 引擎集成指南 (新增)
- ✅ 元数据导出 (新增)

### 暂不支持 (计划于后续版本实现)

| 功能 | 限制说明 | 计划版本 |
|------|---------|---------|
| **参考图上传** | 暂不支持 IP-Adapter 角色锁定 | v0.3 |
| **批量生成** | 暂不支持批量生成和任务队列 | v0.3 |
| **完整历史画廊** | 当前只保留最新一张结果 | v0.3 |
| **Spritesheet 拼合** | 暂不支持多帧自动拼合 | v0.4 |
| **高级抠图** | 复杂背景可能需要后期编辑 | v0.4 |
| **自动微调** | 暂不支持 LoRA 模型微调 | v1.0 |

---

## 🚀 快速开始

### 系统要求

- **操作系统**: Windows 10+, Linux (Ubuntu 20.04+), macOS 12+
- **Python**: 3.9 - 3.11
- **GPU**: NVIDIA GPU 推荐 (8GB+ VRAM)，也支持 CPU (较慢)
- **磁盘空间**: 至少 20GB (用于模型)

### 安装步骤

#### 1️⃣ 克隆或下载项目
```bash
cd d:\111\2d
```

#### 2️⃣ 运行启动脚本（自动配置）

**Windows:**
```bash
run.bat
# 选择 "3" 同时启动后端和前端
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
# 选择 "3" 同时启动后端和前端
```

#### 3️⃣ 打开浏览器

后端 API: http://127.0.0.1:8000  
**前端界面: http://127.0.0.1:7860** ← 主要使用这个

---

## 📖 使用指南

### 基本流程（快速模式）

1. **选择素材类型** - 角色立绘、背景、瓦片等
2. **选择风格** - 像素风、卡通风等
3. **输入提示词** - 用英文/中文描述素材
4. **点击"生成素材"** - 等待生成 (2-8 秒)
5. **(可选) 锁定种子** - 点击「🔒 锁定此种子」保存满意风格
6. **下载结果** - 点击「📥 下载 PNG」获取透明背景文件

### 素材类型说明

| 类型 | 尺寸 | 用途 | 示例提示词 |
|------|------|------|----------|
| **角色立绘** | 512x512 | 单个角色的高分辨率立绘 | "a knight warrior, red armor, sword, standing pose, high quality" |
| **角色精灵** | 128x128 | 游戏中的可动画精灵 | "cute mage girl, purple robe, standing pose, white background" |
| **场景背景** | 1024x768 | 游戏关卡背景 | "fantasy tavern interior, wooden furniture, warm lighting, detailed" |
| **瓦片地图** | 256x256 | 可无缝拼接的地形纹理 | "grass ground tile, seamless pattern, tileable" |
| **UI 图标** | 256x256 | 游戏菜单和图标 | "sword weapon icon, simple design, centered" |

### 提示词技巧

#### ✅ 好的提示词示例
```
"a warrior elf princess, long blonde hair, elegant green dress, 
standing pose, high quality game character, detailed armor, fantasy style"

"grass ground tile, seamless pattern, tileable texture, bright colors"

"sword weapon icon, simple design, centered, pixel art style"
```

#### ❌ 不好的提示词
```
"beautiful girl"           // 太模糊，缺乏指向性
"a character"              // 太抽象，无法明确指导生成
"character with many arms" // 超出能力范围，容易变形
```

#### 🎯 关键提示词
- **姿态**: `standing pose`, `walking`, `sitting`, `T-pose`, `action pose`
- **背景**: `white background`, `transparent background`, `on ground`
- **质量**: `high quality`, `detailed`, `masterpiece`, `4K`
- **风格**: `pixel art`, `cartoon style`, `hand drawn`, `3D`
- **效果**: `full body`, `close-up`, `front view`, `side view`

### 快速模式 vs 高级模式

| 对比项 | 快速模式 | 高级模式 |
|--------|---------|---------|
| **参数** | 简化，仅需素材类型、风格、提示词 | 完整参数调控 |
| **推理步数** | 固定 8 步 (2-5 秒) | 可选 4-50 步 |
| **反向提示词** | 自动应用最佳默认值 | 自定义反向提示词 |
| **引导强度** | 7.5 (默认) | 1-20 可调 |
| **适合场景** | 快速原型、初步生成 | 质量微调、精细控制 |

### 保持风格一致的正确方式

#### 方法 1：种子锁定 ✨ (推荐)
```
1. 快速生成素材，满意后点击「🔒 锁定此种子」
2. 修改提示词 (如改变动作、属性等)
3. 保持其他参数不变，重新生成
4. ✅ 角色姿态和风格会保持一致
```

#### 方法 2：参考图上传 (v0.3+ 功能)
```
暂不支持，计划在 v0.3 版本实现 IP-Adapter 集成
预期功能: 上传参考图 → AI 学习风格 → 生成一致角色的其他姿态
```

#### 方法 3：提示词固定结构
```
保持相同的核心描述，仅修改动作部分:

固定部分: "a knight warrior, red armor, sword, high quality"
动作变化: 
  - "+ standing pose" → 待机姿态
  - "+ walking forward" → 行走动作
  - "+ sword attack" → 攻击动作
```

### 高级参数说明

| 参数 | 范围 | 说明 | 推荐值 |
|------|------|------|--------|
| **推理步数** | 4-50 | 步数越多质量越好，但耗时越长 | **快速**: 4-8 / **质量**: 15-30 / **完美**: 30+ |
| **引导强度** | 1-20 | 控制与提示词的贴切度 | **平衡**: 7.5 / **风格类**: 5-10 / **强约束**: 10-15 |
| **随机种子** | -1 或整数 | `-1` 为完全随机；输入整数重现结果 | 空或 -1 (首次) / 锁定后自动填入 |
| **自动抠图** | ON/OFF | 移除背景生成透明素材 | **ON** (推荐) |
| **反向提示词** | 文本 | 列举要避免的特征 | `low quality, blurry, deformed, ugly, watermark, text` |

---

## 🎮 游戏引擎集成指南

### Unity 导入设置示例

#### 角色精灵 (Character Sprite 128x128)
```yaml
Filter Mode: Point (No Filter)
Wrap Mode: Clamp
Pixels Per Unit: 16 (或 32，取决于分辨率)
Sprite Mode: Single
Generate Mip Maps: ✗ OFF
```

#### 背景图 (Background 1024x768)
```yaml
Filter Mode: Bilinear
Wrap Mode: Clamp
Pixels Per Unit: 100
Generate Mip Maps: ✓ ON
Compression: High Quality
```

### Godot 导入设置示例

#### 角色精灵
```yaml
Filter: Nearest
Mipmaps: ✗ OFF
Repeat: Disabled
Sprite Mode: 2D
Animation FPS: 12
```

#### 背景图
```yaml
Filter: Linear
Mipmaps: ✓ ON
Repeat: Disabled
```

---

## 💾 下载和导出

### 下载 PNG (推荐)
- 生成后点击「📥 下载 PNG」按钮
- ✅ 自动保留透明通道 (如已启用抠图)
- 文件位置: 浏览器默认下载目录

### 导出元数据 (高级模式)
- 包含生成参数、时间戳、图像信息
- JSON 格式便于后续处理
- 用于记录生成配置和版本管理

### 生成历史 (计划功能)
- 当前版本: 输出文件存储于 `output/` 目录
- v0.3+: 将实现完整的历史画廊和管理界面

---

## 🏗️ 项目结构

```
d:\111\2d\
├── backend/                    # FastAPI 后端
│   ├── main.py                # 主应用
│   ├── generators/
│   │   ├── sd_generator.py    # SD + LCM 生成器
│   │   └── background_remover.py  # 背景移除
│   ├── models/
│   │   └── schemas.py         # 数据模型
│   └── utils/
│
├── frontend/
│   └── app.py                 # Gradio 前端 (v0.2)
│
├── output/                    # 生成结果目录
├── config.py                  # 全局配置
├── requirements.txt           # Python 依赖
├── run.bat                    # Windows 启动脚本
├── run.sh                     # Linux/Mac 启动脚本
└── README.md                  # 本文件
```

---

## 🔧 后端 API 文档

### FastAPI 自动文档

访问 http://127.0.0.1:8000/docs (Swagger UI)

### 主要端点

#### POST /generate - 生成素材
```bash
curl -X POST "http://127.0.0.1:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a knight warrior, red armor",
    "asset_type": "character_portrait",
    "style": "pixel_art",
    "width": 512,
    "height": 512,
    "guidance_scale": 7.5,
    "num_inference_steps": 8,
    "remove_background": true
  }'
```

#### GET /health - 健康检查
```bash
curl "http://127.0.0.1:8000/health"
```

#### GET /image/{task_id} - 下载图像
```bash
curl "http://127.0.0.1:8000/image/{task_id}" -o image.png
```

---

## ⚙️ 配置调整

编辑 `config.py` 来自定义：

### 生成参数
```python
GENERATION_PRESETS = {
    "character_portrait": {
        "width": 512,
        "height": 512,
        "guidance_scale": 7.5,
        "num_inference_steps": 8,
    },
    # ...
}
```

### 模型配置
```python
MODEL_CONFIG = {
    "base_model": "runwayml/stable-diffusion-v1-5",
    "lcm_lora": "latent-consistency/lcm-lora-sdv1-5",
    "device": "cuda",  # 或 "cpu"
    "dtype": "float16",  # 或 "float32"
}
```

### API 配置
```python
API_CONFIG = {
    "host": "127.0.0.1",
    "port": 8000,
}
```

---

## 🐛 故障排查

### 问题 1: "无法连接到后端服务"
**解决**:
1. 确保后端已启动
   ```bash
   # Windows
   python backend/main.py
   
   # Linux/Mac
   python3 backend/main.py
   ```
2. 检查后端是否在 http://127.0.0.1:8000
3. 查看后端输出日志中的错误信息

### 问题 2: "CUDA 内存不足" (显卡报错)
**解决**: 
- 降低推理步数: 从 8 改为 4-6
- 降低图像尺寸: 修改 `config.py`
- 关闭其他占用 VRAM 的程序

### 问题 3: "模型下载很慢"
**解决**: 使用国内镜像或离线模型
```python
# config.py
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
```

### 问题 4: "生成的图像质量差"
**解决**: 
- ✅ 增加推理步数: 从 8 改为 15-30
- ✅ 增加引导强度: 从 7.5 改为 8-10
- ✅ 改进提示词: 增加关键词如 "high quality", "detailed"
- ✅ 尝试其他风格组合

### 问题 5: "前端无法加载"
**解决**:
1. 检查前端是否启动: `http://127.0.0.1:7860`
2. 查看浏览器控制台错误 (F12 → Console)
3. 重启前端: `python frontend/app.py`

---

## 📊 性能指标

使用 NVIDIA RTX 3090 GPU 的基准测试：

| 配置 | 生成时间 | 显存占用 | 质量 | 使用场景 |
|------|---------|---------|------|---------|
| LCM 4 步 | 2-3 秒 | 4GB | ⭐⭐⭐ | 快速原型 |
| LCM 8 步 | 4-6 秒 | 5GB | ⭐⭐⭐⭐ | **推荐 (平衡)** |
| 常规 30 步 | 20-30 秒 | 6GB | ⭐⭐⭐⭐⭐ | 最终成品 |

**CPU 运行** (Intel i7-10700K):
- 预计比 GPU 慢 10-20 倍 (4 步约 30-60 秒)

---

## 🔮 后续开发路线

### Phase 2: v0.3 - 风格一致化 (4-6 周)
- [ ] IP-Adapter 参考图上传
- [ ] 完整的生成历史画廊
- [ ] 批量生成和任务队列
- [ ] 预训练风格 LoRA

### Phase 3: v0.4 - 游戏引擎深度集成 (6-8 周)
- [ ] Unity 编辑器插件
- [ ] Godot 编辑器插件
- [ ] 自动 Spritesheet 切割
- [ ] 高级抠图算法 (SAM)

### Phase 4: v1.0+ - 生产化 (8+ 周)
- [ ] Electron 桌面应用
- [ ] 模型管理和微调
- [ ] 多人协作支持
- [ ] 素材版本控制

---

## 📚 学习资源

### Stable Diffusion & LCM
- [Hugging Face Diffusers](https://huggingface.co/docs/diffusers)
- [LCM LoRA Hub](https://huggingface.co/latent-consistency)
- [LCM 论文](https://arxiv.org/abs/2310.04378)

### 游戏开发
- [Unity Sprite 导入](https://docs.unity3d.com/Manual/Sprites.html)
- [Godot 2D 资源](https://docs.godotengine.org/en/stable/getting_started/introduction/first_2d_game/index.html)
- [LoRA 训练指南](https://github.com/kohya-ss/sd-scripts)

### 游戏素材设计
- [OpenGameArt.org](https://opengameart.org/) - 游戏素材库
- [Itch.io](https://itch.io/game-assets) - 游戏资源市场

---

## 📝 常见问题 (FAQ)

**Q: 能在 CPU 上运行吗？**  
A: 可以，但速度会慢 10-20 倍。在 `config.py` 改 `device = "cpu"`

**Q: 能离线使用吗？**  
A: 首次运行需要下载模型 (5-10GB)，之后完全离线运行

**Q: 生成的素材能用于商业用途吗？**  
A: 检查 Stable Diffusion 模型的许可证 (通常允许商业使用)。建议查阅当地法律。

**Q: 怎样保证风格一致性？**  
A: 使用种子锁定功能（点击「🔒 锁定此种子」），保持相同种子和提示词结构。v0.3+ 将支持参考图上传。

**Q: 支持 GPU 加速吗？**  
A: 支持 NVIDIA GPU (CUDA)。AMD 和 Intel GPU 支持计划在后续版本添加。

**Q: 生成的图像太小/太大怎么办？**  
A: 在高级模式中选择合适的素材类型 (已预设尺寸)，或编辑 `config.py` 修改预设参数。

**Q: 如何分享我的生成结果？**  
A: 点击「📥 下载 PNG」保存，或「📋 导出元数据」保存生成参数便于分享和复现。

---

## 🤝 反馈与支持

- **Bug 报告**: 请附上错误日志和复现步骤
- **功能建议**: 欢迎在 Issue 中描述需求
- **API 文档**: http://127.0.0.1:8000/docs
- **生成文件**: 浏览 `/file/output` 查看生成的素材

---

## 📄 许可证

本项目采用 MIT License。生成的素材请遵守 Stable Diffusion 模型许可证。

**版本**: MVP v0.2  
**模型**: SD 1.5 + LCM LoRA  
**框架**: FastAPI + Gradio 4.0+  
**更新时间**: 2026-05-24  
A: 使用相同的 `seed` 值，或等待 Phase 2 的 LoRA 和 IP-Adapter

**Q: 支持实时预览吗？**  
A: 现在不支持，但可以快速迭代 (每 2-5 秒一张)

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境
```bash
pip install -e ".[dev]"
black . && flake8 . && pytest
```

---

## 📄 许可证

MIT License - 自由使用和修改

---

## 👨‍💻 开发团队

**项目**: 2D 游戏素材生成工具  
**版本**: 0.1.0 MVP  
**最后更新**: 2024

---

## 📧 联系方式

如有问题或建议，欢迎联系我们！

---

**祝你使用愉快！🎉**
