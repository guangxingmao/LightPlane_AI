#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义模式中文显示测试脚本
验证修改后的自定义模式是否能正常显示中文
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
pygame.display.set_caption('自定义模式中文测试')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

def test_custom_config_import():
    """测试自定义配置页面模块导入"""
    try:
        import custom_config_page
        print("✓ custom_config_page模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ custom_config_page模块导入失败: {e}")
        return False

def test_custom_game_import():
    """测试自定义游戏页面模块导入"""
    try:
        from custom_game_page import CustomGamePage
        print("✓ custom_game_page模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ custom_game_page模块导入失败: {e}")
        return False

def test_font_manager():
    """测试字体管理器"""
    try:
        from font_manager import render_chinese_text, get_chinese_font
        print("✓ 字体管理器导入成功")
        
        # 测试中文文本渲染
        test_text = "测试中文显示"
        text_surface = render_chinese_text(test_text, 24, BLACK)
        print(f"✓ 中文文本渲染成功: {test_text}")
        return True
    except Exception as e:
        print(f"✗ 字体管理器测试失败: {e}")
        return False

def main():
    """主函数"""
    print("自定义模式中文显示测试")
    print("=" * 50)
    
    # 测试模块导入
    config_ok = test_custom_config_import()
    game_ok = test_custom_game_import()
    font_ok = test_font_manager()
    
    if not all([config_ok, game_ok, font_ok]):
        print("测试失败，无法继续")
        return
    
    # 创建自定义配置页面实例
    try:
        import custom_config_page
        config_page = custom_config_page.CustomConfigPage(screen)
        print("✓ 自定义配置页面创建成功")
    except Exception as e:
        print(f"✗ 自定义配置页面创建失败: {e}")
        return
    
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
        
        # 绘制测试信息
        try:
            from font_manager import render_chinese_text
            
            # 标题
            title = render_chinese_text("自定义模式中文显示测试", 36, BLACK)
            title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 100))
            screen.blit(title, title_rect)
            
            # 测试文本
            test_texts = [
                "✓ custom_config_page模块导入成功",
                "✓ custom_game_page模块导入成功",
                "✓ 字体管理器工作正常",
                "✓ 自定义配置页面创建成功",
                "✓ 中文显示测试通过"
            ]
            
            y_offset = 200
            for i, text in enumerate(test_texts):
                color = GREEN if "✓" in text else BLACK
                text_surface = render_chinese_text(text, 24, color)
                text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, y_offset + i * 40))
                screen.blit(text_surface, text_rect)
            
            # 显示已翻译的文本示例
            translated_texts = [
                "自定义配置",
                "玩家战机",
                "敌机",
                "背景",
                "上传",
                "AI生成",
                "清除",
                "返回",
                "完成"
            ]
            
            y_offset = 450
            for i, text in enumerate(translated_texts):
                text_surface = render_chinese_text(text, 20, BLUE)
                text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, y_offset + i * 25))
                screen.blit(text_surface, text_rect)
            
            # 底部信息
            info_text = render_chinese_text("按ESC键退出测试", 20, RED)
            info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
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
