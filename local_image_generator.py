#!/usr/bin/env python3
"""
本地图片生成器模块 - 强制使用GPU加速
"""

import pygame
import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# 全局变量用于缓存模型
_global_pipe = None
_model_loaded = False

def generate_image_local(prompt, width=512, height=512, steps=8, use_fast_mode=True):
    """
    使用本地Stable Diffusion生成图片（强制GPU加速）
    
    Args:
        prompt (str): 图片描述
        width (int): 图片宽度
        height (int): 图片高度
        steps (int): 生成步数（默认8步，快速生成）
        use_fast_mode (bool): 是否使用快速模式
    
    Returns:
        pygame.Surface: 生成的图片
    """
    global _global_pipe, _model_loaded
    
    try:
        print(f"🎨 使用本地Stable Diffusion生成图片: {prompt}")
        print(f"  尺寸: {width}x{height}")
        print(f"  步数: {steps}（快速生成）")
        
        # 强制使用GPU加速
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            import time
            
            # 检查GPU可用性
            if torch.backends.mps.is_available():
                device = "mps"
                print("🍎 使用Apple Silicon GPU加速")
            elif torch.cuda.is_available():
                device = "cuda"
                print("🚀 使用NVIDIA GPU加速")
            else:
                print("❌ 没有可用的GPU，使用备用方案")
                return generate_fallback_image(prompt, width, height)
            
            # 检查模型是否已加载
            if not _model_loaded or _global_pipe is None:
                print("🔄 加载本地Stable Diffusion模型...")
                
                # 使用Hugging Face模型，支持本地缓存
                model_id = "CompVis/stable-diffusion-v1-4"
                print(f"🔄 从Hugging Face加载模型: {model_id}")
                print("📥 首次使用会下载模型到本地缓存，后续使用会从缓存加载")
                
                _global_pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    use_safetensors=True,
                    low_cpu_mem_usage=True,
                    cache_dir="./models",  # 指定缓存目录
                    safety_checker=None  # 禁用安全过滤器
                )
                
                # 强制移动到GPU
                _global_pipe = _global_pipe.to(device)
                print(f"✅ 模型加载成功，已移动到{device}")
                
                _model_loaded = True
                print("✅ 模型加载完成")
            else:
                print("🔄 使用已加载的模型...")
            
            print("🎯 开始生成图片...")
            
            # 记录开始时间
            start_time = time.time()
            
            # 使用高质量生成设置
            image = _global_pipe(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=12.0,  # 增加引导强度，提高与提示词的匹配度
                eta=0.0  # 减少随机性
            ).images[0]
            
            # 检查生成时间
            generation_time = time.time() - start_time
            print(f"✅ Stable Diffusion生成成功，耗时: {generation_time:.2f}秒")
            
            # 转换为pygame surface
            pygame_surface = pil_to_pygame(image)
            return pygame_surface
            
        except ImportError as e:
            print(f"⚠️ Stable Diffusion导入失败，使用备用方案: {e}")
            return generate_fallback_image(prompt, width, height)
        except Exception as e:
            print(f"⚠️ Stable Diffusion生成失败，使用备用方案: {e}")
            # 重置模型状态，下次重新加载
            _global_pipe = None
            _model_loaded = False
            return generate_fallback_image(prompt, width, height)
        
    except Exception as e:
        print(f"❌ 本地图片生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_fallback_image(prompt, width, height):
    """备用图片生成方案（当Stable Diffusion失败时使用）"""
    print("🔄 使用备用图片生成方案...")
    
    # 创建PIL图片
    pil_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pil_image)
    
    # 根据提示词生成不同的颜色和图案
    colors = generate_colors_from_prompt(prompt)
    
    # 绘制背景
    if 'background' in prompt.lower() or 'space' in prompt.lower():
        # 太空背景
        draw_space_background(draw, width, height, colors)
    elif 'plane' in prompt.lower() or 'jet' in prompt.lower():
        # 飞机相关
        draw_plane_background(draw, width, height, colors)
    else:
        # 默认背景
        draw_default_background(draw, width, height, colors)
    
    # 转换为pygame surface
    pygame_surface = pil_to_pygame(pil_image)
    
    print("✅ 备用方案生成成功")
    return pygame_surface

