"""
Gradio 前端应用 - 2D 游戏素材生成工具用户界面
MVP v0.2 - 改进版本，包含快速/高级模式、历史记录、种子锁定等功能
"""
import logging
from pathlib import Path
import requests
import json
from typing import Optional, Tuple, List, Dict, Any
import gradio as gr
from PIL import Image
import numpy as np
from datetime import datetime
import io

# 配置
API_BASE_URL = "http://127.0.0.1:8001"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

logger = logging.getLogger(__name__)

# 风格配置
STYLES = {
    "pixel_art": "像素风格 - 复古像素艺术风格，适合像素类游戏",
    "cartoon": "卡通风格 - 明亮欢快的卡通风格",
    "hand_drawn": "手绘风格 - 温暖的手工绘制风格",
    "flat": "扁平设计 - 现代扁平设计风格",
}

# 素材类型配置
ASSET_TYPES = {
    "character_portrait": "角色立绘 (512x512) - 生成单个角色的立绘或头像",
    "character_sprite": "角色精灵 (128x128) - 游戏角色的精灵图",
    "background": "场景背景 (1024x768) - 游戏场景或背景",
    "tileset": "瓦片地图 (256x256) - 无缝拼接的瓦片纹理",
    "ui_icon": "UI图标 (256x256) - 游戏UI元素或图标",
}

# 提示词提示配置
PROMPT_HINTS = {
    "character_portrait": "💡 建议加入: full body, standing pose, high quality, detailed",
    "character_sprite": "⚠️ 建议加入: white background, full body, T-pose, simple style (便于抠图)",
    "background": "💡 建议加入: scenery, landscape, detailed, atmospheric lighting",
    "tileset": "⚠️ 建议加入: seamless pattern, tileable, repeating texture",
    "ui_icon": "💡 建议加入: simple design, icon style, centered composition",
}

# 预设示例
PROMPT_EXAMPLES = {
    "character_portrait": [
        "a knight warrior, red armor, sword, standing pose",
        "a cute mage girl, purple robe, staff, smile",
        "a goblin archer, green skin, leather armor",
        "an elf princess, flowing blonde hair, crown",
    ],
    "background": [
        "fantasy tavern interior, wooden furniture, warm lighting",
        "dark forest with tall trees, misty atmosphere",
        "sunny beach with palm trees and ocean",
        "ancient temple ruins, stone structures",
    ],
    "tileset": [
        "grass ground tile, seamless pattern",
        "stone brick wall, tileable texture",
        "wooden floor planks, seamless tile",
        "sand desert ground, repeating pattern",
    ],
    "ui_icon": [
        "sword weapon icon, simple design",
        "potion bottle icon, red liquid",
        "treasure chest icon, golden",
        "heal cross icon, medical symbol",
    ],
}

# 引擎集成指南（动态生成）
ENGINE_GUIDES = {
    "character_portrait": {
        "Unity": "Filter Mode: Point; Pixels Per Unit: 100; Generate Mip Maps: OFF",
        "Godot": "Filter: Nearest; Mipmaps: OFF; Repeat: Disabled",
        "PixelArt": "Nearest neighbor; No compression"
    },
    "character_sprite": {
        "Unity": "Filter Mode: Point; Pixels Per Unit: 16-32; Sprite Mode: Single",
        "Godot": "Filter: Nearest; Sprite Mode: 2D; Animation FPS: 12",
        "PixelArt": "Nearest neighbor; Sprite sheet compatible"
    },
    "background": {
        "Unity": "Filter Mode: Bilinear; Compression: High quality",
        "Godot": "Filter: Linear; Mipmaps: ON",
        "PixelArt": "Can use bilinear; HD suitable"
    },
    "tileset": {
        "Unity": "Filter Mode: Point; Wrap Mode: Repeat; Pixels Per Unit: 16",
        "Godot": "Filter: Nearest; Repeat Enabled",
        "PixelArt": "Nearest neighbor; Tile size: 16x16 or 32x32"
    },
    "ui_icon": {
        "Unity": "Filter Mode: Bilinear; UI Sprite; Pixels Per Unit: 100",
        "Godot": "Filter: Linear; UI Mode",
        "PixelArt": "Either bilinear or nearest depending on style"
    },
}


