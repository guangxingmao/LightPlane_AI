#!/usr/bin/env python3
"""
自定义模式测试脚本
测试各个组件的功能
"""

import pygame
import sys
import os

def test_pygame_init():
    """测试pygame初始化"""
    try:
        pygame.init()
        print("✅ Pygame初始化成功")
        return True
    except Exception as e:
        print(f"❌ Pygame初始化失败: {e}")
        return False

def test_custom_config_page():
    """测试自定义配置页面"""
    try:
        from custom_config_page import CustomConfigPage
        print("✅ 自定义配置页面导入成功")
        
        # 创建测试屏幕
        screen = pygame.display.set_mode((800, 600))
        config_page = CustomConfigPage(screen, 800, 600)
        print("✅ 自定义配置页面创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 自定义配置页面测试失败: {e}")
        return False

def test_custom_game_page():
    """测试自定义游戏页面"""
    try:
        from custom_game_page import CustomGamePage
        print("✅ 自定义游戏页面导入成功")
        
        # 创建测试屏幕
        screen = pygame.display.set_mode((800, 600))
        
        # 创建测试配置
        test_config = {
            'player_plane': None,
            'enemy_plane': None,
            'background': None,
            'player_plane_path': '',
            'enemy_plane_path': '',
            'background_path': ''
        }
        
        game_page = CustomGamePage(screen, 800, 600, test_config)
        print("✅ 自定义游戏页面创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 自定义游戏页面测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖库"""
    try:
        import PIL
        print("✅ PIL/Pillow库可用")
    except ImportError:
        print("❌ PIL/Pillow库不可用")
        
    try:
        import requests
        print("✅ requests库可用")
    except ImportError:
        print("❌ requests库不可用")
        
    try:
        import tkinter
        print("✅ tkinter库可用")
    except ImportError:
        print("❌ tkinter库不可用")

def main():
    """主测试函数"""
    print("🚀 开始测试自定义模式...")
    print("=" * 50)
    
    # 测试依赖
    print("\n📦 测试依赖库:")
    test_dependencies()
    
    # 测试pygame
    print("\n🎮 测试Pygame:")
    if not test_pygame_init():
        print("❌ Pygame测试失败，无法继续")
        return
        
    # 测试自定义配置页面
    print("\n⚙️ 测试自定义配置页面:")
    if not test_custom_config_page():
        print("❌ 自定义配置页面测试失败")
        
    # 测试自定义游戏页面
    print("\n🎯 测试自定义游戏页面:")
    if not test_custom_game_page():
        print("❌ 自定义游戏页面测试失败")
        
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    
    # 清理pygame
    pygame.quit()

if __name__ == "__main__":
    main()
