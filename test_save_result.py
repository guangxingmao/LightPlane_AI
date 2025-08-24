#!/usr/bin/env python3
"""
测试保存背景去除结果
"""

import os
import cv2
import numpy as np
from PIL import Image

def test_save_background_removal():
    """测试保存背景去除结果"""
    print("🧪 测试保存背景去除结果...")
    
    try:
        from background_remover import BackgroundRemover
        
        # 创建背景去除器
        remover = BackgroundRemover()
        print(f"✓ 背景去除器创建成功，可用模型: {remover.get_available_models()}")
        
        # 设置模型
        remover.set_model('opencv')
        print("✓ 已设置OpenCV模型")
        
        # 测试图片
        test_image = "./images/bomb.png"
        if not os.path.exists(test_image):
            print(f"测试图片不存在: {test_image}")
            return False
        
        print(f"🔍 测试图片: {test_image}")
        
        # 使用改进的算法去除背景
        output_path = "test_result_bomb.png"
        print(f"开始背景去除...")
        
        try:
            result = remover.remove_background(test_image, output_path)
            
            if result:
                print(f"✓ 背景去除成功！")
                
                # 检查输出文件
                if os.path.exists(output_path):
                    output_size = os.path.getsize(output_path)
                    print(f"输出文件大小: {output_size} bytes")
                    
                    # 分析结果
                    analyze_saved_result(test_image, output_path)
                    
                    print(f"结果已保存到: {output_path}")
                    print("请查看这个文件来确认背景去除效果")
                    
                    return True
                else:
                    print("❌ 输出文件不存在")
                    return False
                    
            else:
                print("❌ 背景去除失败")
                return False
                
        except Exception as e:
            print(f"❌ 背景去除过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_saved_result(original_path, processed_path):
    """分析保存的结果"""
    try:
        print(f"\n🔍 分析保存的结果...")
        
        # 读取原始图片
        original = cv2.imread(original_path)
        if original is not None:
            print(f"原始图片尺寸: {original.shape}")
        
        # 尝试多种方式读取处理后的图片
        processed = None
        
        # 方法1: 使用cv2.IMREAD_UNCHANGED
        processed = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
        if processed is not None:
            print(f"✓ 使用cv2.IMREAD_UNCHANGED读取成功")
        else:
            # 方法2: 使用PIL读取
            try:
                pil_image = Image.open(processed_path)
                processed = np.array(pil_image)
                print(f"✓ 使用PIL读取成功")
            except Exception as e:
                print(f"❌ PIL读取失败: {e}")
                return
        
        if processed is None:
            print("❌ 无法读取处理后的图片")
            return
        
        print(f"处理后图片尺寸: {processed.shape}")
        
        # 检查是否有透明通道
        if len(processed.shape) == 3 and processed.shape[2] == 4:
            print("✓ 图片有4个通道（RGBA）")
            
            # 提取Alpha通道
            alpha = processed[:, :, 3]
            print(f"Alpha通道范围: {np.min(alpha)} - {np.max(alpha)}")
            
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
            
            # 保存Alpha通道用于查看
            alpha_path = "test_alpha_channel.png"
            cv2.imwrite(alpha_path, alpha)
            print(f"Alpha通道已保存到: {alpha_path}")
            
        elif len(processed.shape) == 3 and processed.shape[2] == 3:
            print("⚠ 图片有3个通道（RGB），没有透明通道")
        else:
            print(f"⚠ 图片格式异常: {processed.shape}")
            
    except Exception as e:
        print(f"❌ 分析结果失败: {e}")
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

def main():
    """主函数"""
    print("=" * 50)
    print("背景去除结果保存测试")
    print("=" * 50)
    
    success = test_save_background_removal()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试成功！背景去除结果已保存")
        print("\n💡 查看结果:")
        print("• 主结果文件: test_result_bomb.png")
        print("• Alpha通道: test_alpha_channel.png")
        print("• 请用图片查看器打开这些文件查看效果")
    else:
        print("❌ 测试失败！请检查错误信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
