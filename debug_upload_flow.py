#!/usr/bin/env python3
"""
调试图片上传流程
"""

import pygame
import os
import subprocess
import sys

def debug_upload_flow():
    """调试图片上传流程"""
    print("🔍 调试图片上传流程...")
    
    # 初始化 pygame
    pygame.init()
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
    
    # 测试文件选择器
    print("\n📁 测试文件选择器...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    selector_script = os.path.join(current_dir, 'pyqt5_file_selector.py')
    
    print(f"选择器脚本路径: {selector_script}")
    print(f"脚本是否存在: {os.path.exists(selector_script)}")
    
    # 测试上传 player_plane
    print(f"\n🎯 测试上传 player_plane...")
    try:
        result = subprocess.run(
            [sys.executable, selector_script, 'player_plane'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"返回码: {result.returncode}")
        print(f"输出: {result.stdout.strip()}")
        if result.stderr:
            print(f"错误: {result.stderr.strip()}")
            
        if result.returncode == 0 and result.stdout.strip():
            output = result.stdout.strip()
            if output.startswith("SELECTED_FILE:"):
                file_path = output[14:]
                print(f"✅ 选择文件: {file_path}")
                
                # 测试加载图片
                try:
                    original_image = pygame.image.load(file_path).convert_alpha()
                    original_size = original_image.get_size()
                    print(f"✅ 图片加载成功: {original_size}")
                    
                    # 测试缩放
                    target_size = (45, 56)  # player_plane 的目标尺寸
                    scaled_image = pygame.transform.scale(original_image, target_size)
                    print(f"✅ 图片缩放成功: {target_size}")
                    
                    # 保存到配置
                    config['player_plane'] = scaled_image
                    config['player_plane_path'] = file_path
                    print(f"✅ 配置保存成功")
                    
                except Exception as e:
                    print(f"❌ 图片处理失败: {e}")
            else:
                print(f"❌ 文件选择失败: {output}")
        else:
            print(f"❌ 文件选择器失败")
            
    except subprocess.TimeoutExpired:
        print("⏰ 文件选择器超时")
    except Exception as e:
        print(f"❌ 文件选择器异常: {e}")
    
    print(f"\n最终配置状态:")
    print(f"  - player_plane: {config['player_plane'] is not None}")
    print(f"  - player_plane_path: {config['player_plane_path']}")
    
    pygame.quit()

if __name__ == "__main__":
    debug_upload_flow()
