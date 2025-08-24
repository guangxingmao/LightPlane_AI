#!/usr/bin/env python3
"""
测试背景去除功能
"""

import os
import sys
import pygame

def test_background_removal():
    """测试背景去除功能"""
    print("🧪 测试背景去除功能...")
    
    try:
        from background_remover import BackgroundRemover
        
        # 创建背景去除器
        remover = BackgroundRemover()
        print(f"✓ 背景去除器创建成功，可用模型: {remover.get_available_models()}")
        
        # 检查是否有可用的模型
        if not remover.get_available_models():
            print("❌ 没有可用的AI模型")
            return False
        
        # 设置模型
        current_model = remover.get_available_models()[0]
        remover.set_model(current_model)
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
        
        # 检查文件信息
        if os.path.exists(test_image):
            file_size = os.path.getsize(test_image)
            print(f"文件大小: {file_size} bytes")
            
            # 尝试读取图片
            try:
                import cv2
                test_cv2 = cv2.imread(test_image)
                if test_cv2 is not None:
                    print(f"OpenCV读取成功，尺寸: {test_cv2.shape}")
                else:
                    print("OpenCV读取失败")
            except Exception as e:
                print(f"OpenCV测试失败: {e}")
            
            # 尝试使用PIL读取
            try:
                from PIL import Image
                test_pil = Image.open(test_image)
                print(f"PIL读取成功，尺寸: {test_pil.size}, 模式: {test_pil.mode}")
            except Exception as e:
                print(f"PIL测试失败: {e}")
            
            # 尝试背景去除
            print(f"\n🚀 开始背景去除测试...")
            try:
                output_path = f"test_output_{os.path.basename(test_image)}"
                result = remover.remove_background(test_image, output_path)
                
                if result:
                    print(f"✓ 背景去除成功！")
                    if isinstance(result, str):
                        print(f"输出文件: {result}")
                    else:
                        print(f"输出对象类型: {type(result)}")
                    
                    # 检查输出文件
                    if os.path.exists(output_path):
                        output_size = os.path.getsize(output_path)
                        print(f"输出文件大小: {output_size} bytes")
                        
                        # 清理测试文件
                        os.remove(output_path)
                        print("✓ 测试文件已清理")
                    
                    return True
                else:
                    print("❌ 背景去除失败")
                    return False
                    
            except Exception as e:
                print(f"❌ 背景去除过程中发生错误: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print(f"❌ 测试图片不存在: {test_image}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("背景去除功能测试")
    print("=" * 50)
    
    success = test_background_removal()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试成功！背景去除功能正常工作")
    else:
        print("❌ 测试失败！请检查错误信息")
        print("\n🔧 故障排除建议:")
        print("1. 确保已安装所有依赖包")
        print("2. 检查图片文件格式是否支持")
        print("3. 查看详细的错误日志")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
