# 🎮 Colab 内联启动方案 (最简单)

## 方案说明
不依赖任何启动脚本，直接在 Colab 单元格中设置路径并启动

---

## 📋 完整步骤

### 步骤1: 克隆项目并安装依赖

```python
import os

# 清理并克隆
os.chdir('/content')
!rm -rf 2d-game-assets-generator
!git clone https://github.com/lsthaha/2d-game-assets-generator.git

# 安装依赖
!pip install -q diffusers==0.24.0 transformers accelerate safetensors
!pip install -q fastapi uvicorn python-multipart pillow gradio qiniu

print("✅ 准备完成")
```

---

### 步骤2: 后台启动后端 (关键!)

```python
import sys
import os

# 设置项目路径
project_path = '/content/2d-game-assets-generator'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.chdir(project_path)

print(f"✓ 工作目录: {os.getcwd()}")
print(f"✓ Python 路径已设置")
print(f"✓ 后台启动服务...\n")

# 后台启动
import subprocess
backend_process = subprocess.Popen(
    [sys.executable, '-c', '''
import sys
sys.path.insert(0, "/content/2d-game-assets-generator")

from backend.main import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
'''],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# 显示启动日志
import time
for i in range(60):
    line = backend_process.stdout.readline()
    if line:
        print(line.strip())
        if "Uvicorn running" in line or "startup complete" in line:
            print("\n✅ 后端启动成功!")
            break
    time.sleep(0.5)

print("\n⏳ 等待服务就绪...")
time.sleep(15)
```

---

### 步骤3: 健康检查

```python
import requests

for i in range(10):
    try:
        r = requests.get("http://127.0.0.1:8001/health", timeout=5)
        if r.status_code == 200:
            print(f"✅ 后端正常: {r.json()}")
            print(f"🎉 API: http://127.0.0.1:8001")
            print(f"📚 文档: http://127.0.0.1:8001/docs")
            break
    except:
        if i < 9:
            print(f"⏳ 尝试 {i+1}/10...")
            import time
            time.sleep(3)
        else:
            print("❌ 连接失败，请检查日志")
```

---

### 步骤4: 测试生成

```python
import requests
from PIL import Image
import io
from IPython.display import display

response = requests.post(
    "http://127.0.0.1:8001/generate",
    json={
        "prompt": "a red knight, pixel art",
        "width": 256,
        "height": 256,
        "num_inference_steps": 4,
        "seed": 42
    },
    timeout=120
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ 生成成功! 耗时: {result['generation_time']:.2f}秒")
    img_url = result['image_paths'][0]
    img_data = requests.get(f"http://127.0.0.1:8001{img_url}").content
    display(Image.open(io.BytesIO(img_data)))
else:
    print(f"❌ 失败: {response.text}")
```

---

### 步骤5: 启动前端 (可选)

```python
!cd /content/2d-game-assets-generator && python3 frontend/app.py
```

---

## 🔧 替代方案: 使用 %%writefile 创建启动脚本

如果上面的方案还有问题，使用这个:

```python
%%writefile /content/start.py
import sys
sys.path.insert(0, '/content/2d-game-assets-generator')

from backend.main import app
import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)
```

然后启动:

```python
import subprocess
import time

proc = subprocess.Popen(
    ['python3', '/content/start.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

for i in range(60):
    line = proc.stdout.readline()
    if line:
        print(line.strip())
        if 'Uvicorn running' in line:
            print("✅ 启动成功!")
            break
    time.sleep(0.5)

time.sleep(10)
```

---

## 🎯 最简化方案 (如果一切都失败)

直接用命令行:

```bash
%%bash --bg
cd /content/2d-game-assets-generator
export PYTHONPATH=/content/2d-game-assets-generator:$PYTHONPATH
python3 -c "
import sys; 
sys.path.insert(0, '/content/2d-game-assets-generator'); 
from backend.main import app; 
import uvicorn; 
uvicorn.run(app, host='0.0.0.0', port=8001)
" 2>&1 | tee /tmp/backend.log
```

查看日志:

```python
!tail -f /tmp/backend.log
```
