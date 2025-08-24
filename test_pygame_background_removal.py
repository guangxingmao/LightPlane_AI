#!/usr/bin/env python3
"""
测试Pygame surface的背景去除功能
"""

import os
import sys
import pygame

def test_pygame_background_removal():
    """测试Pygame surface的背景去除功能"""
    print("🧪 测试Pygame surface的背景去除功能...")
    
    try:
        from ai_image_processor import AIImageProcessor
        
        # 创建AI图片处理器
        processor = AIImageProcessor()
        print(f"✓ AI图片处理器创建成功，可用模型: {processor.get_available_models()}")
        
        # 检查是否有可用的模型
        if not processor.get_available_models():
            print("❌ 没有可用的AI模型")
            return False
        
        # 设置模型
        current_model = processor.get_available_models()[0]
        processor.set_model(current_model)
        print(f"✓ 已设置模型: {current_model}")
        
        # 查找测试图片
        test_images = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # 排除一些特殊文件
                    if not file.startswith('.') and 'test' not in file.lower():
                        test_images.append(os.path.join(root, file))
                        if len(test_images) >= 3:  # 只取前3个
                            break
            if len(test_images) >= 3:
                break
        
        if not test_images:
            print("❌ 未找到测试图片")
            return False
        
        print(f"✓ 找到测试图片: {test_images[:3]}")
        
        # 测试第一张图片
        test_image = test_images[0]
        print(f"\n🔍 测试图片: {test_image}")
        
        # 使用Pygame加载图片
        try:
            pygame_surface = pygame.image.load(test_image)
            print(f"✓ Pygame加载成功，尺寸: {pygame_surface.get_size()}")
            
            # 检查是否有透明通道
            if pygame_surface.get_alpha() is not None:
                print(f"✓ 图片有透明通道")
            else:
                print("⚠ 图片没有透明通道")
            
        except Exception as e:
            print(f"❌ Pygame加载失败: {e}")
            return False
        
        # 测试背景去除
        print(f"\n🚀 开始Pygame surface背景去除测试...")
        
        def on_complete(result):
            if result['status'] == 'success':
                print(f"✓ 背景去除成功！")
                print(f"类型: {result['type']}")
                print(f"原始路径: {result['original_path']}")
                print(f"处理后路径: {result['processed_path']}")
                print(f"Pygame surface类型: {type(result['pygame_surface'])}")
                print(f"Pygame surface尺寸: {result['pygame_surface'].get_size()}")
                
                # 检查输出文件
                if result['processed_path'] and os.path.exists(result['processed_path']):
                    output_size = os.path.getsize(result['processed_path'])
                    print(f"输出文件大小: {output_size} bytes")
                    
                    # 清理输出文件
                    try:
                        os.remove(result['processed_path'])
                        print("✓ 输出文件已清理")
                    except:
                        pass
                
                return True
            else:
                print(f"❌ 背景去除失败: {result['error']}")
                return False
        
        # 开始处理
        success = processor.process_pygame_surface(
            pygame_surface, 
            "test_plane", 
            callback=on_complete
        )
        
        if success:
            print("✓ 处理请求已提交")
            
            # 等待处理完成
            print("等待处理完成...")
            while processor.is_processing:
                status = processor.get_processing_status()
                print(f"状态: {status['status']}, 进度: {status['progress']}%, 消息: {status['message']}")
                pygame.time.wait(500)  # 等待500毫秒
            
            print("处理完成")
            return True
        else:
            print("❌ 处理请求提交失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("Pygame Surface背景去除功能测试")
    print("=" * 50)
    
    # 初始化Pygame
    pygame.init()
    
    try:
        success = test_pygame_background_removal()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 测试成功！Pygame surface背景去除功能正常工作")
        else:
            print("❌ 测试失败！请检查错误信息")
            print("\n🔧 故障排除建议:")
            print("1. 确保已安装所有依赖包")
            print("2. 检查图片文件格式是否支持")
            print("3. 查看详细的错误日志")
            print("4. 检查Pygame surface是否正确加载")
        
        print("=" * 50)
        
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
