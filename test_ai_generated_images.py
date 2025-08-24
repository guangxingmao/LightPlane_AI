#!/usr/bin/env python3
"""
测试AI生成图片的抠图效果
"""

import os
import cv2
import numpy as np
from PIL import Image
import time

def test_ai_generated_images():
    """测试AI生成图片的抠图效果"""
    print("🧪 测试AI生成图片的抠图效果...")
    
    try:
        from background_remover import BackgroundRemover
        
        # 创建背景去除器
        remover = BackgroundRemover()
        print(f"✓ 背景去除器创建成功")
        print(f"📋 可用模型: {remover.get_available_models()}")
        
        # 查找AI生成的图片或类似的复杂图片
        test_images = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # 优先选择可能更复杂的图片
                    if not file.startswith('.') and 'test' not in file.lower() and 'debug' not in file.lower():
                        test_images.append(os.path.join(root, file))
                        if len(test_images) >= 5:
                            break
            if len(test_images) >= 5:
                break
        
        if not test_images:
            print("❌ 未找到测试图片")
            return False
        
        print(f"✓ 找到测试图片: {len(test_images)} 张")
        
        # 测试每张图片
        for i, test_image in enumerate(test_images[:3]):  # 测试前3张
            print(f"\n🔍 测试图片 {i+1}: {test_image}")
            
            # 分析原始图片
            analyze_original_image(test_image)
            
            # 测试不同模型的抠图效果
            test_different_models(remover, test_image, i)
        
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
            
            # 检测是否为AI生成图片的特征
            detect_ai_generated_features(image_rgb)
        
    except Exception as e:
        print(f"❌ 分析原始图片失败: {e}")

def detect_ai_generated_features(image_rgb):
    """检测AI生成图片的特征"""
    try:
        # 检测色彩过渡的平滑性
        # AI生成的图片通常有更平滑的色彩过渡
        
        # 计算相邻像素的差异
        diff_x = np.diff(image_rgb, axis=1)
        diff_y = np.diff(image_rgb, axis=0)
        
        # 计算平均差异
        avg_diff_x = np.mean(np.abs(diff_x))
        avg_diff_y = np.mean(np.abs(diff_y))
        
        print(f"  色彩过渡分析:")
        print(f"    水平方向平均差异: {avg_diff_x:.1f}")
        print(f"    垂直方向平均差异: {avg_diff_y:.1f}")
        
        # 判断是否为AI生成图片
        if avg_diff_x < 15 and avg_diff_y < 15:
            print(f"    🎨 可能是AI生成的图片 (色彩过渡平滑)")
        else:
            print(f"    📷 可能是真实拍摄的图片 (色彩过渡明显)")
            
    except Exception as e:
        print(f"    ❌ AI特征检测失败: {e}")

def test_different_models(remover, test_image, index):
    """测试不同模型的抠图效果"""
    print(f"\n🔬 测试不同模型的抠图效果...")
    
    models_to_test = ['rembg', 'opencv']
    available_models = remover.get_available_models()
    
    for model in models_to_test:
        if model in available_models:
            print(f"\n🎯 测试模型: {model}")
            
            # 设置模型
            remover.set_model(model)
            
            # 生成输出文件名
            output_path = f"test_{model}_{index+1}_{os.path.basename(test_image)}"
            
            try:
                start_time = time.time()
                
                # 去除背景
                result = remover.remove_background(test_image, output_path)
                
                if result:
                    processing_time = time.time() - start_time
                    print(f"  ✅ 抠图成功！耗时: {processing_time:.2f}秒")
                    
                    # 分析结果
                    analyze_result_quality(test_image, output_path, model)
                    
                    # 清理测试文件
                    try:
                        os.remove(output_path)
                        print("  ✓ 测试文件已清理")
                    except:
                        pass
                        
                else:
                    print(f"  ❌ 抠图失败")
                    
            except Exception as e:
                print(f"  ❌ 抠图过程中发生错误: {e}")
        else:
            print(f"⚠ 模型 {model} 不可用")