def generate_asset(
    prompt: str,
    asset_type: str,
    style: str,
    negative_prompt: str = "low quality, blurry, deformed",
    num_inference_steps: int = 8,
    guidance_scale: float = 7.5,
    remove_background: bool = True,
    seed: Optional[int] = None,
) -> Tuple[Optional[Image.Image], str]:
    """
    调用后端 API 生成素材
    """
    try:
        if not prompt.strip():
            return None, "❌ 请输入提示词"
        
        # 准备请求数据
        request_data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "asset_type": asset_type,
            "style": style,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "remove_background": remove_background,
            "seed": seed,
        }
        
        # 根据素材类型设置尺寸
        if asset_type == "character_portrait":
            request_data.update({"width": 512, "height": 512})
        elif asset_type == "character_sprite":
            request_data.update({"width": 128, "height": 128})
        elif asset_type == "background":
            request_data.update({"width": 1024, "height": 768})
        elif asset_type == "tileset":
            request_data.update({"width": 256, "height": 256})
        elif asset_type == "ui_icon":
            request_data.update({"width": 256, "height": 256})
        
        logger.info(f"发送生成请求: {request_data}")
        
        # 调用后端 API
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=request_data,
            timeout=120
        )
        
        if response.status_code != 200:
            return None, f"❌ API 错误: {response.status_code} - {response.text}"
        
        result = response.json()
        
        # 获取生成的图像
        if result.get("image_paths"):
            image_path = result["image_paths"][0]
            try:
                image = Image.open(image_path)
                task_id = result.get("task_id", "unknown")
                used_seed = result.get("seed", seed)
                message = f"""✅ 生成成功！
━━━━━━━━━━━━━━━━━
📌 任务ID: {task_id}
🎨 风格: {STYLES.get(style, style)}
🔢 使用种子: {used_seed}
⏱️  时间: {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━
📝 提示词: {prompt}"""
                return image, message
            except Exception as e:
                return None, f"❌ 无法加载生成的图像: {e}"
        else:
            return None, "❌ 生成失败，未获得有效的输出路径"
    
    except requests.exceptions.ConnectionError:
        return None, """❌ 无法连接到后端服务
请确保后端已启动：
Windows: run.bat → 选择 1 或 3
Linux/Mac: ./run.sh → 选择 1 或 3"""
    except Exception as e:
        logger.error(f"生成失败: {e}")
        return None, f"❌ 生成失败: {str(e)}"


def get_prompt_hint(asset_type: str) -> str:
    """获取对应素材类型的提示词提示"""
    return PROMPT_HINTS.get(asset_type, "")


def format_engine_guide(asset_type: str, engine: str = "Unity") -> str:
    """格式化引擎集成指南"""
    guides = ENGINE_GUIDES.get(asset_type, {})
    if not guides:
        return "暂无指南"
    
    guide_text = f"### {engine} 导入设置\n"
    if engine in guides:
        guide_text += f"```\n{guides[engine]}\n```"
    
    return guide_text