def generate_colors_from_prompt(prompt):
    """根据提示词生成颜色方案"""
    prompt_lower = prompt.lower()
    
    if 'blue' in prompt_lower:
        primary_color = (0, 100, 200)
    elif 'red' in prompt_lower:
        primary_color = (200, 50, 50)
    elif 'green' in prompt_lower:
        primary_color = (50, 200, 50)
    elif 'dark' in prompt_lower or 'black' in prompt_lower:
        primary_color = (30, 30, 30)
    else:
        primary_color = (100, 100, 200)
    
    # 生成互补色
    secondary_color = tuple(255 - c for c in primary_color)
    
    # 生成背景色
    if 'space' in prompt_lower or 'cosmic' in prompt_lower:
        background_color = (10, 10, 30)
    else:
        background_color = (240, 240, 250)
    
    return {
        'primary': primary_color,
        'secondary': secondary_color,
        'background': background_color
    }

def draw_space_background(draw, width, height, colors):
    """绘制太空背景"""
    # 填充背景
    draw.rectangle([0, 0, width, height], fill=colors['background'])
    
    # 绘制星星
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 3)
        brightness = random.randint(100, 255)
        color = (brightness, brightness, brightness)
        draw.ellipse([x, y, x + size, y + size], fill=color)
    
    # 绘制星云
    for _ in range(3):
        center_x = random.randint(0, width)
        center_y = random.randint(0, height)
        radius = random.randint(50, 150)
        alpha = random.randint(30, 100)
        
        # 创建渐变星云
        for r in range(radius, 0, -5):
            alpha_factor = int(alpha * (r / radius))
            color = (*colors['primary'], alpha_factor)
            draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], 
                        fill=color, outline=color)

def draw_plane_background(draw, width, height, colors):
    """绘制飞机相关背景"""
    # 填充背景
    draw.rectangle([0, 0, width, height], fill=colors['background'])
    
    # 绘制云朵
    for _ in range(5):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(20, 60)
        color = (200, 200, 200, 100)
        draw.ellipse([x, y, x + size, y + size], fill=color)
    
    # 绘制简单的飞机轮廓
    plane_x = width // 2
    plane_y = height // 2
    plane_size = 40
    
    # 飞机主体
    draw.rectangle([plane_x - plane_size//2, plane_y - plane_size//2, 
                   plane_x + plane_size//2, plane_y + plane_size//2], 
                  fill=colors['primary'])
    
    # 机翼
    wing_width = plane_size * 2
    wing_height = plane_size // 3
    draw.rectangle([plane_x - wing_width//2, plane_y - wing_height//2,
                   plane_x + wing_width//2, plane_y + wing_height//2],
                  fill=colors['secondary'])

def draw_default_background(draw, width, height, colors):
    """绘制默认背景"""
    # 填充背景
    draw.rectangle([0, 0, width, height], fill=colors['background'])
    
    # 绘制简单的几何图案
    for i in range(5):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(20, 80)
        
        if i % 2 == 0:
            draw.ellipse([x, y, x + size, y + size], fill=colors['primary'])
        else:
            draw.rectangle([x, y, x + size, y + size], fill=colors['secondary'])

def pil_to_pygame(pil_image):
    """将PIL图片转换为pygame surface"""
    # 转换为RGB模式（pygame不支持RGBA）
    if pil_image.mode == 'RGBA':
        # 创建白色背景
        background = Image.new('RGB', pil_image.size, (255, 255, 255))
        background.paste(pil_image, mask=pil_image.split()[-1])  # 使用alpha通道作为mask
        pil_image = background
    elif pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # 转换为pygame surface
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    
    pygame_surface = pygame.image.fromstring(data, size, mode)
    return pygame_surface

def get_generator():
    """获取生成器信息"""
    return {
        'name': 'Local Stable Diffusion Generator (GPU Accelerated)',
        'type': 'local_stable_diffusion',
        'capabilities': ['stable_diffusion', 'fallback_generation', 'gpu_acceleration']
    }

# 测试函数
if __name__ == "__main__":
    print("🧪 测试本地图片生成器（GPU加速）...")
    
    # 初始化pygame（用于测试）
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # 测试生成
    test_prompts = [
        "blue fighter jet",
        "space background with stars",
        "dark military aircraft"
    ]
    
    for prompt in test_prompts:
        print(f"\n测试提示词: {prompt}")
        image = generate_image_local(prompt, 256, 256)
        if image:
            print(f"✅ 生成成功，尺寸: {image.get_size()}")
        else:
            print(f"❌ 生成失败")
    
    pygame.quit()
    print("\n测试完成！")
