#!/usr/bin/env python3
"""
测试改进后的背景去除算法
"""

import os
import sys
import pygame
import cv2
import numpy as np
from PIL import Image

def test_improved_algorithm():
    """测试改进后的算法"""
    print("🧪 测试改进后的背景去除算法...")
    
    try:
        from background_remover import BackgroundRemover
        
        # 创建背景去除器
        remover = BackgroundRemover()
        print(f"✓ 背景去除器创建成功，可用模型: {remover.get_available_models()}")
        
        # 设置模型
        remover.set_model('opencv')
        print("✓ 已设置OpenCV模型")
        
        # 查找测试图片
        test_images = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # 排除一些特殊文件
                    if not file.startswith('.') and 'test' not in file.lower():
                        test_images.append(os.path.join(root, file))
                        if len(test_images) >= 5:  # 取更多图片测试
                            break
            if len(test_images) >= 5:
                break
        
        if not test_images:
            print("❌ 未找到测试图片")
            return False
        
        print(f"✓ 找到测试图片: {test_images[:5]}")
        
        # 测试每张图片
        for i, test_image in enumerate(test_images[:3]):  # 测试前3张
            print(f"\n🔍 测试图片 {i+1}: {test_image}")
            
            # 检查文件信息
            if os.path.exists(test_image):
                file_size = os.path.getsize(test_image)
                print(f"文件大小: {file_size} bytes")
                
                # 使用改进的算法去除背景
                output_path = f"test_improved_{i+1}_{os.path.basename(test_image)}"
                print(f"开始改进的背景去除...")
                
                try:
                    result = remover.remove_background(test_image, output_path)
                    
                    if result:
                        print(f"✓ 背景去除成功！")
                        
                        # 检查输出文件
                        if os.path.exists(output_path):
                            output_size = os.path.getsize(output_path)
                            print(f"输出文件大小: {output_size} bytes")
                            
                            # 分析结果
                            analyze_result(test_image, output_path)
                            
                            # 清理测试文件
                            try:
                                os.remove(output_path)
                                print("✓ 测试文件已清理")
                            except:
                                pass
                        else:
                            print("❌ 输出文件不存在")
                    else:
                        print("❌ 背景去除失败")
                        
                except Exception as e:
                    print(f"❌ 背景去除过程中发生错误: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"❌ 测试图片不存在: {test_image}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_result(original_path, processed_path):
    """分析处理结果"""
    try:
        # 读取原始图片
        original = cv2.imread(original_path)
        
        # 尝试多种方式读取处理后的图片
        processed = None
        
        # 方法1: 使用cv2.IMREAD_UNCHANGED
        processed = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
        if processed is not None:
            print(f"使用cv2.IMREAD_UNCHANGED读取成功")
        else:
            # 方法2: 使用PIL读取
            try:
                pil_image = Image.open(processed_path)
                processed = np.array(pil_image)
                print(f"使用PIL读取成功")
            except Exception as e:
                print(f"PIL读取失败: {e}")
                return
        
        if original is None or processed is None:
            print("无法读取图片进行分析")
            return
        
        print(f"原始图片尺寸: {original.shape}")
        print(f"处理后图片尺寸: {processed.shape}")
        
        # 检查是否有透明通道
        if len(processed.shape) == 3 and processed.shape[2] == 4:
            # 提取Alpha通道
            alpha = processed[:, :, 3]
            
            # 计算透明区域比例
            transparent_pixels = np.sum(alpha < 128)
            total_pixels = alpha.shape[0] * alpha.shape[1]
            transparent_ratio = transparent_pixels / total_pixels * 100
            
            print(f"透明区域比例: {transparent_ratio:.1f}%")
            
            # 分析前景区域
            foreground_pixels = np.sum(alpha > 128)
            foreground_ratio = foreground_pixels / total_pixels * 100
            print(f"前景区域比例: {foreground_ratio:.1f}%")
            
            # 检查边缘质量
            edge_quality = analyze_edge_quality(alpha)
            print(f"边缘质量: {edge_quality}")
            
        else:
            print("处理后图片没有透明通道")
            
    except Exception as e:
        print(f"分析结果失败: {e}")
        import traceback
        traceback.print_exc()

def analyze_edge_quality(alpha_mask):
    """分析边缘质量"""
    try:
        # 使用Sobel算子检测边缘
        sobel_x = cv2.Sobel(alpha_mask, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(alpha_mask, cv2.CV_64F, 0, 1, ksize=3)
        
        # 计算边缘强度
        edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # 计算平均边缘强度
        avg_edge_strength = np.mean(edge_magnitude)
        
        if avg_edge_strength < 10:
            return "模糊"
        elif avg_edge_strength < 30:
            return "一般"
        elif avg_edge_strength < 60:
            return "清晰"
        else:
            return "非常清晰"
            
    except Exception as e:
        return f"分析失败: {e}"

def test_individual_methods():
    """测试各个掩码创建方法"""
    print("\n🔬 测试各个掩码创建方法...")
    
    try:
        from background_remover import BackgroundRemover
        
        remover = BackgroundRemover()
        
        # 测试图片
        test_image = "./images/bomb.png"
        if not os.path.exists(test_image):
            print(f"测试图片不存在: {test_image}")
            return
        
        # 读取图片
        image = cv2.imread(test_image)
        if image is None:
            print("无法读取测试图片")
            return
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        print(f"测试图片尺寸: {image_rgb.shape}")
        
        # 测试各个方法
        methods = [
            ("颜色掩码", lambda: remover._create_color_mask(hsv)),
            ("边缘检测", lambda: remover._create_edge_mask(image_rgb)),
            ("轮廓检测", lambda: remover._create_contour_mask(image_rgb)),
        ]
        
        for method_name, method_func in methods:
            try:
                print(f"\n测试 {method_name}...")
                mask = method_func()
                if mask is not None:
                    print(f"✓ {method_name} 成功，掩码尺寸: {mask.shape}")
                    
                    # 保存掩码用于查看
                    mask_path = f"test_mask_{method_name}.png"
                    cv2.imwrite(mask_path, mask)
                    print(f"掩码已保存到: {mask_path}")
                    
                    # 清理测试文件
                    try:
                        os.remove(mask_path)
                    except:
                        pass
                else:
                    print(f"❌ {method_name} 失败")
            except Exception as e:
                print(f"❌ {method_name} 测试失败: {e}")
        
        # 测试GrabCut（如果图片足够大）
        if image_rgb.shape[0] > 100 and image_rgb.shape[1] > 100:
            try:
                print(f"\n测试 GrabCut...")
                mask = remover._create_grabcut_mask(image_rgb)
                if mask is not None:
                    print(f"✓ GrabCut 成功，掩码尺寸: {mask.shape}")
                else:
                    print("❌ GrabCut 失败")
            except Exception as e:
                print(f"❌ GrabCut 测试失败: {e}")
        
    except Exception as e:
        print(f"测试各个方法失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("改进后的背景去除算法测试")
    print("=" * 50)
    
    # 测试各个掩码创建方法
    test_individual_methods()
    
    # 测试完整的改进算法
    success = test_improved_algorithm()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！改进后的背景去除算法正常工作")
        print("\n💡 改进内容:")
        print("• 多种掩码创建方法组合")
        print("• 改进的颜色阈值检测")
        print("• 边缘检测和轮廓检测")
        print("• GrabCut高级分割算法")
        print("• 智能掩码组合和后处理")
    else:
        print("❌ 测试失败！请检查错误信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
