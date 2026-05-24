# 🚀 快速开始指南 (Quick Start)

## 5 分钟快速上手

### Step 1: 检查环境

打开命令行/终端，验证 Python 已安装：

```bash
python --version
# 或 Mac/Linux:
python3 --version
```

需要 **Python 3.9 - 3.11** 和 **NVIDIA GPU** (可选，支持 CPU 但较慢)

### Step 2: 自动安装和启动

#### Windows 用户：
```bash
cd d:\111\2d
run.bat
# 选择 "3" 同时启动后端和前端
```

#### Linux / Mac 用户：
```bash
cd /path/to/2d
chmod +x run.sh
./run.sh
# 选择 "3" 同时启动后端和前端
```

**等待 2-3 分钟** (首次安装会下载模型)

### Step 3: 打开浏览器

**主要界面 (推荐)**: http://127.0.0.1:7860

你会看到一个友好的 Web 界面，包含：
- 素材类型选择
- 风格选择
- 提示词输入框
- 生成按钮

**API 文档** (高级): http://127.0.0.1:8000/docs

---

## 🎮 第一次生成

### 最简单的例子

1. **素材类型**: 角色立绘 (默认)
2. **风格**: 像素风格 (默认)
3. **提示词**: 复制粘贴以下内容
   ```
   a cute elf archer, green clothes, blonde hair, standing pose, 
   game character, high quality
   ```
4. **点击**: "🚀 生成素材"

**等待 4-8 秒**...✨ 完成！

### 保存图像

右击生成的图像 → "另存为" → 保存为 PNG

---

## 🎨 更多示例

### 例1：像素风格的骑士

```
素材类型: 角色立绘
风格: 像素风格
提示词: 
a knight warrior, red armor, golden sword, standing pose, 
pixel art style, 8-bit game character
```

### 例2：卡通风格背景

```
素材类型: 场景背景
风格: 卡通风格
提示词:
fantasy tavern interior, cozy atmosphere, wooden furniture,
warm lighting, cartoon style, video game background
```

### 例3：平铺瓦片

```
素材类型: 瓦片地图
风格: 像素风格
提示词:
grass ground tile, seamless pattern, 2d game tileset,
pixel art, repeating texture
```

---

## ⚙️ 性能调整

生成太慢？或质量不好？

### 快速模式 (2-3 秒)
```
推理步数: 4
引导强度: 7
```

### 平衡模式 (4-6 秒) ⭐ 推荐
```
推理步数: 8
引导强度: 7.5
```

### 高质量模式 (15-20 秒)
```
推理步数: 20
引导强度: 8
```

---

## 🆘 常见问题

### Q: 启动时卡在"正在初始化模型"

**A**: 首次运行会下载 5-10GB 的模型文件，需要 5-10 分钟。请耐心等待。

### Q: "CUDA 内存不足"

**A**: 降低图像尺寸：
- 在高级参数中改成 256x256 或 128x128
- 或改为 CPU 模式（虽然慢）

### Q: 生成的图像质量差

**A**: 尝试：
1. 增加推理步数 (8 → 15-20)
2. 改进提示词 (更具体的描述)
3. 尝试不同的风格
4. 点击"随机"重新生成 (使用不同种子)

### Q: 后端启动失败

**A**: 查看错误日志，常见原因：
- 缺少依赖: `pip install -r requirements.txt`
- PyTorch 版本问题: `pip install torch --index-url https://download.pytorch.org/whl/cu118`
- GPU 驱动过旧: 更新 NVIDIA 驱动

### Q: 能用生成的图片做什么？

**A**: 
- ✓ 游戏中使用 (商业项目，检查许可证)
- ✓ 修改和再创作
- ✓ 培训和学习
- 检查 Stable Diffusion 许可证了解完整规则

---

## 📚 学习更多

- **详细文档**: 看 [README.md](README.md)
- **API 文档**: http://127.0.0.1:8000/docs
- **配置调整**: 编辑 `config.py`
- **代码探索**: 看 `backend/` 和 `frontend/` 目录

---

## 🔥 进阶技巧

### 生成一致的角色

使用相同的**种子值**：

```
输入任何数字作为种子，如 42
生成一张角色图片
下次生成同一个角色描述 + 相同种子
结果会完全一样
```

### 批量生成

在 `config.py` 添加：

```python
# 运行脚本生成 10 张不同角色
prompts = [
    "knight warrior",
    "mage girl",
    "rogue assassin",
    # ...
]

for prompt in prompts:
    generate(prompt)
```

### 集成到游戏引擎

**Unity** (手动导入):
1. 生成图像
2. 拖到 Assets/ 文件夹
3. 设置 Sprite Mode = Multiple
4. 创建 Animation Clip

**Godot** (类似):
1. 生成图像
2. 放到 res://assets/sprites/
3. 创建 SpriteFrames 资源
4. 使用 AnimatedSprite2D 播放

---

## 🎯 下一步建议

1. **生成你的第一个素材** (现在试试！)
2. **调整参数** 找到你喜欢的风格
3. **阅读完整文档** [README.md](README.md)
4. **考虑 Phase 2 功能** (等待更新)：
   - 更好的风格控制
   - 角色形象锁定 (IP-Adapter)
   - 无缝纹理生成
   - 游戏引擎插件

---

## 📞 获得帮助

- 查看日志: 窗口中的 "日志信息" 区域
- 检查系统: 运行 `python test_setup.py`
- API 健康检查: http://127.0.0.1:8000/health

---

**开始创建吧！🎮✨**
