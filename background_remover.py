#!/usr/bin/env python3
"""
Background Removal Tool - 使用AI模型识别图片主题并去除背景
支持多种AI模型：RemBG、SAM、OpenCV等
"""

import os
import sys
import pygame
import numpy as np
from PIL import Image
import io
import threading
import time

try:
    import rembg
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("RemBG not available. Install with: pip install rembg")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("OpenCV not available. Install with: pip install opencv-python")

try:
    from segment_anything import sam_model_registry, SamPredictor
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    print("SAM not available. Install with: pip install segment-anything")

class BackgroundRemover:
    """AI背景去除工具类"""
    
    def __init__(self):
        self.available_models = []
        self.current_model = None
        self.sam_predictor = None
        
        # 检查可用的模型
        self._check_available_models()
        
        # 设置默认模型
        if self.available_models:
            self.current_model = self.available_models[0]
    
    def _check_available_models(self):
        """检查可用的AI模型"""
        # 按质量优先级排序：RemBG > SAM > OpenCV
        if REMBG_AVAILABLE:
            self.available_models.append('rembg')
            print("✓ RemBG model available - 最高质量AI抠图")
        
        if SAM_AVAILABLE:
            self.available_models.append('sam')
            print("✓ SAM model available - Meta先进分割模型")
        
        if OPENCV_AVAILABLE:
            self.available_models.append('opencv')
            print("✓ OpenCV model available - 基础图像处理")
        
        if not self.available_models:
            print("⚠ No AI models available. Please install at least one:")
            print("  pip install rembg")
            print("  pip install opencv-python")
            print("  pip install segment-anything")
    
    def set_model(self, model_name):
        """设置当前使用的模型"""
        if model_name in self.available_models:
            self.current_model = model_name
            print(f"Switched to {model_name} model")
            return True
        else:
            print(f"Model {model_name} not available")
            return False
    
    def get_available_models(self):
        """获取可用的模型列表"""
        return self.available_models.copy()
    
    def remove_background_rembg(self, image_path, output_path=None):
        """使用RemBG去除背景 - 最高质量AI抠图（AI智能版）"""
        if not REMBG_AVAILABLE:
            raise ImportError("RemBG not available")
        
        try:
            print(f"📖 读取图片: {image_path}")
            # 读取图片
            with open(image_path, 'rb') as f:
                input_data = f.read()
            
            # AI智能参数选择
            print(f"🧠 开始AI智能参数分析...")
            complexity_score = self._analyze_image_complexity(image_path)
            print(f"📊 图片复杂度评分: {complexity_score:.1f}/100")
            
            # 根据复杂度选择最佳参数
            output_data = self._rembg_with_adaptive_params(input_data, complexity_score)
            
            # 后处理优化
            print(f"🔧 开始AI智能后处理优化...")
            optimized_data = self._post_process_rembg_result(output_data, image_path, complexity_score)
            
            # 保存结果
            if output_path:
                print(f"💾 保存结果到: {output_path}")
                with open(output_path, 'wb') as f:
                    f.write(optimized_data)
                
                # 验证保存的文件
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"📁 文件保存成功，大小: {file_size} bytes")
                    
                    # 验证抠图质量
                    quality_score = self._validate_rembg_quality(output_path)
                    print(f"🎯 抠图质量评分: {quality_score:.1f}/100")
                    
                    return output_path
                else:
                    print("❌ 文件保存失败")
                    return None
            else:
                # 返回PIL Image对象
                print("🖼️ 返回PIL Image对象")
                return Image.open(io.BytesIO(optimized_data))
                
        except Exception as e:
            print(f"❌ RemBG背景去除失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _analyze_image_complexity(self, image_path):
        """分析图片复杂度 - AI智能分析"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                return 50.0
            
            # 转换为灰度图进行分析
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 1. 边缘复杂度分析
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size * 100
            
            # 2. 纹理复杂度分析
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            texture_variance = np.var(laplacian)
            
            # 3. 色彩复杂度分析
            if len(image.shape) == 3:
                color_variance = np.var(image, axis=(0, 1))
                total_color_variance = np.sum(color_variance)
            else:
                total_color_variance = 0
            
            # 4. 局部方差分析（检测细节丰富度）
            local_var = cv2.GaussianBlur(gray.astype(np.float32), (15, 15), 3)
            local_variance = np.var(local_var)
            
            # 5. 梯度复杂度分析
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            avg_gradient = np.mean(gradient_magnitude)
            
            # 6. AI生成图片特征检测
            ai_features = self._detect_ai_generation_features(image)
            
            # 综合复杂度评分
            complexity_score = (
                edge_density * 0.25 +
                min(texture_variance / 1000, 25) +
                min(total_color_variance / 10000, 20) +
                min(local_variance / 100, 15) +
                min(avg_gradient / 10, 15)
            )
            
            # AI特征调整
            if ai_features['is_likely_ai_generated']:
                complexity_score *= 1.2  # AI生成的图片通常更复杂
                print(f"🎨 检测到AI生成图片特征，复杂度提升20%")
            
            return min(complexity_score, 100.0)
            
        except Exception as e:
            print(f"⚠ 复杂度分析失败: {e}")
            return 50.0
    
    def _detect_ai_generation_features(self, image):
        """检测AI生成图片的特征"""
        try:
            # 转换为RGB进行分析
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 1. 色彩过渡平滑性检测
            diff_x = np.diff(image_rgb, axis=1)
            diff_y = np.diff(image_rgb, axis=0)
            avg_diff_x = np.mean(np.abs(diff_x))
            avg_diff_y = np.mean(np.abs(diff_y))
            
            # 2. 色彩饱和度分析
            hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
            saturation = hsv[:, :, 1]
            avg_saturation = np.mean(saturation)
            
            # 3. 边缘平滑度分析
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            laplacian_variance = np.var(laplacian)
            
            # 判断是否为AI生成图片
            is_smooth = (avg_diff_x < 15 and avg_diff_y < 15)
            is_high_saturation = avg_saturation > 100
            is_smooth_edges = laplacian_variance < 5000
            
            is_likely_ai_generated = (is_smooth and is_high_saturation) or is_smooth_edges
            
            return {
                'is_likely_ai_generated': is_likely_ai_generated,
                'smoothness_score': max(0, 1 - (avg_diff_x + avg_diff_y) / 200),
                'saturation_score': avg_saturation / 255,
                'edge_smoothness': max(0, 1 - laplacian_variance / 10000)
            }
            
        except Exception as e:
            print(f"⚠ AI特征检测失败: {e}")
            return {'is_likely_ai_generated': False, 'smoothness_score': 0.5, 'saturation_score': 0.5, 'edge_smoothness': 0.5}
    
    def _rembg_with_adaptive_params(self, input_data, complexity_score):
        """使用自适应参数的RemBG抠图"""
        try:
            print(f"🎯 根据复杂度选择最佳参数...")
            
            if complexity_score > 80:
                # 极高复杂度：最保守的参数
                print(f"🔴 极高复杂度，使用最保守参数")
                output_data = rembg.remove(input_data, 
                                         alpha_matting=True,
                                         alpha_matting_foreground_threshold=250,
                                         alpha_matting_background_threshold=5,
                                         alpha_matting_erode_size=25)
            elif complexity_score > 70:
                # 高复杂度：保守参数
                print(f"🟠 高复杂度，使用保守参数")
                output_data = rembg.remove(input_data, 
                                         alpha_matting=True,
                                         alpha_matting_foreground_threshold=245,
                                         alpha_matting_background_threshold=8,
                                         alpha_matting_erode_size=20)
            elif complexity_score > 50:
                # 中等复杂度：平衡参数
                print(f"🟡 中等复杂度，使用平衡参数")
                output_data = rembg.remove(input_data, 
                                         alpha_matting=True,
                                         alpha_matting_foreground_threshold=240,
                                         alpha_matting_background_threshold=12,
                                         alpha_matting_erode_size=15)
            else:
                # 低复杂度：标准参数
                print(f"🟢 低复杂度，使用标准参数")
                output_data = rembg.remove(input_data, 
                                         alpha_matting=True,
                                         alpha_matting_foreground_threshold=235,
                                         alpha_matting_background_threshold=15,
                                         alpha_matting_erode_size=10)
            
            print(f"✅ 自适应参数AI抠图完成！")
            return output_data
            
        except Exception as e:
            print(f"⚠ 自适应参数处理失败，使用标准参数: {e}")
            # 回退到标准参数
            return rembg.remove(input_data)
    
    def _post_process_rembg_result(self, output_data, original_image_path, complexity_score):
        """后处理RemBG结果，优化抠图质量（AI智能版）"""
        try:
            # 将输出数据转换为PIL Image
            output_image = Image.open(io.BytesIO(output_data))
            
            # 转换为numpy数组
            output_array = np.array(output_image)
            
            # 检查是否有Alpha通道
            if len(output_array.shape) == 3 and output_array.shape[2] == 4:
                # 提取Alpha通道
                alpha = output_array[:, :, 3]
                
                # 检测是否过度抠图
                foreground_ratio = np.sum(alpha > 128) / alpha.size * 100
                print(f"📊 当前前景区域: {foreground_ratio:.1f}%")
                
                # 根据复杂度调整优化策略
                if foreground_ratio < 30:  # 前景区域过小，可能存在过度抠图
                    print(f"⚠ 检测到过度抠图，开始AI智能优化...")
                    
                    # 优化策略1: 智能前景扩展
                    optimized_alpha = self._expand_foreground_smart(alpha, complexity_score)
                    
                    # 优化策略2: 智能边缘优化
                    optimized_alpha = self._smooth_edges_smart(optimized_alpha, complexity_score)
                    
                    # 应用优化后的Alpha通道
                    output_array[:, :, 3] = optimized_alpha
                    
                    new_ratio = np.sum(optimized_alpha > 128) / optimized_alpha.size * 100
                    print(f"✅ AI智能优化完成，前景区域: {foreground_ratio:.1f}% → {new_ratio:.1f}%")
                
                # 优化策略3: 智能色彩增强
                output_array = self._enhance_colors_smart(output_array, complexity_score)
                
                # 优化策略4: AI细节恢复（仅对高复杂度图片）
                if complexity_score > 70:
                    output_array = self._restore_ai_details(output_array, original_image_path)
                
                # 新增：去除黑色阴影优化
                output_array = self._remove_black_shadows(output_array)
                
            # 转换回PIL Image
            optimized_image = Image.fromarray(output_array, 'RGBA')
            
            # 转换为字节数据
            output_buffer = io.BytesIO()
            optimized_image.save(output_buffer, format='PNG')
            optimized_data = output_buffer.getvalue()
            
            return optimized_data
            
        except Exception as e:
            print(f"⚠ 后处理失败，使用原始结果: {e}")
            return output_data
    
    def _expand_foreground(self, alpha):
        """扩大前景区域，解决过度抠图问题"""
        try:
            # 创建前景掩码
            foreground_mask = alpha > 128
            
            # 使用形态学膨胀操作扩大前景
            kernel = np.ones((5, 5), np.uint8)
            expanded_mask = cv2.dilate(foreground_mask.astype(np.uint8), kernel, iterations=2)
            
            # 使用高斯模糊创建平滑过渡
            expanded_mask = cv2.GaussianBlur(expanded_mask.astype(np.float32), (15, 15), 3)
            
            # 重新映射到0-255范围
            expanded_alpha = (expanded_mask * 255).astype(np.uint8)
            
            return expanded_alpha
            
        except Exception as e:
            print(f"⚠ 前景扩展失败: {e}")
            return alpha
    
    def _expand_foreground_smart(self, alpha, complexity_score):
        """智能前景扩展，根据复杂度调整策略"""
        try:
            # 创建前景掩码
            foreground_mask = alpha > 128
            
            # 根据复杂度调整扩展参数 - 微调优化版本
            if complexity_score > 80:
                # 极高复杂度：轻微扩展
                kernel_size = 3
                iterations = 1
                blur_sigma = 1
                print(f"🔴 极高复杂度，使用轻微前景扩展")
            elif complexity_score > 70:
                # 高复杂度：很轻微扩展
                kernel_size = 3
                iterations = 1
                blur_sigma = 0.8
                print(f"🟠 高复杂度，使用很轻微前景扩展")
            elif complexity_score > 50:
                # 中等复杂度：几乎不扩展
                kernel_size = 3
                iterations = 1
                blur_sigma = 0.5
                print(f"🟡 中等复杂度，几乎不扩展")
            else:
                # 低复杂度：完全不扩展
                kernel_size = 1
                iterations = 0
                blur_sigma = 0
                print(f"🟢 低复杂度，完全不扩展")
            
            # 使用形态学膨胀操作扩大前景
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            expanded_mask = cv2.dilate(foreground_mask.astype(np.uint8), kernel, iterations=iterations)
            
            # 使用高斯模糊创建平滑过渡
            expanded_mask = cv2.GaussianBlur(expanded_mask.astype(np.float32), (15, 15), blur_sigma)
            
            # 重新映射到0-255范围
            expanded_alpha = (expanded_mask * 255).astype(np.uint8)
            
            return expanded_alpha
            
        except Exception as e:
            print(f"⚠ 智能前景扩展失败: {e}")
            return alpha
    
    def _smooth_edges(self, alpha):
        """平滑边缘，改善抠图质量"""
        try:
            # 使用双边滤波保持边缘的同时平滑区域
            smoothed = cv2.bilateralFilter(alpha, 9, 75, 75)
            
            # 轻微的高斯模糊进一步平滑
            smoothed = cv2.GaussianBlur(smoothed.astype(np.float32), (5, 5), 1)
            
            return smoothed.astype(np.uint8)
            
        except Exception as e:
            print(f"⚠ 边缘平滑失败: {e}")
            return alpha
    
    def _smooth_edges_smart(self, alpha, complexity_score):
        """智能边缘平滑，根据复杂度调整策略"""
        try:
            # 根据复杂度调整边缘平滑参数 - 微调优化版本
            if complexity_score > 80:
                # 极高复杂度：很轻微边缘处理
                bilateral_d = 3
                bilateral_sigma_color = 30
                bilateral_sigma_space = 30
                gaussian_kernel = 3
                gaussian_sigma = 0.1
                print(f"🔴 极高复杂度，使用很轻微边缘平滑")
            elif complexity_score > 70:
                # 高复杂度：几乎不平滑
                bilateral_d = 3
                bilateral_sigma_color = 25
                bilateral_sigma_space = 25
                gaussian_kernel = 3
                gaussian_sigma = 0.05
                print(f"🟠 高复杂度，几乎不平滑")
            elif complexity_score > 50:
                # 中等复杂度：几乎不平滑
                bilateral_d = 3
                bilateral_sigma_color = 20
                bilateral_sigma_space = 20
                gaussian_kernel = 3
                gaussian_sigma = 0.02
                print(f"🟡 中等复杂度，几乎不平滑")
            else:
                # 低复杂度：完全不平滑
                bilateral_d = 1
                bilateral_sigma_color = 10
                bilateral_sigma_space = 10
                gaussian_kernel = 1
                gaussian_sigma = 0.01
                print(f"🟢 低复杂度，完全不平滑")
            
            # 使用双边滤波保持边缘的同时平滑区域
            smoothed = cv2.bilateralFilter(alpha, bilateral_d, bilateral_sigma_color, bilateral_sigma_space)
            
            # 轻微的高斯模糊进一步平滑
            smoothed = cv2.GaussianBlur(smoothed.astype(np.float32), (gaussian_kernel, gaussian_kernel), gaussian_sigma)
            
            return smoothed.astype(np.uint8)
            
        except Exception as e:
            print(f"⚠ 智能边缘平滑失败: {e}")
            return alpha
    
    def _enhance_colors(self, rgba_array):
        """增强色彩，改善视觉效果"""
        try:
            # 只处理RGB通道
            rgb = rgba_array[:, :, :3].astype(np.float32)
            
            # 轻微的色彩增强
            # 增加饱和度
            hsv = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.1, 0, 255)  # 增加饱和度10%
            enhanced_rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            # 应用增强后的RGB
            rgba_array[:, :, :3] = enhanced_rgb
            
            return rgba_array
            
        except Exception as e:
            print(f"⚠ 色彩增强失败: {e}")
            return rgba_array
    
    def _remove_black_shadows(self, rgba_array):
        """去除黑色阴影，优化抠图边缘 - 平衡版本"""
        try:
            # 提取Alpha通道
            alpha = rgba_array[:, :, 3]
            
            # 创建前景掩码 - 微调优化版本
            foreground_mask = alpha > 80  # 进一步提高阈值，只处理核心前景区域
            
            # 对前景区域进行黑色阴影检测和去除
            rgb = rgba_array[:, :, :3]
            
            # 检测黑色像素（RGB值都很低）- 更严格的阈值
            black_threshold = 15  # 进一步降低阈值，只处理真正的深黑色像素
            black_pixels = np.all(rgb < black_threshold, axis=2)
            
            # 只在前景区域内处理黑色像素
            black_in_foreground = black_pixels & foreground_mask
            
            if np.any(black_in_foreground):
                print(f"🔍 检测到 {np.sum(black_in_foreground)} 个黑色像素，开始精确优化...")
                
                # 方法1: 更精确的透明度调整
                rgba_array[black_in_foreground, 3] = np.clip(alpha[black_in_foreground] * 0.8, 0, 255)
                
                # 方法2: 只对真正的边缘进行极轻微修复
                edge_mask = (alpha > 80) & (alpha < 120)  # 更窄的边缘范围
                if np.any(edge_mask):
                    print(f"🔧 对 {np.sum(edge_mask)} 个边缘像素进行极轻微修复...")
                    
                    # 使用更小的邻域，减少影响范围
                    for i in range(1, rgba_array.shape[0] - 1):
                        for j in range(1, rgba_array.shape[1] - 1):
                            if edge_mask[i, j]:
                                # 获取周围3x3区域的有效像素
                                neighborhood = rgba_array[max(0, i-1):min(rgba_array.shape[0], i+2),
                                                        max(0, j-1):min(rgba_array.shape[1], j+2)]
                                valid_pixels = neighborhood[neighborhood[:, :, 3] > 180]  # 更高的透明度要求
                                
                                if len(valid_pixels) > 0:
                                    # 使用加权平均，保持原有颜色特征
                                    weights = valid_pixels[:, 3] / 255.0  # 使用透明度作为权重
                                    weighted_avg = np.average(valid_pixels[:, :3], axis=0, weights=weights)
                                    
                                    # 混合原有颜色和修复颜色，保持85%原有特征
                                    original_color = rgba_array[i, j, :3]
                                    rgba_array[i, j, :3] = (original_color * 0.85 + weighted_avg * 0.15).astype(np.uint8)
                                    rgba_array[i, j, 3] = alpha[i, j]  # 保持原有透明度
                
                print(f"✅ 精确黑色阴影优化完成")
            
            return rgba_array
            
        except Exception as e:
            print(f"⚠ 黑色阴影去除失败: {e}")
            return rgba_array
    
    def _enhance_colors_smart(self, rgba_array, complexity_score):
        """智能色彩增强，根据复杂度调整策略"""
        try:
            # 只处理RGB通道
            rgb = rgba_array[:, :, :3].astype(np.float32)
            
            # 根据复杂度调整色彩增强参数 - 微调优化版本
            if complexity_score > 80:
                # 极高复杂度：轻微色彩增强
                saturation_factor = 1.08
                brightness_factor = 1.03
                print(f"🔴 极高复杂度，使用轻微色彩增强")
            elif complexity_score > 70:
                # 高复杂度：很轻微色彩增强
                saturation_factor = 1.05
                brightness_factor = 1.02
                print(f"🟠 高复杂度，使用很轻微色彩增强")
            elif complexity_score > 50:
                # 中等复杂度：几乎不增强
                saturation_factor = 1.02
                brightness_factor = 1.01
                print(f"🟡 中等复杂度，几乎不增强")
            else:
                # 低复杂度：完全不增强
                saturation_factor = 1.0
                brightness_factor = 1.0
                print(f"🟢 低复杂度，完全不增强")
            
            # 转换为HSV
            hsv = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            
            # 增强饱和度
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_factor, 0, 255)
            
            # 增强亮度
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * brightness_factor, 0, 255)
            
            # 转换回RGB
            enhanced_rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            # 应用增强后的RGB
            rgba_array[:, :, :3] = enhanced_rgb
            
            return rgba_array
            
        except Exception as e:
            print(f"⚠ 智能色彩增强失败: {e}")
            return rgba_array
    
    def _restore_ai_details(self, rgba_array, original_image_path):
        """AI细节恢复，专门针对高复杂度图片"""
        try:
            print(f"🔍 开始AI细节恢复...")
            
            # 读取原始图片
            original = cv2.imread(original_image_path)
            if original is None:
                print("⚠ 无法读取原始图片，跳过细节恢复")
                return rgba_array
            
            # 转换为RGB
            original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
            
            # 创建细节掩码（完全不透明区域）
            alpha = rgba_array[:, :, 3]
            detail_mask = (alpha > 200).astype(np.float32)
            
            # 在完全不透明区域恢复原始细节
            for i in range(3):
                rgba_array[:, :, i] = (rgba_array[:, :, i] * (1 - detail_mask) + 
                                      original_rgb[:, :, i] * detail_mask).astype(np.uint8)
            
            print(f"✅ AI细节恢复完成")
            return rgba_array
            
        except Exception as e:
            print(f"⚠ AI细节恢复失败: {e}")
            return rgba_array
    
    def _validate_rembg_quality(self, output_path):
        """验证RemBG抠图质量"""
        try:
            # 读取处理后的图片
            processed = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            if processed is None:
                return 0
            
            if len(processed.shape) == 3 and processed.shape[2] == 4:
                alpha = processed[:, :, 3]
                
                # 计算质量指标
                foreground_ratio = np.sum(alpha > 128) / alpha.size * 100
                
                # 前景区域评分（30-70%为理想范围）
                if 30 <= foreground_ratio <= 70:
                    foreground_score = 100
                elif foreground_ratio < 30:
                    foreground_score = max(0, 100 - (30 - foreground_ratio) * 3)
                else:
                    foreground_score = max(0, 100 - (foreground_ratio - 70) * 2)
                
                # 边缘质量评分
                edge_quality = self._analyze_edge_quality(alpha)
                edge_score = edge_quality * 20  # 转换为0-100分
                
                # 综合评分
                total_score = (foreground_score * 0.6 + edge_score * 0.4)
                
                return total_score
            
            return 0
            
        except Exception as e:
            print(f"⚠ 质量验证失败: {e}")
            return 0
    
    def _analyze_edge_quality(self, alpha_mask):
        """分析边缘质量"""
        try:
            # 使用Sobel算子检测边缘
            sobel_x = cv2.Sobel(alpha_mask, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(alpha_mask, cv2.CV_64F, 0, 1, ksize=3)
            
            # 计算边缘强度
            edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            
            # 计算平均边缘强度
            avg_edge_strength = np.mean(edge_magnitude)
            
            # 转换为1-5分
            if avg_edge_strength < 10:
                return 1  # 模糊
            elif avg_edge_strength < 30:
                return 2  # 一般
            elif avg_edge_strength < 60:
                return 3  # 清晰
            elif avg_edge_strength < 100:
                return 4  # 很清晰
            else:
                return 5  # 非常清晰
                
        except Exception as e:
            return 3  # 默认中等质量
    
    def remove_background_opencv(self, image_path, output_path=None):
        """使用OpenCV进行背景去除"""
        if not OPENCV_AVAILABLE:
            raise ImportError("OpenCV not available")
        
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            # 检查文件大小
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                raise ValueError(f"图片文件为空: {image_path}")
            
            print(f"正在读取图片: {image_path} (大小: {file_size} bytes)")
            
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                # 尝试使用绝对路径
                abs_path = os.path.abspath(image_path)
                print(f"尝试使用绝对路径: {abs_path}")
                image = cv2.imread(abs_path)
                
                if image is None:
                    # 尝试使用PIL读取然后转换
                    print("OpenCV读取失败，尝试使用PIL读取...")
                    pil_image = Image.open(image_path)
                    # 转换为OpenCV格式
                    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                    print("使用PIL成功读取图片")
            
            if image is None:
                raise ValueError(f"无法读取图片: {image_path}")
            
            print(f"图片读取成功，尺寸: {image.shape}")
            
            # 转换为RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 创建掩码
            mask = self._create_mask_opencv(image_rgb)
            
            # 应用掩码
            result = self._apply_mask(image_rgb, mask)
            
            # 保存结果
            if output_path:
                # 检查结果是否有Alpha通道
                if len(result.shape) == 3 and result.shape[2] == 4:
                    print(f"检测到4通道图片，使用PIL保存RGBA")
                    # 有Alpha通道，使用PIL保存以保持透明度
                    try:
                        pil_image = Image.fromarray(result, 'RGBA')
                        pil_image.save(output_path, 'PNG')
                        print(f"✓ 使用PIL保存RGBA图片成功: {output_path}")
                        print(f"保存的图片尺寸: {result.shape}, Alpha通道范围: {np.min(result[:, :, 3])} - {np.max(result[:, :, 3])}")
                    except Exception as e:
                        print(f"❌ PIL保存失败: {e}")
                        # 备用方法：转换为BGR保存
                        result_bgr = cv2.cvtColor(result, cv2.COLOR_RGBA2BGR)
                        cv2.imwrite(output_path, result_bgr)
                        print(f"使用OpenCV备用保存")
                else:
                    print(f"检测到{len(result.shape)}通道图片，使用OpenCV保存")
                    # 没有Alpha通道，直接保存
                    cv2.imwrite(output_path, result)
                
                return output_path
            else:
                return Image.fromarray(result)
                
        except Exception as e:
            print(f"OpenCV background removal failed: {e}")
            print(f"详细错误信息: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_mask_opencv(self, image):
        """使用OpenCV创建掩码 - 改进版本"""
        try:
            # 转换为HSV色彩空间
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # 方法1: 改进的颜色阈值方法
            mask1 = self._create_color_mask(hsv)
            
            # 方法2: 边缘检测方法
            mask2 = self._create_edge_mask(image)
            
            # 方法3: 轮廓检测方法
            mask3 = self._create_contour_mask(image)
            
            # 方法4: 尝试GrabCut算法（如果图片足够大）
            mask4 = None
            if image.shape[0] > 100 and image.shape[1] > 100:
                mask4 = self._create_grabcut_mask(image)
            
            # 组合所有掩码
            combined_mask = self._combine_masks([mask1, mask2, mask3, mask4])
            
            # 后处理掩码
            final_mask = self._post_process_mask(combined_mask)
            
            return final_mask
            
        except Exception as e:
            print(f"掩码创建失败，使用备用方法: {e}")
            # 备用方法：简单的颜色阈值
            return self._create_simple_color_mask(hsv)
    
    def _create_color_mask(self, hsv):
        """创建颜色掩码 - 改进版本"""
        # 扩展的颜色范围，包括更多背景颜色
        color_ranges = [
            # 蓝色天空
            (np.array([100, 50, 50]), np.array([130, 255, 255])),
            # 浅蓝色
            (np.array([90, 30, 100]), np.array([110, 255, 255])),
            # 白色云朵
            (np.array([0, 0, 200]), np.array([180, 30, 255])),
            # 浅灰色
            (np.array([0, 0, 150]), np.array([180, 30, 200])),
            # 绿色（草地）
            (np.array([35, 50, 50]), np.array([85, 255, 255])),
            # 深蓝色
            (np.array([110, 100, 50]), np.array([130, 255, 255])),
            # 浅绿色
            (np.array([40, 30, 100]), np.array([80, 255, 255])),
        ]
        
        background_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in color_ranges:
            mask = cv2.inRange(hsv, lower, upper)
            background_mask = cv2.bitwise_or(background_mask, mask)
        
        # 反转得到前景
        foreground_mask = cv2.bitwise_not(background_mask)
        
        # 形态学操作改善掩码质量
        kernel = np.ones((3, 3), np.uint8)
        foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_CLOSE, kernel)
        foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel)
        
        return foreground_mask
    
    def _create_edge_mask(self, image):
        """创建边缘检测掩码"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 使用Canny边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 膨胀边缘
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # 填充边缘内部
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        return edges
    
    def _create_contour_mask(self, image):
        """创建轮廓检测掩码"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 自适应阈值
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 创建掩码
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        # 过滤小轮廓，保留主要物体
        min_area = (gray.shape[0] * gray.shape[1]) * 0.01  # 最小面积阈值
        for contour in contours:
            if cv2.contourArea(contour) > min_area:
                cv2.fillPoly(mask, [contour], 255)
        
        return mask
    
    def _create_grabcut_mask(self, image):
        """使用GrabCut算法创建掩码"""
        try:
            # 创建掩码
            mask = np.zeros(image.shape[:2], np.uint8)
            
            # 创建临时数组
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            
            # 定义前景矩形（图片中心区域）
            h, w = image.shape[:2]
            rect = (w//4, h//4, w//2, h//2)
            
            # 运行GrabCut
            cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
            
            # 创建掩码
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            
            return mask2 * 255
            
        except Exception as e:
            print(f"GrabCut失败: {e}")
            return None
    
    def _combine_masks(self, masks):
        """组合多个掩码 - 修复版本"""
        if not masks or all(m is None for m in masks):
            return np.zeros((100, 100), dtype=np.uint8)
        
        # 过滤None值
        valid_masks = [m for m in masks if m is not None]
        if not valid_masks:
            return np.zeros((100, 100), dtype=np.uint8)
        
        # 确保所有掩码尺寸一致
        target_shape = valid_masks[0].shape
        normalized_masks = []
        
        for mask in valid_masks:
            if mask.shape != target_shape:
                mask = cv2.resize(mask, target_shape[::-1])
            normalized_masks.append(mask)
        
        # 使用颜色掩码作为基础（第一个掩码）
        if len(normalized_masks) > 0:
            base_mask = normalized_masks[0].copy()
            print(f"使用基础掩码，非零像素: {np.sum(base_mask > 0)}")
            
            # 如果有其他掩码，尝试改进基础掩码
            if len(normalized_masks) > 1:
                # 使用边缘检测掩码来改进边界
                edge_mask = normalized_masks[1] if len(normalized_masks) > 1 else None
                if edge_mask is not None:
                    # 在边缘区域使用边缘检测结果
                    edge_region = edge_mask > 0
                    base_mask[edge_region] = np.maximum(base_mask[edge_region], edge_mask[edge_region])
                    print(f"结合边缘检测后，非零像素: {np.sum(base_mask > 0)}")
            
            return base_mask
        else:
            return np.zeros((100, 100), dtype=np.uint8)
    
    def _post_process_mask(self, mask):
        """后处理掩码"""
        # 形态学操作
        kernel = np.ones((3, 3), np.uint8)
        
        # 开运算去除小噪点
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # 闭运算填充小孔
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 高斯模糊边缘
        mask = cv2.GaussianBlur(mask, (3, 3), 0)
        
        return mask
    
    def _create_simple_color_mask(self, hsv):
        """创建简单的颜色掩码（备用方法）"""
        # 蓝色天空
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # 白色云朵
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # 合并掩码
        background_mask = cv2.bitwise_or(blue_mask, white_mask)
        
        # 反转掩码得到前景
        foreground_mask = cv2.bitwise_not(background_mask)
        
        # 形态学操作
        kernel = np.ones((5, 5), np.uint8)
        foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_CLOSE, kernel)
        foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel)
        
        return foreground_mask
    
    def _apply_mask(self, image, mask):
        """应用掩码到图片"""
        try:
            # 检查输入参数
            if image is None:
                raise ValueError("输入图片为空")
            if mask is None:
                raise ValueError("掩码为空")
            
            # 确保图片是3通道RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                pass  # 已经是3通道RGB
            elif len(image.shape) == 3 and image.shape[2] == 4:
                # 如果是4通道RGBA，转换为RGB
                image = image[:, :, :3]
            elif len(image.shape) == 2:
                # 如果是灰度图，转换为RGB
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                raise ValueError(f"不支持的图片格式: {image.shape}")
            
            # 确保掩码是2D
            if len(mask.shape) == 3:
                mask = mask[:, :, 0]  # 取第一个通道
            
            # 创建4通道RGBA图片
            result = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
            
            # 复制RGB通道
            result[:, :, :3] = image
            
            # 设置Alpha通道 - 掩码值直接作为透明度
            # 掩码值255表示完全不透明（前景），0表示完全透明（背景）
            result[:, :, 3] = mask
            
            print(f"掩码应用成功，结果图片尺寸: {result.shape}")
            print(f"Alpha通道范围: {np.min(mask)} - {np.max(mask)}")
            
            return result
            
        except Exception as e:
            print(f"应用掩码失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_background_sam(self, image_path, output_path=None, point_coords=None):
        """使用SAM模型进行背景去除"""
        if not SAM_AVAILABLE:
            raise ImportError("SAM not available")
        
        try:
            # 初始化SAM模型（这里需要下载预训练模型）
            if self.sam_predictor is None:
                print("Initializing SAM model...")
                # 这里需要设置模型路径，用户需要下载SAM模型
                sam_checkpoint = "sam_vit_h_4b8939.pth"  # 需要用户下载
                model_type = "vit_h"
                
                if not os.path.exists(sam_checkpoint):
                    print(f"SAM model not found: {sam_checkpoint}")
                    print("Please download SAM model from: https://github.com/facebookresearch/segment-anything")
                    return None
                
                sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
                self.sam_predictor = SamPredictor(sam)
            
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Cannot read image")
            
            # 设置图片
            self.sam_predictor.set_image(image)
            
            # 如果没有指定点坐标，使用图片中心
            if point_coords is None:
                h, w = image.shape[:2]
                point_coords = np.array([[w//2, h//2]])
            
            # 预测分割
            masks, scores, logits = self.sam_predictor.predict(
                point_coords=point_coords,
                point_labels=np.array([1]),  # 1表示前景
                multimask_output=True
            )
            
            # 选择最佳掩码
            best_mask_idx = np.argmax(scores)
            mask = masks[best_mask_idx]
            
            # 应用掩码
            result = self._apply_mask_sam(image, mask)
            
            # 保存结果
            if output_path:
                print(f"准备保存结果，结果形状: {result.shape}")
                
                # 检查结果是否有Alpha通道
                if len(result.shape) == 3 and result.shape[2] == 4:
                    print(f"检测到4通道图片，使用PIL保存RGBA")
                    # 有Alpha通道，使用PIL保存以保持透明度
                    try:
                        pil_image = Image.fromarray(result, 'RGBA')
                        pil_image.save(output_path, 'PNG')
                        print(f"✓ 使用PIL保存RGBA图片成功: {output_path}")
                        print(f"保存的图片尺寸: {result.shape}, Alpha通道范围: {np.min(result[:, :, 3])} - {np.max(result[:, :, 3])}")
                    except Exception as e:
                        print(f"❌ PIL保存失败: {e}")
                        # 备用方法：转换为BGR保存
                        result_bgr = cv2.cvtColor(result, cv2.COLOR_RGBA2BGR)
                        cv2.imwrite(output_path, result_bgr)
                        print(f"使用OpenCV备用保存")
                else:
                    print(f"检测到{len(result.shape)}通道图片，使用OpenCV保存")
                    # 没有Alpha通道，直接保存
                    cv2.imwrite(output_path, result)
                
                return output_path
            else:
                return Image.fromarray(result)
                
        except Exception as e:
            print(f"SAM background removal failed: {e}")
            return None
    
    def _apply_mask_sam(self, image, mask):
        """使用SAM掩码应用分割结果"""
        # 创建4通道RGBA图片
        result = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
        
        # 复制RGB通道
        result[:, :, :3] = image
        
        # 设置Alpha通道
        result[:, :, 3] = mask.astype(np.uint8) * 255
        
        return result
    
    def remove_background(self, image_path, output_path=None, model_name=None, **kwargs):
        """主要的背景去除方法 - 智能选择最佳模型（改进版）"""
        if model_name:
            self.set_model(model_name)
        
        if not self.current_model:
            raise ValueError("No AI model available")
        
        print(f"🎯 使用 {self.current_model} 模型进行背景去除...")
        
        if self.current_model == 'rembg':
            print("🚀 使用RemBG高质量AI抠图...")
            result = self.remove_background_rembg(image_path, output_path)
            
            # 智能质量检测和回退
            if result and output_path:
                quality_score = self._validate_rembg_quality(output_path)
                if quality_score < 60:  # 质量评分低于60分
                    print(f"⚠ RemBG抠图质量较低 ({quality_score:.1f}/100)，尝试OpenCV回退...")
                    
                    # 尝试OpenCV作为回退方案
                    try:
                        opencv_result = self.remove_background_opencv(image_path, output_path.replace('.png', '_opencv_fallback.png'))
                        if opencv_result:
                            opencv_quality = self._validate_opencv_quality(opencv_result)
                            print(f"🔄 OpenCV回退完成，质量评分: {opencv_quality:.1f}/100")
                            
                            # 如果OpenCV效果更好，使用OpenCV结果
                            if opencv_quality > quality_score:
                                print(f"✅ OpenCV效果更好，使用OpenCV结果")
                                # 替换原文件
                                if os.path.exists(opencv_result):
                                    os.replace(opencv_result, output_path)
                                return output_path
                            else:
                                print(f"✅ RemBG效果更好，保留RemBG结果")
                                # 清理OpenCV回退文件
                                if os.path.exists(opencv_result):
                                    os.remove(opencv_result)
                    except Exception as e:
                        print(f"⚠ OpenCV回退失败: {e}")
            
            return result
            
        elif self.current_model == 'opencv':
            print("🔧 使用OpenCV基础图像处理...")
            return self.remove_background_opencv(image_path, output_path)
        elif self.current_model == 'sam':
            print("🧠 使用SAM先进分割模型...")
            return self.remove_background_sam(image_path, output_path, **kwargs)
        else:
            raise ValueError(f"Unknown model: {self.current_model}")
    
    def _validate_opencv_quality(self, output_path):
        """验证OpenCV抠图质量"""
        try:
            # 读取处理后的图片
            processed = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
            if processed is None:
                return 0
            
            if len(processed.shape) == 3 and processed.shape[2] == 4:
                alpha = processed[:, :, 3]
                
                # 计算质量指标
                foreground_ratio = np.sum(alpha > 128) / alpha.size * 100
                
                # 前景区域评分（40-80%为理想范围，OpenCV通常更保守）
                if 40 <= foreground_ratio <= 80:
                    foreground_score = 100
                elif foreground_ratio < 40:
                    foreground_score = max(0, 100 - (40 - foreground_ratio) * 2)
                else:
                    foreground_score = max(0, 100 - (foreground_ratio - 80) * 1.5)
                
                # 边缘质量评分
                edge_quality = self._analyze_edge_quality(alpha)
                edge_score = edge_quality * 20  # 转换为0-100分
                
                # 综合评分
                total_score = (foreground_score * 0.6 + edge_score * 0.4)
                
                return total_score
            
            return 0
            
        except Exception as e:
            print(f"⚠ OpenCV质量验证失败: {e}")
            return 0
    
    def remove_background_pygame_surface(self, pygame_surface, output_path=None, model_name=None):
        """从Pygame surface去除背景"""
        # 将Pygame surface转换为PIL Image
        pil_image = self._pygame_to_pil(pygame_surface)
        
        # 保存为临时文件
        temp_path = "temp_image.png"
        pil_image.save(temp_path)
        
        try:
            # 去除背景
            result = self.remove_background(temp_path, output_path, model_name)
            return result
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def _pygame_to_pil(self, pygame_surface):
        """将Pygame surface转换为PIL Image"""
        # 获取surface数据
        string_image = pygame.image.tostring(pygame_surface, "RGBA", False)
        
        # 创建PIL Image
        pil_image = Image.frombytes("RGBA", pygame_surface.get_size(), string_image)
        
        return pil_image
    
    def _pil_to_pygame(self, pil_image):
        """将PIL Image转换为Pygame surface"""
        # 转换为RGBA模式
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        
        # 转换为Pygame surface
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        
        pygame_surface = pygame.image.fromstring(data, size, mode)
        
        return pygame_surface
    
    def auto_detect_airplane(self, image_path):
        """自动检测图片中的飞机"""
        # 这里可以实现更复杂的飞机检测逻辑
        # 目前返回图片中心点作为默认值
        try:
            image = cv2.imread(image_path)
            if image is not None:
                h, w = image.shape[:2]
                return np.array([[w//2, h//2]])
        except:
            pass
        
        return None

# 使用示例
if __name__ == "__main__":
    # 创建背景去除器
    remover = BackgroundRemover()
    
    # 检查可用模型
    print("Available models:", remover.get_available_models())
    
    # 测试背景去除
    test_image = "test_airplane.png"
    if os.path.exists(test_image):
        print(f"Testing background removal on {test_image}")
        
        # 使用默认模型
        result = remover.remove_background(test_image)
        if result:
            print("Background removal successful!")
            if isinstance(result, str):
                print(f"Result saved to: {result}")
            else:
                print("Result returned as PIL Image")
        else:
            print("Background removal failed")
    else:
        print(f"Test image {test_image} not found")
