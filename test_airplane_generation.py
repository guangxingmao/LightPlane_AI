#!/usr/bin/env python3
"""
测试飞机AI生成功能 - 使用更具体的关键词和更大尺寸
"""

import pygame
import sys
from local_image_generator import generate_image_local

# 初始化pygame
pygame.init()

def test_airplane_generation():
    """测试飞机AI生成功能"""
    print("✈️ 开始测试飞机AI生成...")
    
    # 测试不同的飞机关键词和尺寸
    test_cases = [
        {
            'prompt': 'white airplane flying in sky, side view aircraft, plane with wings',
            'size': (128, 96),  # 更大尺寸
            'name': 'white_airplane'
        },
        {
            'prompt': 'airplane silhouette, black and white plane, aircraft side profile',
            'size': (128, 96),
            'name': 'airplane_silhouette'
        },
        {
            'prompt': 'simple airplane drawing, minimalist plane design, aircraft outline',
            'size': (128, 96),
            'name': 'simple_airplane'
        },
        {
            'prompt': 'cartoon airplane, cute plane illustration, friendly aircraft',
            'size': (128, 96),
            'name': 'cartoon_airplane'
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        prompt = test_case['prompt']
        width, height = test_case['size']
        name = test_case['name']
        
        print(f"\n🔄 测试 {i+1}: {name}")
        print(f"   提示词: {prompt}")
        print(f"   尺寸: {width}x{height}")
        
        try:
            # 生成图片
            image = generate_image_local(prompt, width, height, steps=20)  # 增加步数
            
            if image:
                print(f"✅ 生成成功！图片尺寸: {image.get_size()}")
                
                # 保存图片用于查看
                filename = f"airplane_test_{name}_{width}x{height}.png"
                pygame.image.save(image, filename)
                print(f"💾 图片已保存为: {filename}")
            else:
                print("❌ 生成失败")
                
        except Exception as e:
            print(f"❌ 生成出错: {e}")
            import traceback
            traceback.print_exc()
    
    # 测试原始小尺寸
    print(f"\n🔄 测试原始小尺寸 (64x48):")
    try:
        prompt = 'airplane, plane, aircraft'
        image = generate_image_local(prompt, 64, 48, steps=20)
        
        if image:
            print(f"✅ 小尺寸生成成功！图片尺寸: {image.get_size()}")
            pygame.image.save(image, "airplane_test_small_64x48.png")
            print(f"💾 图片已保存为: airplane_test_small_64x48.png")
        else:
            print("❌ 小尺寸生成失败")
    except Exception as e:
        print(f"❌ 小尺寸生成出错: {e}")
    
    print("\n🏁 飞机测试完成")

if __name__ == "__main__":
    test_airplane_generation()
    pygame.quit()