def analyze_result_quality(original_path, processed_path, model_name):
    """分析抠图结果的质量"""
    try:
        print(f"  🔍 结果质量分析:")
        
        # 读取原始图片
        original = cv2.imread(original_path)
        if original is None:
            print("    ❌ 无法读取原始图片")
            return
        
        # 读取处理后的图片
        processed = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
        if processed is None:
            print("    ❌ 无法读取处理后的图片")
            return
        
        # 基本信息对比
        original_size = original.shape[:2]
        processed_size = processed.shape[:2]
        file_size = os.path.getsize(processed_path)
        
        print(f"    处理后文件大小: {file_size} bytes")
        
        # 检查透明通道
        if len(processed.shape) == 3 and processed.shape[2] == 4:
            print(f"    ✅ 成功生成RGBA透明图片")
            
            # 提取Alpha通道
            alpha = processed[:, :, 3]
            
            # 计算透明区域比例
            transparent_pixels = np.sum(alpha < 128)
            total_pixels = alpha.shape[0] * alpha.shape[1]
            transparent_ratio = transparent_pixels / total_pixels * 100
            
            print(f"    透明区域比例: {transparent_ratio:.1f}%")
            
            # 分析前景区域
            foreground_pixels = np.sum(alpha > 128)
            foreground_ratio = foreground_pixels / total_pixels * 100
            print(f"    前景区域比例: {foreground_ratio:.1f}%")
            
            # 分析色彩保留情况
            analyze_color_preservation(original, processed, alpha, model_name)
            
        else:
            print(f"    ⚠ 处理后图片没有透明通道")
            
    except Exception as e:
        print(f"    ❌ 结果质量分析失败: {e}")

def analyze_color_preservation(original, processed, alpha, model_name):
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
            
            # 模型特定的分析
            if model_name == 'rembg':
                analyze_rembg_specific_issues(original, processed, alpha)
            elif model_name == 'opencv':
                analyze_opencv_specific_issues(original, processed, alpha)
                
    except Exception as e:
        print(f"      ❌ 色彩保留分析失败: {e}")

def analyze_rembg_specific_issues(original, processed, alpha):
    """分析RemBG特定的问题"""
    try:
        print(f"      🔍 RemBG特定分析:")
        
        # 检测边缘过度抠图问题
        # 使用形态学操作检测边缘
        kernel = np.ones((3, 3), np.uint8)
        edge_mask = cv2.morphologyEx(alpha, cv2.MORPH_GRADIENT, kernel)
        
        # 计算边缘区域的色彩变化
        edge_pixels = edge_mask > 0
        if np.sum(edge_pixels) > 0:
            edge_original = original[edge_pixels]
            edge_processed = processed[edge_pixels, :3]
            
            edge_color_diff = np.mean(np.abs(edge_original - edge_processed))
            print(f"        边缘区域色彩差异: {edge_color_diff:.1f}")
            
            if edge_color_diff > 50:
                print(f"        ⚠ 边缘区域可能存在过度抠图")
        
        # 检测前景区域是否过小
        foreground_ratio = np.sum(alpha > 128) / alpha.size * 100
        if foreground_ratio < 20:
            print(f"        ⚠ 前景区域过小，可能存在过度抠图")
        elif foreground_ratio > 80:
            print(f"        ⚠ 前景区域过大，可能存在抠图不足")
        else:
            print(f"        ✅ 前景区域比例合理")
            
    except Exception as e:
        print(f"        ❌ RemBG特定分析失败: {e}")

def analyze_opencv_specific_issues(original, processed, alpha):
    """分析OpenCV特定的问题"""
    try:
        print(f"      🔍 OpenCV特定分析:")
        
        # 检测颜色阈值问题
        # OpenCV可能因为颜色阈值设置不当导致问题
        
        # 检查掩码的连续性
        kernel = np.ones((3, 3), np.uint8)
        closed_mask = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)
        
        # 计算掩码的连续性
        continuity_score = np.sum(closed_mask == alpha) / alpha.size * 100
        print(f"        掩码连续性: {continuity_score:.1f}%")
        
        if continuity_score < 90:
            print(f"        ⚠ 掩码可能存在断裂或不连续")
        
        # 检查边缘质量
        edge_quality = analyze_edge_quality(alpha)
        print(f"        边缘质量: {edge_quality}")
        
    except Exception as e:
        print(f"        ❌ OpenCV特定分析失败: {e}")

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
    print("AI生成图片抠图效果测试")
    print("=" * 50)
    
    success = test_ai_generated_images()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！")
        print("\n💡 问题分析:")
        print("• 如果RemBG抠图后色彩丢失严重，说明存在过度抠图问题")
        print("• 如果前景区域过小，可能需要调整抠图参数")
        print("• 如果边缘质量差，可能需要后处理优化")
    else:
        print("❌ 测试失败！请检查错误信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
