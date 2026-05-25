# 🎮 2D游戏素材生成工具 - Google Colab 部署指南

## 完整启动流程 (复制粘贴即可)

### 📦 步骤1: 清理并克隆项目

```python
import os

# 重置工作目录
os.chdir('/content')

# 清理旧版本
!rm -rf 2d-game-assets-generator

# 克隆项目
!git clone https://github.com/lsthaha/2d-game-assets-generator.git

# 进入项目目录
os.chdir('/content/2d-game-assets-generator')

# 确认文件存在
!pwd
!ls -lh run_backend.py

print("\n✅ 项目克隆完成")
```

### 📚 步骤2: 安装依赖

```python
# 升级pip
!pip install --upgrade pip -q

# 安装核心依赖
!pip install diffusers==0.24.0 transformers accelerate safetensors -q

# 安装后端依赖
!pip install fastapi uvicorn python-multipart pillow -q

# 安装前端依赖
!pip install gradio -q

# 安装七牛云SDK
!pip install qiniu -q

print("\n✅ 依赖安装完成")
```

### ⚙️ 步骤3: 检查GPU

```python
import torch

if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    print(f"✅ GPU已启用: {gpu_name}")
    print(f"   显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
else:
    print("⚠️  未检测到GPU，将使用CPU（速度较慢）")
    print("   建议: 运行时 → 更改运行时类型 → 选择GPU")
```

### 🚀 步骤4: 启动后端

```python
import subprocess
import os

# 确保在正确目录
os.chdir('/content/2d-game-assets-generator')

# 启动后端（后台运行）
process = subprocess.Popen(
    ['python3', '-u', 'run_backend.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

print("🚀 后端正在启动...")
print("📝 首次运行会下载模型 (约5GB, 需要5-10分钟)\n")
print("=" * 60)

# 显示启动日志（前50行）
import time
for i in range(50):
    line = process.stdout.readline()
    if line:
        print(line.strip())
        # 检测启动成功
        if "Uvicorn running" in line or "startup complete" in line:
            print("\n" + "=" * 60)
            print("✅ 后端启动成功!")
            print("=" * 60)
            break
    time.sleep(0.5)

print("\n⏳ 等待后端完全就绪...")
time.sleep(10)
```

### 🔍 步骤5: 健康检查

```python
import requests
import time

print("🔍 检查后端状态...\n")

for i in range(10):
    try:
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 后端服务正常!")
            print(f"📊 状态: {response.json()}")
            print(f"\n🎉 后端API地址: http://127.0.0.1:8001")
            print(f"📚 API文档: http://127.0.0.1:8001/docs")
            break
    except Exception as e:
        if i < 9:
            print(f"⏳ 等待中... 尝试 {i+1}/10")
            time.sleep(3)
        else:
            print(f"\n❌ 后端未能启动")
            print(f"错误: {e}")
            print("\n💡 可能原因:")
            print("1. 模型下载时间较长，需要继续等待")
            print("2. GPU显存不足")
            print("3. 查看进程状态: !ps aux | grep python")
```

### 🎨 步骤6: 启动前端

```python
# 启动前端（会自动提供公开链接）
!python3 frontend/app.py
```

---

## 🧪 测试功能

### 测试1: 快速生成测试

```python
import requests
from PIL import Image
import io
from IPython.display import display

print("🎨 测试素材生成...\n")

response = requests.post(
    "http://127.0.0.1:8001/generate",
    json={
        "prompt": "a red knight warrior, pixel art style",
        "asset_type": "character_portrait",
        "style": "pixel_art",
        "width": 256,
        "height": 256,
        "num_inference_steps": 4,
        "guidance_scale": 7.5,
        "seed": 42
    },
    timeout=120
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ 生成成功!")
    print(f"任务ID: {result['task_id']}")
    print(f"耗时: {result['generation_time']:.2f}秒")
    
    # 显示图片
    img_response = requests.get(f"http://127.0.0.1:8001{result['image_url']}")
    img = Image.open(io.BytesIO(img_response.content))
    display(img)
else:
    print(f"❌ 生成失败: {response.text}")
```

### 测试2: 风格缓存

```python
import requests
import time

print("🔍 测试风格缓存机制\n")
print("=" * 60)

test_params = {
    "prompt": "a cute cat, pixel art",
    "asset_type": "character_portrait",
    "style": "pixel_art",
    "width": 256,
    "height": 256,
    "num_inference_steps": 4,
    "seed": 42
}

# 第一次生成
print("📝 第一次生成 (创建缓存)...")
start = time.time()
r1 = requests.post("http://127.0.0.1:8001/generate", json=test_params, timeout=120)
time1 = time.time() - start

if r1.status_code == 200:
    result1 = r1.json()
    print(f"   ✅ 耗时: {time1:.2f}秒")
    print(f"   📊 缓存命中: {result1.get('cache_hit', False)}")

print("\n" + "-" * 60 + "\n")

# 第二次生成
print("📝 第二次生成 (应命中缓存)...")
start = time.time()
r2 = requests.post("http://127.0.0.1:8001/generate", json=test_params, timeout=120)
time2 = time.time() - start

if r2.status_code == 200:
    result2 = r2.json()
    print(f"   ✅ 耗时: {time2:.2f}秒")
    print(f"   📊 缓存命中: {result2.get('cache_hit', False)}")
    
    if result2.get('cache_hit'):
        speedup = time1 / time2
        print(f"\n🚀 性能提升: {speedup:.2f}x")

print("\n" + "=" * 60)
```

---

## 🛠️ 故障排除

### 查看进程

```python
!ps aux | grep python | grep -E "run_backend|app.py"
```

### 重启后端

```python
# 停止旧进程
!pkill -f "run_backend.py"
!sleep 3

print("✅ 已停止，请重新运行步骤4")
```

### 查看日志

```python
# 如果使用了日志文件
!tail -n 100 /content/2d-game-assets-generator/backend.log
```

---

## 📖 性能参考

### GPU (T4)
- 快速模式 (4步): 2-3秒/张 ⚡
- 标准模式 (8步): 4-5秒/张
- 高质量 (20步): 8-10秒/张

### CPU
- 快速模式: 2-4分钟/张 🐢

---

## 💡 使用建议

1. **首次启动**: 耐心等待模型下载（5-10分钟）
2. **保持连接**: Colab 闲置90分钟会断开
3. **保存作品**: 定期下载生成的素材
4. **风格一致**: 使用相同的seed和style参数

---

## 🌐 七牛云集成（可选）

如需启用七牛云功能:

```python
import os

os.environ['QINIU_ACCESS_KEY'] = 'your_access_key'
os.environ['QINIU_SECRET_KEY'] = 'your_secret_key'
os.environ['QINIU_BUCKET'] = 'your_bucket'
os.environ['QINIU_CDN_DOMAIN'] = 'your_cdn_domain'
os.environ['STYLE_CACHE_ENABLED'] = 'true'

# 重启后端以应用配置
```
