#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义模式中文显示效果测试脚本
验证修改后的自定义模式是否能正常显示中文
"""

import pygame
import sys
import os

# 初始化pygame
pygame.init()

# 设置窗口
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('自定义模式中文显示效果测试')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (100, 255, 100)
RED = (255, 100, 100)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

def main():
    """主函数"""
    clock = pygame.time.Clock()
    running = True
    
    # 导入自定义配置页面
    try:
        from custom_config_page import CustomConfigPage
        print("✓ 自定义配置页面导入成功")
        
        # 创建自定义配置页面实例
        config_page = CustomConfigPage(screen, WINDOW_WIDTH, WINDOW_HEIGHT)
        print("✓ 自定义配置页面创建成功")
        
        # 运行配置页面
        print("正在显示自定义配置页面...")
        print("按ESC键退出测试")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # 更新配置页面
            config_page.update()
            
            # 绘制配置页面
            config_page.draw()
            
            # 更新屏幕
            pygame.display.flip()
            clock.tick(60)
            
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        
        # 如果出错，显示错误信息
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # 清屏
            screen.fill(BLACK)
            
            # 显示错误信息
            try:
                from font_manager import render_chinese_text
                error_title = render_chinese_text("自定义模式加载失败", 48, RED)
                error_text = render_chinese_text(f"错误信息: {str(e)}", 24, WHITE)
                info_text = render_chinese_text("按ESC键退出", 20, BLUE)
                
                title_rect = error_title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
                text_rect = error_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
                
                screen.blit(error_title, title_rect)
                screen.blit(error_text, text_rect)
                screen.blit(info_text, info_rect)
                
            except:
                # 如果字体管理器也不可用，使用默认字体
                default_font = pygame.font.Font(None, 36)
                error_title = default_font.render("Custom Mode Loading Failed", True, RED)
                error_text = default_font.render(f"Error: {str(e)}", True, WHITE)
                info_text = default_font.render("Press ESC to exit", True, BLUE)
                
                title_rect = error_title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
                text_rect = error_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
                
                screen.blit(error_title, title_rect)
                screen.blit(error_text, text_rect)
                screen.blit(info_text, info_rect)
            
            pygame.display.flip()
            clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
