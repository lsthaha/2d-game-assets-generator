# PR3: 前端基础实现 - Gradio

## PR 信息

**标题**: feat: 前端基础实现 (Gradio)

**目标分支**: main  
**源分支**: feature/frontend-basic

---

## 功能描述

本 PR 实现了完整的 Gradio 前端界面，提供用户友好的素材生成工具。前端通过 REST API 与后端通信，支持所有素材类型、风格和参数配置。

### 主要功能
1. **素材类型与风格选择**
   - 5 种素材类型：角色立绘、精灵图、背景、瓦片、UI 图标
   - 4 种美术风格：像素风、卡通风、手绘风、扁平设计

2. **提示词输入与示例**
   - 自由文本输入
   - 根据素材类型动态更新示例提示词
   - 一键使用示例

3. **参数配置**
   - 推理步数滑块 (4-50)
   - 引导强度 (1-20)
   - 随机种子 (-1 为随机，或指定固定值)
   - 反向提示词
   - 自动抠图开关

4. **生成与结果展示**
   - 实时生成结果预览
   - 生成信息显示（包括风格、提示词、时间等）
   - 下载 PNG 功能

5. **日志和调试**
   - 实时日志输出
   - 错误信息友好提示

---

## 实现思路

### 技术栈
- **框架**: Gradio 4.0+
- **后端通信**: requests 库
- **图像处理**: PIL

### 架构设计

```
前端 Gradio UI
    ↓
requests.post("/generate")
    ↓
后端 FastAPI 服务
    ↓
Stable Diffusion + LCM
    ↓
返回生成的图像路径
    ↓
前端显示结果和元数据
```

### 关键组件

1. **参数配置区**
   - gr.Radio: 素材类型和风格选择
   - gr.Slider: 推理步数和引导强度
   - gr.Number: 种子值
   - gr.Checkbox: 自动抠图
   - gr.Textbox: 提示词和反向提示词

2. **示例提示词动态更新**
   ```python
   asset_type.change(
       fn=update_examples_fn,
       inputs=asset_type,
       outputs=example_buttons
   )
   ```

3. **API 调用**
   ```python
   response = requests.post(
       f"{API_BASE_URL}/generate",
       json=request_data,
       timeout=120
   )
   ```

4. **结果展示**
   - gr.Image: 生成的图像
   - gr.Textbox: 生成信息
   - 下载链接

---

## UI 布局

```
┌─────────────────────────────────────────┐
│  2D 游戏素材 AI 生成工具                 │
├──────────────────┬──────────────────────┤
│  配置区           │  提示词输入区         │
│                  │                      │
│ ○ 素材类型       │ [   提示词   ]      │
│ ○ 风格           │ [   反向提示词   ]  │
│ ○ 推理步数       │ [示例1] [示例2]    │
│ ○ 引导强度       │                      │
│ ☑ 自动抠图       │ [  生成按钮  ]      │
│                  │                      │
├─────────────────────────────────────────┤
│  结果区                                  │
│  [生成的图像]  |  生成信息文本           │
├─────────────────────────────────────────┤
│ [下载PNG] [导出元数据] [清空]            │
└─────────────────────────────────────────┘
```

---

## API 集成

### 调用示例
```python
def generate_asset(
    prompt: str,
    asset_type: str,
    style: str,
    negative_prompt: str,
    num_inference_steps: int,
    guidance_scale: float,
    remove_background: bool,
    seed: Optional[int],
) -> Tuple[Optional[Image.Image], str]:
    
    response = requests.post(
        f"{API_BASE_URL}/generate",
        json={
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "asset_type": asset_type,
            "style": style,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "remove_background": remove_background,
            "seed": seed,
        },
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        image = Image.open(result["image_paths"][0])
        return image, "✓ 生成成功"
    else:
        return None, f"❌ 生成失败: {response.text}"
```

### 错误处理
- 后端连接失败：显示连接错误提示
- API 返回错误：显示具体错误信息
- 生成超时：120 秒超时保护

---

## 测试方式

### 前置条件
```bash
# 确保后端已启动
python backend/main.py

# 在另一个终端启动前端
python frontend/app.py
```

### 1. 访问前端
- 打开浏览器访问 http://127.0.0.1:7860
- 验证 UI 加载正常

### 2. 测试基本生成流程
```
1. 选择素材类型: "角色立绘"
2. 选择风格: "像素风格"
3. 输入提示词: "a knight warrior, red armor"
4. 点击"生成素材"
5. 等待 5-10 秒
6. 验证: 图像显示、生成信息显示、下载可用
```

### 3. 测试参数调整
```
- 推理步数: 4 → 8 → 15 (验证质量变化和耗时变化)
- 引导强度: 5 → 7.5 → 10 (验证风格贴切度变化)
- 种子值: -1 (随机) → 固定值 (验证可重现性)
```

### 4. 测试示例提示词
```
1. 选择不同的素材类型 (精灵图、背景等)
2. 验证: 示例提示词随之更新
3. 点击示例 → 提示词自动填入
```

### 5. 测试错误处理
```
- 后端未启动: 应显示"无法连接到后端服务"
- 提示词为空: 应显示"请输入提示词"
- 后端返回错误: 应显示具体错误信息
```

### 6. 测试下载功能
```
- 生成图像后点击"下载PNG"
- 验证: 文件下载、格式为 PNG、透明通道保留
```

---

## 文件变更

### 新增/修改文件
- ✅ `frontend/app.py` - Gradio 前端主应用
- ✅ `frontend/__init__.py` - 包初始化（如需要）

### 关键特性
- 完整的参数配置 UI
- 动态示例提示词
- 实时结果预览
- 友好的错误提示
- 性能优化：合理的超时和异常处理

---

## 用户交互流程

```
用户打开前端
    ↓
选择素材类型和风格
    ↓
输入或选择提示词
    ↓
（可选）调整高级参数
    ↓
点击"生成素材"
    ↓
显示"正在生成..."
    ↓
后端推理 (2-15 秒)
    ↓
显示结果图像
    ↓
显示生成信息（风格、耗时等）
    ↓
用户可下载、修改参数重新生成
```

---

## 依赖说明

### 新增依赖
- `gradio>=4.0.0` - Web UI 框架
- `requests>=2.31.0` - HTTP 客户端
- `pillow>=10.0.0` - 图像处理

### 原创功能部分
- Gradio 前端架构设计
- 参数配置 UI 组件
- 动态示例提示词系统
- API 集成和错误处理

---

## 已知限制

1. **同步请求** - 当前采用同步 HTTP 请求，生成期间 UI 会阻塞
2. **单任务** - 不支持并发生成多张图像
3. **历史记录** - 当前版本不保存生成历史（v0.3 实现）

---

## 后续改进

- [ ] WebSocket 实时进度反馈
- [ ] 生成历史画廊
- [ ] 参考图上传
- [ ] 批量生成
- [ ] 参数预设保存

---

## 相关资源

- [Gradio 文档](https://www.gradio.app/)
- [Gradio 示例](https://github.com/gradio-app/gradio/tree/main/demo)

