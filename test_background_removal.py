#!/usr/bin/env python3
"""
测试背景去除和黑色阴影去除功能
"""

import os
import sys
import pygame
from background_remover import BackgroundRemover

def test_background_removal():
    """测试背景去除功能"""
    print("🧪 开始测试背景去除功能...")
    
    # 初始化背景去除器
    remover = BackgroundRemover()
    
    # 检查可用模型
    available_models = remover.get_available_models()
    print(f"📋 可用模型: {available_models}")
    
    if not available_models:
        print("❌ 没有可用的AI模型")
        return
    
    # 设置模型
    model_name = available_models[0]
    remover.set_model(model_name)
    print(f"🎯 使用模型: {model_name}")
    
    # 查找测试图片
    test_images = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                # 跳过已处理的图片
                if not file.startswith('processed_') and not file.startswith('removed_bg_'):
                    test_images.append(os.path.join(root, file))
    
    if not test_images:
        print("❌ 没有找到测试图片")
        return
    
    print(f"📁 找到 {len(test_images)} 张测试图片")
    
    # 选择第一张图片进行测试
    test_image = test_images[0]
    print(f"🖼️ 测试图片: {test_image}")
    
    # 创建输出目录
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 输出路径
    output_path = os.path.join(output_dir, f"removed_bg_{os.path.basename(test_image)}")
    
    try:
        # 执行背景去除
        print(f"🚀 开始去除背景...")
        result = remover.remove_background(test_image, output_path)
        
        if result:
            print(f"✅ 背景去除成功!")
            print(f"📁 输出文件: {output_path}")
            
            # 检查文件大小
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📊 文件大小: {file_size} bytes")
                
                # 显示结果
                show_result(test_image, output_path)
            else:
                print("❌ 输出文件不存在")
        else:
            print("❌ 背景去除失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def show_result(original_path, processed_path):
    """显示处理结果对比"""
    try:
        # 初始化Pygame
        pygame.init()
        
        # 加载图片
        original_img = pygame.image.load(original_path)
        processed_img = pygame.image.load(processed_path)
        
        # 获取图片尺寸
        orig_width, orig_height = original_img.get_size()
        proc_width, proc_height = processed_img.get_size()
        
        # 计算显示尺寸
        max_width = 800
        max_height = 600
        
        # 缩放图片以适应屏幕
        if orig_width > max_width or orig_height > max_height:
            scale = min(max_width / orig_width, max_height / orig_height)
            orig_width = int(orig_width * scale)
            orig_height = int(orig_height * scale)
            original_img = pygame.transform.scale(original_img, (orig_width, orig_height))
        
        if proc_width > max_width or proc_height > max_height:
            scale = min(max_width / proc_width, max_height / proc_height)
            proc_width = int(proc_width * scale)
            proc_height = int(proc_height * scale)
            processed_img = pygame.transform.scale(processed_img, (proc_width, proc_height))
        
        # 创建窗口
        window_width = max(orig_width, proc_width) + 50
        window_height = orig_height + proc_height + 100
        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("背景去除测试结果")
        
        # 颜色
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (100, 150, 255)
        
        # 主循环
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # 清屏
            screen.fill(WHITE)
            
            # 绘制标题
            font = pygame.font.Font(None, 36)
            title = font.render("背景去除测试结果", True, BLACK)
            title_rect = title.get_rect(center=(window_width // 2, 30))
            screen.blit(title, title_rect)
            
            # 绘制原图
            orig_x = (window_width - orig_width) // 2
            orig_y = 80
            screen.blit(original_img, (orig_x, orig_y))
            
            # 原图标签
            orig_label = font.render("原图", True, BLACK)
            orig_label_rect = orig_label.get_rect(center=(orig_x + orig_width // 2, orig_y + orig_height + 20))
            screen.blit(orig_label, orig_label_rect)
            
            # 绘制处理后图片
            proc_x = (window_width - proc_width) // 2
            proc_y = orig_y + orig_height + 50
            screen.blit(processed_img, (proc_x, proc_y))
            
            # 处理后图片标签
            proc_label = font.render("背景已去除", True, BLUE)
            proc_label_rect = proc_label.get_rect(center=(proc_x + proc_width // 2, proc_y + proc_height + 20))
            screen.blit(proc_label, proc_label_rect)
            
            # 提示信息
            hint_font = pygame.font.Font(None, 24)
            hint = hint_font.render("按ESC键退出", True, BLACK)
            hint_rect = hint.get_rect(center=(window_width // 2, window_height - 20))
            screen.blit(hint, hint_rect)
            
            # 更新显示
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        
    except Exception as e:
        print(f"❌ 显示结果失败: {e}")

if __name__ == "__main__":
    test_background_removal()
