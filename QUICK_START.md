# 🚀 快速启动指南 (Mac Intel)

## ⚠️ 重要提示

你的系统配置:
- **硬件**: Intel Mac + AMD Radeon Pro 5300M
- **限制**: AMD GPU不支持PyTorch,只能使用CPU模式
- **Python**: 3.14.5 (太新,PyTorch不支持)

## 🔧 解决方案

### 方案1: 使用Python 3.11 (推荐)

```bash
# 1. 安装Python 3.11
brew install python@3.11

# 2. 创建虚拟环境
cd /Users/mac/Desktop/2d
python3.11 -m venv venv311
source venv311/bin/activate

# 3. 安装依赖
pip install torch torchvision
pip install -r requirements.txt

# 4. 运行项目
# 后端
python backend/main.py

# 前端 (新终端)
python frontend/app.py
```

### 方案2: 使用Conda (推荐,更稳定)

```bash
# 1. 安装Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh

# 2. 创建环境
conda create -n game-assets python=3.11 -y
conda activate game-assets

# 3. 安装PyTorch (CPU版本)
conda install pytorch torchvision cpuonly -c pytorch

# 4. 安装其他依赖
cd /Users/mac/Desktop/2d
pip install -r requirements.txt

# 5. 运行
python backend/main.py
```

### 方案3: 使用Docker (最简单,推荐)

```bash
# 构建镜像
docker build -t game-assets .

# 运行
docker run -p 8001:8001 -p 7860:7860 game-assets
```

## ⚡ 性能说明

### Intel Mac CPU模式性能:
- **首次加载**: 1-2分钟 (下载模型)
- **单次生成**: 2-4分钟 (LCM加速后)
- **内存需求**: 8-16GB RAM

### 如果需要快速生成:
1. **使用云GPU**: Google Colab, Kaggle, AWS等
2. **降低分辨率**: 修改`config.py`中的尺寸
3. **减少步数**: 已设置为4步 (最快)

## 🎯 CPU优化配置 (已设置)

当前配置已优化为CPU模式:
- ✅ device: "cpu"
- ✅ dtype: "float32"
- ✅ num_inference_steps: 4 (最快)
- ✅ enable_attention_slicing: True

## 📝 临时运行方案 (不安装)

如果暂时无法配置环境,可以:

1. **使用在线Colab**: 
   - 上传代码到Google Colab
   - 使用免费GPU (T4)
   - 生成速度: 2-3秒

2. **使用Replicate API**:
   - 付费API服务
   - 无需本地环境

## ❓ 遇到问题?

### 问题1: Python版本太新
```bash
# 解决: 安装Python 3.11
brew install python@3.11
```

### 问题2: PyTorch安装失败
```bash
# 解决: 使用Conda安装
conda install pytorch torchvision cpuonly -c pytorch
```

### 问题3: 内存不足
```bash
# 解决: 降低分辨率
# 修改config.py中的width/height为256x256
```

---

**需要帮助? 请查看完整文档: README.md**
