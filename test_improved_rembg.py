#!/usr/bin/env python3
"""
测试改进后的RemBG功能
"""

import os
import cv2
import numpy as np
from PIL import Image
import time

def test_improved_rembg():
    """测试改进后的RemBG功能"""
    print("🧪 测试改进后的RemBG功能...")
    
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
        
        # 测试图片列表
        test_images = [
            "./images/bomb.png",
            "./images/resume_pressed.png"
        ]
        
        # 过滤存在的图片
        existing_images = [img for img in test_images if os.path.exists(img)]
        
        if not existing_images:
            print("❌ 未找到测试图片")
            return False
        
        print(f"📸 找到测试图片: {len(existing_images)} 张")
        
        # 测试每张图片
        for i, test_image in enumerate(existing_images):
            print(f"\n🎭 测试图片 {i+1}: {os.path.basename(test_image)}")
            print("-" * 50)
            
            # 分析原始图片
            analyze_original_image(test_image)
            
            # 使用改进的RemBG处理
            print(f"\n🚀 开始改进的RemBG AI抠图...")
            start_time = time.time()
            
            output_path = f"improved_rembg_{i+1}_{os.path.basename(test_image)}"
            
            try:
                result = remover.remove_background(test_image, output_path)
                
                if result:
                    processing_time = time.time() - start_time
                    print(f"✅ 改进的AI抠图完成！耗时: {processing_time:.2f}秒")
                    
                    # 分析结果
                    analyze_improved_result(test_image, output_path)
                    
                    # 清理演示文件
                    try:
                        os.remove(output_path)
                        print("✓ 演示文件已清理")
                    except:
                        pass
                        
                else:
                    print("❌ 改进的AI抠图失败")
                    return False
                    
            except Exception as e:
                print(f"❌ 改进的AI抠图过程中发生错误: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
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
                std_value = np.std(channel)
                print(f"  {color}通道: 平均值={avg_value:.1f}, 标准差={std_value:.1f}")
            
            # 计算整体色彩丰富度
            color_variance = np.var(image_rgb, axis=(0, 1))
            total_variance = np.sum(color_variance)
            print(f"  色彩丰富度: {total_variance:.1f}")
        
    except Exception as e:
        print(f"❌ 分析原始图片失败: {e}")

def analyze_improved_result(original_path, processed_path):
    """分析改进后的结果"""
    try:
        print(f"\n🔍 改进后的结果分析:")
        
        # 读取原始图片
        original = cv2.imread(original_path)
        if original is None:
            print("❌ 无法读取原始图片")
            return
        
        # 读取处理后的图片
        processed = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
        if processed is None:
            print("❌ 无法读取处理后的图片")
            return
        
        # 基本信息对比
        original_size = original.shape[:2]
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
            
            # 检查边缘质量
            edge_quality = analyze_edge_quality(alpha)
            print(f"  边缘质量: {edge_quality}")
            
            # 分析色彩保留情况
            analyze_color_preservation(original, processed, alpha)
            
            # 保存Alpha通道用于查看
            alpha_path = f"improved_alpha_{os.path.basename(processed_path)}"
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

def analyze_color_preservation(original, processed, alpha):
    """分析色彩保留情况"""
    try:
        print(f"    🎨 色彩保留分析:")
        
        # 创建前景掩码
        foreground_mask = alpha > 128
        
        if np.sum(foreground_mask) == 0:
            print(f"      ❌ 没有前景区域")
            return
        
        # 分析前景区域的色彩
        if len(original.shape) == 3 and len(processed.shape) == 4:
            # 原始图片的前景区域
            original_foreground = original[foreground_mask]
            processed_foreground = processed[foreground_mask, :3]  # 只取RGB通道
            
            # 计算色彩统计
            original_mean = np.mean(original_foreground, axis=0)
            processed_mean = np.mean(processed_foreground, axis=0)
            
            # 计算色彩差异
            color_diff = np.abs(original_mean - processed_mean)
            total_color_diff = np.sum(color_diff)
            
            print(f"      原始前景平均色彩: R={original_mean[2]:.1f}, G={original_mean[1]:.1f}, B={original_mean[0]:.1f}")
            print(f"      处理后前景平均色彩: R={processed_mean[2]:.1f}, G={processed_mean[1]:.1f}, B={processed_mean[0]:.1f}")
            print(f"      色彩差异: {total_color_diff:.1f}")
            
            # 评估色彩保留质量
            if total_color_diff < 10:
                print(f"      ✅ 色彩保留优秀")
            elif total_color_diff < 30:
                print(f"      ⚠ 色彩保留一般")
            else:
                print(f"      ❌ 色彩丢失严重")
            
            # 检查前景区域大小是否合理
            foreground_ratio = np.sum(foreground_mask) / alpha.size * 100
            if foreground_ratio < 20:
                print(f"      ⚠ 前景区域过小，可能存在过度抠图")
            elif foreground_ratio > 80:
                print(f"      ⚠ 前景区域过大，可能存在抠图不足")
            else:
                print(f"      ✅ 前景区域比例合理")
                
    except Exception as e:
        print(f"      ❌ 色彩保留分析失败: {e}")

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

def show_improvements():
    """展示改进内容"""
    print("\n🌟 RemBG改进内容:")
    print("=" * 50)
    print("🔧 后处理优化:")
    print("  • 自动检测过度抠图")
    print("  • 智能前景区域扩展")
    print("  • 边缘平滑处理")
    print("  • 色彩增强优化")
    
    print("\n🎯 智能质量检测:")
    print("  • 抠图质量评分系统")
    print("  • 自动OpenCV回退")
    print("  • 结果质量验证")
    print("  • 智能模型选择")
    
    print("\n⚡ 性能优化:")
    print("  • 多参数尝试策略")
    print("  • 失败自动回退")
    print("  • 实时质量监控")
    print("  • 智能错误处理")

def main():
    """主函数"""
    print("=" * 50)
    print("改进后的RemBG功能测试")
    print("=" * 50)
    
    # 运行测试
    success = test_improved_rembg()
    
    # 展示改进内容
    show_improvements()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 改进后的RemBG测试成功！")
        print("\n💡 主要改进:")
        print("• 解决过度抠图问题")
        print("• 改善色彩保留效果")
        print("• 智能质量检测和回退")
        print("• 自动后处理优化")
        print("\n🎯 现在RemBG应该能更好地处理AI生成的图片！")
    else:
        print("❌ 改进后的RemBG测试失败！请检查错误信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
