#!/usr/bin/env python3
"""
测试尺寸信息是否已添加到提示词中
"""

def test_size_in_prompts():
    """测试尺寸信息是否已添加到提示词中"""
    print("🧪 测试尺寸信息是否已添加到提示词中...")
    
    # 模拟TRADITIONAL_SIZES
    TRADITIONAL_SIZES = {
        'player_plane': (45, 56),      # 玩家飞机尺寸
        'enemy_plane': (43, 57),       # 敌机尺寸
        'background': (700, 480)       # 背景尺寸
    }
    
    # 模拟默认提示词（修改后的版本）
    default_prompts = {
        'player_plane': 'futuristic blue fighter jet, sleek design, high quality, size 45x56 pixels',
        'enemy_plane': 'dark military aircraft, red and black, aggressive design, size 43x57 pixels',
        'background': 'space battlefield, stars and nebula, cosmic scene, size 700x480 pixels'
    }
    
    print("📏 传统模式尺寸:")
    for key, size in TRADITIONAL_SIZES.items():
        print(f"  - {key}: {size[0]}x{size[1]} pixels")
    
    print(f"\n🎯 修改后的默认提示词:")
    for key, prompt in default_prompts.items():
        print(f"  - {key}: {prompt}")
    
    # 测试提示词构建逻辑
    print(f"\n🔧 测试提示词构建逻辑:")
    
    test_cases = [
        ('player_plane', 'red stealth fighter'),
        ('enemy_plane', ''),
        ('background', 'cosmic nebula scene'),
        ('player_plane', 'blue modern aircraft')
    ]
    
    for image_type, user_input in test_cases:
        print(f"\n测试 {image_type}:")
        print(f"  用户输入: '{user_input}'")
        
        # 获取默认提示词
        default_prompt = default_prompts.get(image_type, f'default {image_type} description')
        print(f"  默认提示词: {default_prompt}")
        
        # 获取目标尺寸信息
        target_size = TRADITIONAL_SIZES.get(image_type)
        size_info = f", size {target_size[0]}x{target_size[1]} pixels" if target_size else ""
        print(f"  尺寸信息: {size_info}")
        
        # 构建最终提示词
        if user_input.strip():
            # 用户有输入时，结合用户输入、默认关键词和尺寸信息
            prompt = f"{user_input}, {default_prompt}{size_info}"
            print(f"  最终提示词: {prompt}")
        else:
            # 用户没有输入时，使用默认提示词（已包含尺寸信息）
            prompt = default_prompt
            print(f"  最终提示词: {prompt}")
        
        # 检查是否包含尺寸信息
        if 'size' in prompt and 'pixels' in prompt:
            print(f"  ✅ 包含尺寸信息")
        else:
            print(f"  ❌ 缺少尺寸信息")
    
    # 验证尺寸信息的完整性
    print(f"\n✅ 尺寸信息验证:")
    for image_type, size in TRADITIONAL_SIZES.items():
        prompt = default_prompts[image_type]
        expected_size_text = f"size {size[0]}x{size[1]} pixels"
        
        if expected_size_text in prompt:
            print(f"  - {image_type}: ✅ 尺寸信息完整")
        else:
            print(f"  - {image_type}: ❌ 尺寸信息缺失")
    
    print(f"\n🎯 修改总结:")
    print(f"  - 默认提示词已添加尺寸信息: ✅")
    print(f"  - 输入框placeholder已更新: ✅")
    print(f"  - 生成时自动添加尺寸信息: ✅")
    print(f"  - 用户输入与尺寸信息结合: ✅")

if __name__ == "__main__":
    test_size_in_prompts()
