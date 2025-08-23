#!/usr/bin/env python3
"""
测试配置保存和读取
"""

import pygame
import os

def test_config():
    """测试配置功能"""
    print("🧪 测试配置功能...")
    
    # 初始化 pygame
    pygame.init()
    # 设置视频模式（最小尺寸）
    pygame.display.set_mode((1, 1))
    
    # 模拟配置
    config = {
        'player_plane': None,
        'enemy_plane': None,
        'background': None,
        'player_plane_path': None,
        'enemy_plane_path': None,
        'background_path': None
    }
    
    print(f"初始配置: {config}")
    
    # 测试加载图片
    try:
        # 测试加载玩家飞机图片
        player_path = os.path.join('images', 'me1.png')
        if os.path.exists(player_path):
            print(f"✅ 找到玩家飞机图片: {player_path}")
            player_image = pygame.image.load(player_path).convert_alpha()
            print(f"  - 图片尺寸: {player_image.get_size()}")
            
            # 保存到配置
            config['player_plane'] = player_image
            config['player_plane_path'] = player_path
            print(f"✅ 已保存玩家飞机图片到配置")
        else:
            print(f"❌ 玩家飞机图片不存在: {player_path}")
            
        # 测试加载敌机图片
        enemy_path = os.path.join('images', 'enemy1.png')
        if os.path.exists(enemy_path):
            print(f"✅ 找到敌机图片: {enemy_path}")
            enemy_image = pygame.image.load(enemy_path).convert_alpha()
            print(f"  - 图片尺寸: {enemy_image.get_size()}")
            
            # 保存到配置
            config['enemy_plane'] = enemy_image
            config['enemy_plane_path'] = enemy_path
            print(f"✅ 已保存敌机图片到配置")
        else:
            print(f"❌ 敌机图片不存在: {enemy_path}")
            
        # 测试加载背景图片
        background_path = os.path.join('images', 'background.png')
        if os.path.exists(background_path):
            print(f"✅ 找到背景图片: {background_path}")
            background_image = pygame.image.load(background_path).convert_alpha()
            print(f"  - 图片尺寸: {background_image.get_size()}")
            
            # 保存到配置
            config['background'] = background_image
            config['background_path'] = background_path
            print(f"✅ 已保存背景图片到配置")
        else:
            print(f"❌ 背景图片不存在: {background_path}")
            
    except Exception as e:
        print(f"❌ 加载图片失败: {e}")
    
    print(f"\n最终配置状态:")
    print(f"  - player_plane: {config['player_plane'] is not None}")
    print(f"  - enemy_plane: {config['enemy_plane'] is not None}")
    print(f"  - background: {config['background'] is not None}")
    
    # 测试配置复制
    config_copy = config.copy()
    print(f"\n配置复制测试:")
    print(f"  - 原始配置 player_plane: {config['player_plane'] is not None}")
    print(f"  - 复制配置 player_plane: {config_copy['player_plane'] is not None}")
    
    pygame.quit()

if __name__ == "__main__":
    test_config()