def create_interface():
    """创建 Gradio 界面 - 改进版本"""
    
    with gr.Blocks(title="2D 游戏素材生成工具 v0.2") as demo:
        
        gr.Markdown("""
        # 🎮 2D 游戏素材 AI 生成工具 v0.2
        
        **高效、低成本、风格一致的游戏素材生成服务**  
        使用 AI 快速生成游戏所需的各类素材，支持自动背景移除和风格控制。
        
        ⚠️ **当前 MVP 限制** - 参见下方「功能说明」和「即将推出」
        """)
        
        # 创建全局状态：历史记录和锁定的种子
        history_state = gr.State([])
        locked_seed = gr.State(None)
        
        # 主要内容：快速/高级模式切换
        with gr.Tabs() as mode_tabs:
            # ========== 快速模式 ==========
            with gr.TabItem("🚀 快速生成", id="quick_mode"):
                gr.Markdown("""
                ## 快速模式
                只需选择基本参数，即可快速生成素材。系统使用最优默认参数。
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 配置")
                        asset_type_quick = gr.Radio(
                            choices=list(ASSET_TYPES.keys()),
                            value="character_portrait",
                            label="📦 素材类型",
                            info="选择要生成的素材类型"
                        )
                        
                        style_quick = gr.Radio(
                            choices=list(STYLES.keys()),
                            value="pixel_art",
                            label="🎨 风格",
                            info="选择生成的美术风格"
                        )
                        
                        # 动态提示词提示
                        prompt_hint_quick = gr.Markdown(
                            get_prompt_hint("character_portrait"),
                            label="提示"
                        )
                        
                        def update_hint_quick(asset_type_val):
                            return gr.update(value=get_prompt_hint(asset_type_val))
                        
                        asset_type_quick.change(
                            fn=update_hint_quick,
                            inputs=asset_type_quick,
                            outputs=prompt_hint_quick
                        )
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 提示词")
                        prompt_quick = gr.Textbox(
                            label="📝 生成提示词",
                            placeholder="描述你想生成的素材...",
                            lines=4,
                            info="用英文或中文描述素材内容、风格、细节等"
                        )
                        
                        # 示例按钮
                        def update_examples_quick(asset_type_val):
                            examples = PROMPT_EXAMPLES.get(asset_type_val, [])
                            return gr.update(choices=examples)
                        
                        example_buttons_quick = gr.Radio(
                            choices=PROMPT_EXAMPLES.get("character_portrait", []),
                            label="📚 示例提示词",
                            info="点击快速使用"
                        )
                        
                        asset_type_quick.change(
                            fn=update_examples_quick,
                            inputs=asset_type_quick,
                            outputs=example_buttons_quick
                        )
                        
                        def use_example_quick(selected_example):
                            return selected_example
                        
                        example_buttons_quick.change(
                            fn=use_example_quick,
                            inputs=example_buttons_quick,
                            outputs=prompt_quick
                        )
                        
                        remove_bg_quick = gr.Checkbox(
                            value=True,
                            label="✓ 自动抠图 (移除背景)",
                            info="生成透明背景的素材"
                        )
                        
                        generate_btn_quick = gr.Button(
                            "🚀 生成素材",
                            variant="primary",
                            size="lg"
                        )
                
                # 快速模式输出
                gr.Markdown("### 生成结果")
                with gr.Row():
                    output_image_quick = gr.Image(
                        label="生成的图像",
                        type="pil"
                    )
                    
                    output_info_quick = gr.Textbox(
                        label="生成信息",
                        lines=8,
                        interactive=False
                    )
                
                # 种子锁定和下载
                with gr.Row():
                    lock_seed_btn_quick = gr.Button(
                        "🔒 锁定此种子",
                        variant="secondary",
                        scale=1
                    )
                    download_png_quick = gr.Button(
                        "📥 下载 PNG",
                        variant="secondary",
                        scale=1
                    )
                    clear_btn_quick = gr.Button(
                        "🗑️ 清空",
                        scale=1
                    )
                
                # 快速模式绑定事件
                def generate_quick(prompt_val, asset_type_val, style_val, remove_bg_val, locked_seed_val):
                    if locked_seed_val is not None:
                        image, message = generate_asset(
                            prompt=prompt_val,
                            asset_type=asset_type_val,
                            style=style_val,
                            remove_background=remove_bg_val,
                            seed=locked_seed_val,
                        )
                    else:
                        image, message = generate_asset(
                            prompt=prompt_val,
                            asset_type=asset_type_val,
                            style=style_val,
                            remove_background=remove_bg_val,
                        )
                    return image, message
                
                generate_btn_quick.click(
                    fn=generate_quick,
                    inputs=[prompt_quick, asset_type_quick, style_quick, remove_bg_quick, locked_seed],
                    outputs=[output_image_quick, output_info_quick]
                )
                
                def lock_seed(info_text):
                    if "使用种子:" in info_text:
                        try:
                            seed_line = [line for line in info_text.split("\n") if "使用种子:" in line][0]
                            seed_value = int(seed_line.split(": ")[1])
                            return seed_value, f"✅ 已锁定种子: {seed_value}\n点击「生成素材」将复用此种子"
                        except:
                            return None, "❌ 无法提取种子值"
                    return None, "❌ 请先生成一张素材"
                
                lock_seed_btn_quick.click(
                    fn=lock_seed,
                    inputs=output_info_quick,
                    outputs=[locked_seed, output_info_quick]
                )
                
                def download_image(image):
                    if image is None:
                        return None
                    return image
                
                download_png_quick.click(
                    fn=download_image,
                    inputs=output_image_quick,
                    outputs=gr.File(label="下载", visible=True)
                )
                
                def clear_quick():
                    return None, "", None
                
                clear_btn_quick.click(
                    fn=clear_quick,
                    outputs=[output_image_quick, output_info_quick, locked_seed]
                )
            
            # ========== 高级模式 ==========
            with gr.TabItem("⚙️ 高级模式", id="advanced_mode"):
                gr.Markdown("""
                ## 高级模式
                完整参数控制，适合精细调优和实验。
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 基础配置")
                        asset_type_adv = gr.Radio(
                            choices=list(ASSET_TYPES.keys()),
                            value="character_portrait",
                            label="📦 素材类型",
                            info="选择要生成的素材类型"
                        )
                        
                        style_adv = gr.Radio(
                            choices=list(STYLES.keys()),
                            value="pixel_art",
                            label="🎨 风格",
                            info="选择生成的美术风格"
                        )
                        
                        prompt_hint_adv = gr.Markdown(
                            get_prompt_hint("character_portrait"),
                            label="提示"
                        )
                        
                        def update_hint_adv(asset_type_val):
                            return gr.update(value=get_prompt_hint(asset_type_val))
                        
                        asset_type_adv.change(
                            fn=update_hint_adv,
                            inputs=asset_type_adv,
                            outputs=prompt_hint_adv
                        )
                        
                        gr.Markdown("### 高级参数")
                        num_inference_steps_adv = gr.Slider(
                            minimum=4,
                            maximum=50,
                            value=8,
                            step=1,
                            label="推理步数",
                            info="4-8 (快速 2s), 15-30 (高质 5-10s)"
                        )
                        
                        guidance_scale_adv = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=7.5,
                            step=0.5,
                            label="引导强度",
                            info="7.5 (推荐), 5-10 (风格类)"
                        )
                        
                        seed_adv = gr.Number(
                            value=-1,
                            label="随机种子",
                            info="-1 (随机) 或输入数字"
                        )
                        
                        remove_bg_adv = gr.Checkbox(
                            value=True,
                            label="✓ 自动抠图",
                            info="生成透明背景的素材"
                        )
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 提示词")
                        prompt_adv = gr.Textbox(
                            label="📝 生成提示词",
                            placeholder="用英文或中文描述素材...",
                            lines=4,
                            info="支持复杂描述和风格指定"
                        )
                        
                        negative_prompt_adv = gr.Textbox(
                            value="low quality, blurry, deformed, ugly, watermark, text",
                            label="反向提示词",
                            placeholder="输入要避免生成的内容",
                            lines=3,
                            info="系统将避免生成这些特征"
                        )
                        
                        def update_examples_adv(asset_type_val):
                            examples = PROMPT_EXAMPLES.get(asset_type_val, [])
                            return gr.update(choices=examples)
                        
                        example_buttons_adv = gr.Radio(
                            choices=PROMPT_EXAMPLES.get("character_portrait", []),
                            label="📚 示例提示词",
                            info="点击快速使用"
                        )
                        
                        asset_type_adv.change(
                            fn=update_examples_adv,
                            inputs=asset_type_adv,
                            outputs=example_buttons_adv
                        )
                        
                        def use_example_adv(selected_example):
                            return selected_example
                        
                        example_buttons_adv.change(
                            fn=use_example_adv,
                            inputs=example_buttons_adv,
                            outputs=prompt_adv
                        )
                        
                        generate_btn_adv = gr.Button(
                            "🚀 生成素材",
                            variant="primary",
                            size="lg"
                        )
                
                # 高级模式输出
                gr.Markdown("### 生成结果")
                with gr.Row():
                    output_image_adv = gr.Image(
                        label="生成的图像",
                        type="pil"
                    )
                    
                    output_info_adv = gr.Textbox(
                        label="生成信息",
                        lines=8,
                        interactive=False
                    )
                
                # 高级模式控制按钮
                with gr.Row():
                    lock_seed_btn_adv = gr.Button(
                        "🔒 锁定此种子",
                        variant="secondary",
                        scale=1
                    )
                    download_png_adv = gr.Button(
                        "📥 下载 PNG",
                        variant="secondary",
                        scale=1
                    )
                    download_meta_adv = gr.Button(
                        "📋 导出元数据",
                        variant="secondary",
                        scale=1
                    )
                    clear_btn_adv = gr.Button(
                        "🗑️ 清空",
                        scale=1
                    )
                
                # 高级模式事件绑定
                def generate_adv(prompt_val, asset_type_val, style_val, negative_prompt_val, 
                                num_inference_steps_val, guidance_scale_val, remove_bg_val, seed_val):
                    seed_int = int(seed_val) if seed_val and seed_val > 0 else None
                    image, message = generate_asset(
                        prompt=prompt_val,
                        asset_type=asset_type_val,
                        style=style_val,
                        negative_prompt=negative_prompt_val,
                        num_inference_steps=int(num_inference_steps_val),
                        guidance_scale=float(guidance_scale_val),
                        remove_background=remove_bg_val,
                        seed=seed_int,
                    )
                    return image, message
                
                generate_btn_adv.click(
                    fn=generate_adv,
                    inputs=[
                        prompt_adv, asset_type_adv, style_adv, negative_prompt_adv,
                        num_inference_steps_adv, guidance_scale_adv, remove_bg_adv, seed_adv
                    ],
                    outputs=[output_image_adv, output_info_adv]
                )
                
                lock_seed_btn_adv.click(
                    fn=lock_seed,
                    inputs=output_info_adv,
                    outputs=[locked_seed, output_info_adv]
                )
                
                download_png_adv.click(
                    fn=download_image,
                    inputs=output_image_adv,
                    outputs=gr.File(label="下载 PNG", visible=True)
                )
                
                def export_metadata(image, info_text, asset_type_val):
                    if image is None or not info_text:
                        return None
                    
                    metadata = {
                        "timestamp": datetime.now().isoformat(),
                        "asset_type": asset_type_val,
                        "info": info_text,
                        "image_size": f"{image.width}x{image.height}"
                    }
                    
                    json_str = json.dumps(metadata, ensure_ascii=False, indent=2)
                    return gr.File(value=io.BytesIO(json_str.encode()), 
                                 label="元数据", visible=True)
                
                download_meta_adv.click(
                    fn=export_metadata,
                    inputs=[output_image_adv, output_info_adv, asset_type_adv],
                    outputs=gr.File(label="下载元数据", visible=True)
                )
                
                def clear_adv():
                    return None, ""
                
                clear_btn_adv.click(
                    fn=clear_adv,
                    outputs=[output_image_adv, output_info_adv]
                )
        
        # ========== 生成历史 ==========
        with gr.Tabs() as history_tabs:
            with gr.TabItem("📜 生成历史", id="history_tab"):
                gr.Markdown("""
                ## 生成历史和管理
                查看所有生成过的素材（当前版本暂时显示最近一张，完整历史画廊将在 v0.3 实现）
                """)
                
                with gr.Row():
                    history_gallery = gr.Gallery(
                        label="素材历史",
                        show_label=True,
                        elem_id="gallery",
                        columns=4,
                        rows=2,
                        height="auto"
                    )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 历史管理")
                        refresh_btn = gr.Button("🔄 刷新")
                        delete_history_btn = gr.Button("🗑️ 清空历史")
                        gr.Markdown("""
                        **📝 注意:**
                        - 历史记录存储在 `output/` 目录
                        - 完整的历史画廊将在 v0.3 版本实现
                        - 当前可通过导出功能保存元数据
                        """)
            
            with gr.TabItem("🎮 引擎集成指南", id="engine_guide_tab"):
                gr.Markdown("""
                ## 游戏引擎集成
                根据不同素材类型获取相应引擎的导入设置建议。
                """)
                
                with gr.Row():
                    guide_asset_type = gr.Radio(
                        choices=list(ASSET_TYPES.keys()),
                        value="character_sprite",
                        label="选择素材类型"
                    )
                    
                    guide_engine = gr.Radio(
                        choices=["Unity", "Godot"],
                        value="Unity",
                        label="选择游戏引擎"
                    )
                
                guide_output = gr.Markdown(
                    format_engine_guide("character_sprite", "Unity")
                )
                
                def update_guide(asset_type_val, engine_val):
                    return gr.update(value=format_engine_guide(asset_type_val, engine_val))
                
                guide_asset_type.change(
                    fn=update_guide,
                    inputs=[guide_asset_type, guide_engine],
                    outputs=guide_output
                )
                
                guide_engine.change(
                    fn=update_guide,
                    inputs=[guide_asset_type, guide_engine],
                    outputs=guide_output
                )
        
        # ========== 帮助和说明 ==========
        with gr.Accordion("💡 功能说明与限制", open=False):
            gr.Markdown("""
            ### ✅ 已实现功能
            - 快速/高级模式切换
            - 5 种素材类型生成
            - 4 种美术风格选择
            - 自动背景移除
            - 种子锁定（快速复现风格）
            - 参数调优和反向提示词
            - 动态提示词建议
            - 引擎集成指南
            - 元数据导出
            
            ### ⚠️ MVP v0.2 限制
            - **❌ 参考图上传** - 暂不支持 IP-Adapter（v0.3 实现）
            - **❌ 批量生成** - 暂不支持批量生成和队列（v0.3 实现）
            - **❌ 完整历史画廊** - 当前只保留最新结果（v0.3 实现）
            - **❌ Spritesheet 拼合** - 暂不支持多帧自动拼合（v0.4 实现）
            - **❌ 自动抠图优化** - 复杂背景可能需要后期编辑
            
            ### 🔜 即将推出 (v0.3+)
            - 📸 参考图上传与 IP-Adapter 集成
            - 📋 完整的生成历史画廊和管理
            - 🎬 批量生成和任务队列
            - 🎞️ Spritesheet 自动生成和拼合
            - 🎯 更精准的风格锁定系统
            - 🔧 高级抠图算法选择
            """)
        
        with gr.Accordion("📚 快速提示", open=False):
            gr.Markdown("""
            ### 生成效果好的提示词
            1. **具体描述** - 使用具体名词而不是抽象词，如"knight in red armor"而不是"warrior"
            2. **包含风格指示** - 如"pixel art style, low resolution"或"cartoon style, bright colors"
            3. **明确姿态** - 如"standing pose", "walking animation", "idle posture"
            4. **避免复杂背景** - 素材生成更适合单一背景
            5. **使用英文** - 虽然支持中文，但英文提示词效果通常更好
            
            ### 保持风格一致
            1. 生成满意的素材后，点击「🔒 锁定此种子」保存种子
            2. 修改提示词（如改变动作），保持其他参数不变
            3. 使用相同种子和风格重新生成 → 风格保持一致
            4. 确保勾选「自动抠图」获得透明背景
            
            ### 快速生成 vs 高质量
            - **快速**: 推理步数 4-8，生成时间 2-5 秒
            - **高质**: 推理步数 15-30，生成时间 5-15 秒
            - **平衡**: 推理步数 8-12，生成时间 3-8 秒
            """)
        
        gr.Markdown("""
        ---
        ### 📞 反馈和支持
        - 问题报告和功能建议请提交 Issue
        - [API 文档](http://127.0.0.1:8000/docs)
        - [生成输出文件](/file/output)
        
        **版本**: MVP v0.2 | **模型**: SD 1.5 + LCM LoRA | **框架**: Gradio 4.0+
        """)
    
    return demo


if __name__ == "__main__":
    logger.info("启动 Gradio 前端应用 v0.2...")
    
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        show_error=True,
    )
