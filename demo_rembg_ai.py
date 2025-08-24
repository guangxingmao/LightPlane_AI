#!/usr/bin/env python3
"""
RemBG AI抠图功能演示
"""

import os
import cv2
import numpy as np
from PIL import Image
import time

def demo_rembg_ai():
    """演示RemBG AI抠图功能"""
    print("🎬 RemBG AI抠图功能演示")
    print("=" * 50)
    
    try:
        from background_remover import BackgroundRemover
        
        # 创建背景去除器
        remover = BackgroundRemover()
        print(f"✓ 背景去除器创建成功")
        print(f"📋 可用模型: {remover.get_available_models()}")
        
        # 确保RemBG可用
        if 'rembg' not in remover.get_available_models():
            print("❌ RemBG模型不可用，请先安装")
            return False
        
        # 设置RemBG为当前模型
        remover.set_model('rembg')
        print(f"🎯 已设置RemBG模型")
        
        # 演示图片列表
        demo_images = [
            "./images/bomb.png",
            "./images/resume_pressed.png"
        ]
        
        # 过滤存在的图片
        existing_images = [img for img in demo_images if os.path.exists(img)]
        
        if not existing_images:
            print("❌ 未找到演示图片")
            return False
        
        print(f"📸 找到演示图片: {len(existing_images)} 张")
        
        # 演示每张图片
        for i, demo_image in enumerate(existing_images):
            print(f"\n🎭 演示 {i+1}: {os.path.basename(demo_image)}")
            print("-" * 40)
            
            # 分析原始图片
            analyze_original_image(demo_image)
            
            # 使用RemBG处理
            print(f"\n🚀 开始RemBG AI抠图...")
            start_time = time.time()
            
            output_path = f"demo_rembg_{i+1}_{os.path.basename(demo_image)}"
            
            try:
                result = remover.remove_background(demo_image, output_path)
                
                if result:
                    processing_time = time.time() - start_time
                    print(f"✅ AI抠图完成！耗时: {processing_time:.2f}秒")
                    
                    # 分析结果
                    analyze_rembg_result(demo_image, output_path)
                    
                    # 清理演示文件
                    try:
                        os.remove(output_path)
                        print("✓ 演示文件已清理")
                    except:
                        pass
                        
                else:
                    print("❌ AI抠图失败")
                    return False
                    
            except Exception as e:
                print(f"❌ AI抠图过程中发生错误: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_original_image(image_path):
    """分析原始图片"""
    try:
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            print("❌ 无法读取图片")
            return
        
        # 基本信息
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) > 2 else 1
        file_size = os.path.getsize(image_path)
        
        print(f"📊 原始图片信息:")
        print(f"  尺寸: {width} x {height}")
        print(f"  通道: {channels}")
        print(f"  文件大小: {file_size} bytes")
        
        # 颜色分析
        if channels == 3:
            # 转换为RGB进行分析
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 计算主要颜色
            colors = ['红色', '绿色', '蓝色']
            for i, color in enumerate(colors):
                channel = image_rgb[:, :, i]
                avg_value = np.mean(channel)
                print(f"  {color}通道平均值: {avg_value:.1f}")
        
    except Exception as e:
        print(f"❌ 分析原始图片失败: {e}")

def analyze_rembg_result(original_path, processed_path):
    """分析RemBG处理结果"""
    try:
        print(f"\n🔍 RemBG处理结果分析:")
        
        # 读取原始图片
        original = cv2.imread(original_path)
        if original is not None:
            original_size = original.shape[:2]
        
        # 读取处理后的图片
        processed = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
        if processed is None:
            print("❌ 无法读取处理后的图片")
            return
        
        # 基本信息对比
        processed_size = processed.shape[:2]
        file_size = os.path.getsize(processed_path)
        
        print(f"📊 处理结果对比:")
        print(f"  原始尺寸: {original_size[1]} x {original_size[0]}")
        print(f"  处理后尺寸: {processed_size[1]} x {processed_size[0]}")
        print(f"  处理后文件大小: {file_size} bytes")
        
        # 检查透明通道
        if len(processed.shape) == 3 and processed.shape[2] == 4:
            print(f"✅ 成功生成RGBA透明图片")
            
            # 提取Alpha通道
            alpha = processed[:, :, 3]
            print(f"🎭 Alpha通道分析:")
            print(f"  值范围: {np.min(alpha)} - {np.max(alpha)}")
            
            # 计算透明区域比例
            transparent_pixels = np.sum(alpha < 128)
            total_pixels = alpha.shape[0] * alpha.shape[1]
            transparent_ratio = transparent_pixels / total_pixels * 100
            
            print(f"  透明区域比例: {transparent_ratio:.1f}%")
            
            # 分析前景区域
            foreground_pixels = np.sum(alpha > 128)
            foreground_ratio = foreground_pixels / total_pixels * 100
            print(f"  前景区域比例: {foreground_ratio:.1f}%")
            
            # 边缘质量分析
            edge_quality = analyze_edge_quality(alpha)
            print(f"  边缘质量: {edge_quality}")
            
            # 保存Alpha通道用于查看
            alpha_path = f"demo_alpha_{os.path.basename(processed_path)}"
            cv2.imwrite(alpha_path, alpha)
            print(f"  Alpha通道已保存到: {alpha_path}")
            
            # 清理Alpha通道文件
            try:
                os.remove(alpha_path)
                print("  ✓ Alpha通道文件已清理")
            except:
                pass
            
        else:
            print("⚠ 处理后图片没有透明通道")
            
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

def show_rembg_features():
    """展示RemBG特性"""
    print("\n🌟 RemBG AI抠图特性:")
    print("=" * 50)
    print("🚀 深度学习模型:")
    print("  • 基于U2Net架构")
    print("  • 自动下载预训练模型")
    print("  • 理解图片语义内容")
    
    print("\n🎯 智能识别能力:")
    print("  • 自动识别前景物体")
    print("  • 无需手动设置参数")
    print("  • 适应各种图片类型")
    
    print("\n✨ 高质量输出:")
    print("  • 边缘清晰自然")
    print("  • 保留细节信息")
    print("  • 生成透明背景")
    
    print("\n⚡ 性能优势:")
    print("  • 处理速度快")
    print("  • 内存占用低")
    print("  • 支持批量处理")

def main():
    """主函数"""
    print("🎬 RemBG AI抠图功能演示")
    print("=" * 50)
    
    # 运行演示
    success = demo_rembg_ai()
    
    # 展示特性
    show_rembg_features()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 演示成功完成！")
        print("\n💡 使用建议:")
        print("• 对于复杂背景的图片，优先使用RemBG")
        print("• 对于简单背景的图片，可以使用OpenCV")
        print("• RemBG特别适合人物、动物、物体等抠图")
        print("• 处理后的图片可以直接用于游戏素材")
    else:
        print("❌ 演示失败！请检查错误信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
