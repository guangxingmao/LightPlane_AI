#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文显示演示脚本
展示使用字体管理器后的中文显示效果
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
pygame.display.set_caption('中文显示演示')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

def main():
    """主函数"""
    clock = pygame.time.Clock()
    running = True
    
    # 导入字体管理器
    try:
        from font_manager import render_chinese_text, get_chinese_font
        font_available = True
        print("✓ 字体管理器加载成功")
    except ImportError as e:
        font_available = False
        print(f"✗ 字体管理器加载失败: {e}")
    
    # 测试文本
    test_texts = [
        "你好世界 - Hello World",
        "生命: 5",
        "分数: 1000",
        "彩蛋等级: 3",
        "特效: 彩虹模式!",
        "按空格键触发彩蛋",
        "游戏结束 - Game Over",
        "重新开始 - Restart"
    ]
    
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
        if font_available:
            try:
                # 使用字体管理器渲染中文标题
                title = render_chinese_text("pygame中文显示演示", 48, BLACK)
                title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
                screen.blit(title, title_rect)
                
                # 绘制测试文本
                y_offset = 120
                for i, text in enumerate(test_texts):
                    # 根据文本内容选择颜色
                    if "生命" in text or "分数" in text:
                        color = GREEN
                    elif "彩蛋" in text or "特效" in text:
                        color = BLUE
                    elif "游戏结束" in text:
                        color = RED
                    else:
                        color = BLACK
                    
                    text_surface = render_chinese_text(text, 24, color)
                    text_rect = text_surface.get_rect(left=50, top=y_offset + i * 35)
                    screen.blit(text_surface, text_rect)
                
                # 显示状态信息
                status_text = render_chinese_text("✓ 中文字体显示正常", 20, GREEN)
                status_rect = status_text.get_rect(left=50, top=WINDOW_HEIGHT - 60)
                screen.blit(status_text, status_rect)
                
                info_text = render_chinese_text("按ESC键退出", 20, BLUE)
                info_rect = info_text.get_rect(left=50, top=WINDOW_HEIGHT - 40)
                screen.blit(info_text, info_rect)
                
            except Exception as e:
                # 如果字体管理器失败，显示错误信息
                error_font = pygame.font.Font(None, 24)
                error_text = error_font.render(f"Font Error: {str(e)}", True, RED)
                error_rect = error_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                screen.blit(error_text, error_rect)
        else:
            # 字体管理器不可用，使用默认字体
            default_font = pygame.font.Font(None, 36)
            title = default_font.render("Chinese Font Manager Not Available", True, RED)
            title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(title, title_rect)
            
            info_font = pygame.font.Font(None, 24)
            info_text = info_font.render("Press ESC to exit", True, BLUE)
            info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
            screen.blit(info_text, info_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
