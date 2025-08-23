#!/usr/bin/env python3
"""
测试输入框显示逻辑
"""

def test_input_display():
    """测试输入框显示逻辑"""
    print("🧪 测试输入框显示逻辑...")
    
    # 模拟输入框数据
    input_boxes = [
        {
            'type': 'player_plane',
            'text': 'futuristic blue fighter jet, sleek design, high quality',
            'placeholder': 'Enter player plane description...',
            'active': False
        },
        {
            'type': 'enemy_plane',
            'text': 'dark military aircraft, red and black, aggressive design',
            'placeholder': 'Enter enemy plane description...',
            'active': False
        },
        {
            'type': 'background',
            'text': 'space battlefield, stars and nebula, cosmic scene',
            'placeholder': 'Enter background description...',
            'active': False
        }
    ]
    
    print("初始状态:")
    for box in input_boxes:
        print(f"  - {box['type']}: '{box['text']}' (active: {box['active']})")
    
    # 测试选中输入框
    print(f"\n🎯 测试选中输入框...")
    
    for box in input_boxes:
        print(f"\n选中 {box['type']} 输入框:")
        print(f"  选中前: '{box['text']}' (active: {box['active']})")
        
        # 模拟选中逻辑
        box['active'] = True
        
        # 如果当前文本是默认关键词，则清空文本
        if box['text'] == box.get('placeholder', ''):
            box['text'] = ''
            print(f"  🧹 清空默认关键词")
        
        print(f"  选中后: '{box['text']}' (active: {box['active']})")
    
    # 测试显示逻辑
    print(f"\n📝 测试显示逻辑...")
    
    for box in input_boxes:
        print(f"\n{box['type']} 显示内容:")
        
        if box['active']:
            # 激活状态下只显示用户实际输入的内容，不显示默认关键词
            display_text = box['text'] if box['text'] and box['text'] != box.get('placeholder', '') else ''
            text_color = "黑色"
            print(f"  激活状态: '{display_text}' (颜色: {text_color})")
        else:
            # 非激活状态下显示用户输入内容或默认关键词
            display_text = box['text'] if box['text'] else box['placeholder']
            text_color = "灰色"
            print(f"  非激活状态: '{display_text}' (颜色: {text_color})")
    
    print(f"\n最终状态:")
    for box in input_boxes:
        print(f"  - {box['type']}: '{box['text']}' (active: {box['active']})")

if __name__ == "__main__":
    test_input_display()
