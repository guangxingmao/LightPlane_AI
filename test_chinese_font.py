#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文字体显示测试脚本
用于验证pygame中文字体是否正常工作
"""

import pygame
import sys
import os

# 初始化pygame
pygame.init()

# 设置窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('中文字体测试')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def test_system_fonts():
    """测试系统字体"""
    print("=== 测试系统字体 ===")
    
    # 测试1: 使用None字体（默认字体）
    try:
        font1 = pygame.font.SysFont(None, 36)
        text1 = font1.render("Hello World", True, BLACK)
        print("✓ SysFont(None, 36) 成功")
    except Exception as e:
        print(f"✗ SysFont(None, 36) 失败: {e}")
    
    # 测试2: 使用Arial字体
    try:
        font2 = pygame.font.SysFont("arial", 36)
        text2 = font2.render("Hello World", True, BLACK)
        print("✓ SysFont('arial', 36) 成功")
    except Exception as e:
        print(f"✗ SysFont('arial', 36) 失败: {e}")
    
    # 测试3: 尝试渲染中文
    try:
        font3 = pygame.font.SysFont("arial", 36)
        text3 = font3.render("你好世界", True, BLACK)
        print("✓ Arial字体渲染中文成功")
    except Exception as e:
        print(f"✗ Arial字体渲染中文失败: {e}")

def test_chinese_fonts():
    """测试中文字体"""
    print("\n=== 测试中文字体 ===")
    
    # macOS 系统字体
    mac_fonts = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
    ]
    
    # Windows 系统字体
    windows_fonts = [
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
    ]
    
    # Linux 系统字体
    linux_fonts = [
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    
    all_fonts = mac_fonts + windows_fonts + linux_fonts
    
    working_fonts = []
    
    for font_path in all_fonts:
        if os.path.exists(font_path):
            try:
                font = pygame.font.Font(font_path, 36)
                # 测试渲染中文
                text = font.render("你好世界", True, BLACK)
                working_fonts.append(font_path)
                print(f"✓ 中文字体可用: {font_path}")
            except Exception as e:
                print(f"✗ 中文字体不可用: {font_path} - {e}")
        else:
            print(f"- 字体文件不存在: {font_path}")
    
    return working_fonts

def main():
    """主函数"""
    print("pygame中文字体测试")
    print("=" * 50)
    
    # 测试系统字体
    test_system_fonts()
    
    # 测试中文字体
    working_fonts = test_chinese_fonts()
    
    print(f"\n总结: 找到 {len(working_fonts)} 个可用的中文字体")
    
    if working_fonts:
        print("推荐使用的中文字体:")
        for font in working_fonts:
            print(f"  - {font}")
    else:
        print("警告: 未找到可用的中文字体!")
        print("建议:")
        print("  1. 安装中文字体包")
        print("  2. 使用系统默认字体")
        print("  3. 将字体文件放在项目目录中")
    
    # 简单的图形界面测试
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清屏
        screen.fill(WHITE)
        
        # 绘制测试文本
        try:
            # 尝试使用第一个可用的中文字体
            if working_fonts:
                font = pygame.font.Font(working_fonts[0], 48)
                text = font.render("你好世界 - Hello World", True, BLACK)
                text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                screen.blit(text, text_rect)
                
                # 显示字体路径
                info_font = pygame.font.Font(working_fonts[0], 24)
                info_text = info_font.render(f"使用字体: {os.path.basename(working_fonts[0])}", True, BLUE)
                info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 60))
                screen.blit(info_text, info_rect)
            else:
                # 使用默认字体
                font = pygame.font.Font(None, 48)
                text = font.render("No Chinese Font Available", True, RED)
                text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                screen.blit(text, text_rect)
                
                info_font = pygame.font.Font(None, 24)
                info_text = info_font.render("Press ESC to exit", True, BLUE)
                info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 60))
                screen.blit(info_text, info_rect)
                
        except Exception as e:
            # 如果字体渲染失败，显示错误信息
            error_font = pygame.font.Font(None, 24)
            error_text = error_font.render(f"Font Error: {str(e)}", True, RED)
            error_rect = error_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(error_text, error_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
