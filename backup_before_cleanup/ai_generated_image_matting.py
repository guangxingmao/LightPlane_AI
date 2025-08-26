#!/usr/bin/env python3
"""
AI生成图片专用抠图解决方案
专门解决复杂AI生成图片抠图效果不好的问题
"""

import os
import cv2
import numpy as np
from PIL import Image
import time
import io

class AIGeneratedImageMatting:
    """AI生成图片专用抠图解决方案"""
    
    def __init__(self):
        self.available_methods = self._check_available_methods()
        print("🎨 AI生成图片专用抠图器初始化完成")
    
    def _check_available_methods(self):
        """检查可用方法"""
        methods = {}
        
        try:
            import rembg
            methods['rembg'] = True
            print("✅ RemBG可用 - 高质量AI抠图")
        except:
            methods['rembg'] = False
            print("❌ RemBG不可用")
        
        methods['opencv'] = True
        print("✅ OpenCV可用 - 基础图像处理")
        
        return methods
    
    def process_ai_generated_image(self, image_path, output_path, method='auto'):
        """处理AI生成的图片"""
        print(f"🎨 开始处理AI生成图片: {os.path.basename(image_path)}")
        
        # 分析AI生成图片的特征
        ai_features = self._analyze_ai_generated_features(image_path)
        print(f"📊 AI图片特征分析:")
        print(f"  复杂度评分: {ai_features['complexity']:.1f}/100")
        print(f"  色彩丰富度: {ai_features['color_richness']:.1f}")
        print(f"  边缘复杂度: {ai_features['edge_complexity']:.1f}")
        print(f"  纹理复杂度: {ai_features['texture_complexity']:.1f}")
        
        # 根据特征选择最佳方法
        if method == 'auto':
            method = self._select_best_method_for_ai(ai_features)
        
        print(f"🎯 选择抠图方法: {method}")
        
        # 执行抠图
        result = self._execute_ai_matting(method, image_path, ai_features)
        
        if result is not None:
            # AI专用后处理
            final_result = self._ai_specific_postprocess(result, image_path, ai_features)
            
            # 保存结果
            if self._save_result(final_result, output_path):
                print(f"✅ AI生成图片抠图完成: {output_path}")
                return output_path
        
        return None
    
    def _analyze_ai_generated_features(self, image_path):
        """分析AI生成图片的特征"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return self._default_ai_features()
            
            # 转换为RGB进行分析
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 1. 复杂度分析
            complexity = self._calculate_complexity(image_rgb, gray)
            
            # 2. 色彩丰富度
            color_richness = self._calculate_color_richness(image_rgb)
            
            # 3. 边缘复杂度
            edge_complexity = self._calculate_edge_complexity(gray)
            
            # 4. 纹理复杂度
            texture_complexity = self._calculate_texture_complexity(gray)
            
            # 5. AI生成图片特征检测
            ai_indicators = self._detect_ai_generation_indicators(image_rgb)
            
            return {
                'complexity': complexity,
                'color_richness': color_richness,
                'edge_complexity': edge_complexity,
                'texture_complexity': texture_complexity,
                'ai_indicators': ai_indicators,
                'image_size': image.shape[:2]
            }
            
        except Exception as e:
            print(f"⚠ AI特征分析失败: {e}")
            return self._default_ai_features()
    
    def _default_ai_features(self):
        """默认AI特征"""
        return {
            'complexity': 50.0,
            'color_richness': 50.0,
            'edge_complexity': 50.0,
            'texture_complexity': 50.0,
            'ai_indicators': {'smoothness': 0.5, 'artifacts': 0.5},
            'image_size': (100, 100)
        }
    
    def _calculate_complexity(self, image_rgb, gray):
        """计算图片复杂度"""
        try:
            # 边缘密度
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size * 100
            
            # 拉普拉斯方差
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            laplacian_variance = np.var(laplacian)
            
            # 局部方差
            local_var = cv2.GaussianBlur(gray.astype(np.float32), (15, 15), 3)
            local_variance = np.var(local_var)
            
            # 综合复杂度
            complexity = (
                edge_density * 0.3 +
                min(laplacian_variance / 1000, 30) +
                min(local_variance / 100, 40)
            )
            
            return min(complexity, 100.0)
            
        except Exception as e:
            print(f"⚠ 复杂度计算失败: {e}")
            return 50.0
    
    def _calculate_color_richness(self, image_rgb):
        """计算色彩丰富度"""
        try:
            # 计算每个通道的方差
            channel_variances = np.var(image_rgb, axis=(0, 1))
            total_variance = np.sum(channel_variances)
            
            # 计算色彩饱和度
            hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
            saturation = hsv[:, :, 1]
            avg_saturation = np.mean(saturation)
            
            # 综合色彩丰富度
            color_richness = (total_variance / 10000 + avg_saturation / 255) * 50
            
            return min(color_richness, 100.0)
            
        except Exception as e:
            print(f"⚠ 色彩丰富度计算失败: {e}")
            return 50.0
    
    def _calculate_edge_complexity(self, gray):
        """计算边缘复杂度"""
        try:
            # 多尺度边缘检测
            edges1 = cv2.Canny(gray, 30, 100)
            edges2 = cv2.Canny(gray, 50, 150)
            edges3 = cv2.Canny(gray, 70, 200)
            
            # 组合边缘
            combined_edges = cv2.bitwise_or(edges1, edges2)
            combined_edges = cv2.bitwise_or(combined_edges, edges3)
            
            # 计算边缘密度和复杂度
            edge_density = np.sum(combined_edges > 0) / combined_edges.size * 100
            
            # 边缘强度
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            avg_edge_strength = np.mean(edge_magnitude)
            
            # 综合边缘复杂度
            edge_complexity = edge_density * 0.7 + min(avg_edge_strength / 10, 30)
            
            return min(edge_complexity, 100.0)
            
        except Exception as e:
            print(f"⚠ 边缘复杂度计算失败: {e}")
            return 50.0
    
    def _calculate_texture_complexity(self, gray):
        """计算纹理复杂度"""
        try:
            # 局部方差
            local_var = cv2.GaussianBlur(gray.astype(np.float32), (15, 15), 3)
            local_variance = np.var(local_var)
            
            # 梯度方差
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_variance = np.var(grad_x) + np.var(grad_y)
            
            # 纹理复杂度
            texture_complexity = min(local_variance / 100, 50) + min(gradient_variance / 1000, 50)
            
            return texture_complexity
            
        except Exception as e:
            print(f"⚠ 纹理复杂度计算失败: {e}")
            return 50.0
    
    def _detect_ai_generation_indicators(self, image_rgb):
        """检测AI生成图片的指标"""
        try:
            # 1. 色彩过渡平滑性（AI生成的图片通常更平滑）
            diff_x = np.diff(image_rgb, axis=1)
            diff_y = np.diff(image_rgb, axis=0)
            avg_diff_x = np.mean(np.abs(diff_x))
            avg_diff_y = np.mean(np.abs(diff_y))
            
            # 平滑度评分（差异越小越平滑）
            smoothness = max(0, 1 - (avg_diff_x + avg_diff_y) / 200)
            
            # 2. 检测可能的AI生成伪影
            # 使用拉普拉斯算子检测过度平滑区域
            gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            laplacian_variance = np.var(laplacian)
            
            # 伪影检测（方差过低可能表示过度平滑）
            artifacts = max(0, 1 - laplacian_variance / 10000)
            
            return {
                'smoothness': smoothness,
                'artifacts': artifacts,
                'avg_diff_x': avg_diff_x,
                'avg_diff_y': avg_diff_y,
                'laplacian_variance': laplacian_variance
            }
            
        except Exception as e:
            print(f"⚠ AI指标检测失败: {e}")
            return {'smoothness': 0.5, 'artifacts': 0.5}
    
    def _select_best_method_for_ai(self, ai_features):
        """为AI生成图片选择最佳抠图方法"""
        complexity = ai_features['complexity']
        color_richness = ai_features['color_richness']
        edge_complexity = ai_features['edge_complexity']
        ai_indicators = ai_features['ai_indicators']
        
        # 决策逻辑
        if complexity > 80:
            # 极高复杂度：优先使用RemBG
            if self.available_methods.get('rembg'):
                return 'rembg_aggressive'
            else:
                return 'opencv_aggressive'
        
        elif complexity > 60:
            # 高复杂度：使用RemBG + 保守参数
            if self.available_methods.get('rembg'):
                return 'rembg_conservative'
            else:
                return 'opencv_advanced'
        
        elif complexity > 40:
            # 中等复杂度：平衡方法
            if self.available_methods.get('rembg'):
                return 'rembg_balanced'
            else:
                return 'opencv_balanced'
        
        else:
            # 低复杂度：简单方法
            return 'opencv_simple'
    
    def _execute_ai_matting(self, method, image_path, ai_features):
        """执行AI抠图"""
        try:
            if method.startswith('rembg'):
                return self._rembg_ai_matting(method, image_path, ai_features)
            elif method.startswith('opencv'):
                return self._opencv_ai_matting(method, image_path, ai_features)
            else:
                print(f"❌ 未知的抠图方法: {method}")
                return None
                
        except Exception as e:
            print(f"❌ AI抠图执行失败: {e}")
            return None
    
    def _rembg_ai_matting(self, method, image_path, ai_features):
        """RemBG AI抠图"""
        try:
            if not self.available_methods.get('rembg'):
                print("❌ RemBG不可用")
                return None
            
            import rembg
            
            print("🚀 使用RemBG AI抠图...")
            with open(image_path, 'rb') as f:
                input_data = f.read()
            
            # 根据方法选择参数
            if method == 'rembg_aggressive':
                # 激进参数：适合极高复杂度
                output_data = rembg.remove(input_data, alpha_matting=True, 
                                         alpha_matting_foreground_threshold=250,
                                         alpha_matting_background_threshold=5,
                                         alpha_matting_erode_size=20)
            elif method == 'rembg_conservative':
                # 保守参数：适合高复杂度
                output_data = rembg.remove(input_data, alpha_matting=True, 
                                         alpha_matting_foreground_threshold=240,
                                         alpha_matting_background_threshold=10,
                                         alpha_matting_erode_size=15)
            else:
                # 平衡参数：默认
                output_data = rembg.remove(input_data, alpha_matting=True, 
                                         alpha_matting_foreground_threshold=235,
                                         alpha_matting_background_threshold=15,
                                         alpha_matting_erode_size=10)
            
            # 转换为numpy数组
            output_image = Image.open(io.BytesIO(output_data))
            result = np.array(output_image)
            
            return result
            
        except Exception as e:
            print(f"❌ RemBG AI抠图失败: {e}")
            return None
    
    def _opencv_ai_matting(self, method, image_path, ai_features):
        """OpenCV AI抠图"""
        try:
            print(f"🔧 使用OpenCV AI抠图: {method}")
            
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # 根据方法选择策略
            if method == 'opencv_aggressive':
                # 激进策略：适合极高复杂度
                mask = self._create_aggressive_opencv_mask(image, ai_features)
            elif method == 'opencv_advanced':
                # 高级策略：适合高复杂度
                mask = self._create_advanced_opencv_mask(image, ai_features)
            elif method == 'opencv_balanced':
                # 平衡策略：适合中等复杂度
                mask = self._create_balanced_opencv_mask(image, ai_features)
            else:
                # 简单策略：适合低复杂度
                mask = self._create_simple_opencv_mask(image, ai_features)
            
            # 应用掩码
            result = self._apply_mask_to_image(image, mask)
            
            return result
            
        except Exception as e:
            print(f"❌ OpenCV AI抠图失败: {e}")
            return None
    
    def _create_aggressive_opencv_mask(self, image, ai_features):
        """创建激进的OpenCV掩码"""
        try:
            # 多策略组合
            masks = []
            
            # 1. 自适应颜色阈值
            color_mask = self._create_ai_adaptive_color_mask(image, ai_features, sensitivity=0.9)
            if color_mask is not None:
                masks.append(color_mask)
            
            # 2. 多尺度边缘检测
            edge_mask = self._create_ai_edge_mask(image, ai_features, scale_factor=1.5)
            if edge_mask is not None:
                masks.append(edge_mask)
            
            # 3. 纹理分析
            texture_mask = self._create_ai_texture_mask(image, ai_features, sensitivity=0.8)
            if texture_mask is not None:
                masks.append(texture_mask)
            
            # 4. 区域生长
            region_mask = self._create_ai_region_growing_mask(image, ai_features, seed_points=10)
            if region_mask is not None:
                masks.append(region_mask)
            
            # 智能组合
            if masks:
                final_mask = self._intelligent_ai_mask_combination(masks, ai_features)
            else:
                final_mask = self._create_fallback_mask(image)
            
            return final_mask
            
        except Exception as e:
            print(f"⚠ 激进掩码创建失败: {e}")
            return self._create_fallback_mask(image)
    
    def _create_ai_adaptive_color_mask(self, image, ai_features, sensitivity=0.8):
        """创建AI自适应的颜色掩码"""
        try:
            # 转换为HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 根据AI特征调整参数
            complexity = ai_features['complexity']
            color_richness = ai_features['color_richness']
            
            # 动态调整敏感度
            if complexity > 70:
                sensitivity *= 1.2  # 高复杂度增加敏感度
            if color_richness > 70:
                sensitivity *= 0.9  # 高色彩丰富度降低敏感度
            
            # 计算统计信息
            h_mean, s_mean, v_mean = np.mean(hsv, axis=(0, 1))
            h_std, s_std, v_std = np.std(hsv, axis=(0, 1))
            
            # 自适应阈值
            h_lower = max(0, int(h_mean - h_std * sensitivity))
            h_upper = min(179, int(h_mean + h_std * sensitivity))
            s_lower = max(0, int(s_mean - s_std * sensitivity))
            s_upper = min(255, int(s_mean + s_std * sensitivity))
            v_lower = max(0, int(v_mean - v_std * sensitivity))
            v_upper = min(255, int(v_mean + v_std * sensitivity))
            
            # 创建掩码
            lower_bound = np.array([h_lower, s_lower, v_lower], dtype=np.uint8)
            upper_bound = np.array([h_upper, s_upper, v_upper], dtype=np.uint8)
            
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            
            return mask
            
        except Exception as e:
            print(f"⚠ AI自适应颜色掩码失败: {e}")
            return None
    
    def _create_ai_edge_mask(self, image, ai_features, scale_factor=1.0):
        """创建AI自适应的边缘掩码"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 根据AI特征调整参数
            edge_complexity = ai_features['edge_complexity']
            
            # 动态调整边缘检测参数
            if edge_complexity > 70:
                # 高边缘复杂度：使用更多尺度
                edges1 = cv2.Canny(gray, 20, 80)
                edges2 = cv2.Canny(gray, 40, 120)
                edges3 = cv2.Canny(gray, 60, 160)
                edges4 = cv2.Canny(gray, 80, 200)
                
                combined = cv2.bitwise_or(edges1, edges2)
                combined = cv2.bitwise_or(combined, edges3)
                combined = cv2.bitwise_or(combined, edges4)
            else:
                # 标准多尺度
                edges1 = cv2.Canny(gray, 30, 100)
                edges2 = cv2.Canny(gray, 50, 150)
                edges3 = cv2.Canny(gray, 70, 200)
                
                combined = cv2.bitwise_or(edges1, edges2)
                combined = cv2.bitwise_or(combined, edges3)
            
            # 膨胀和填充
            kernel_size = max(3, int(5 * scale_factor))
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            dilated = cv2.dilate(combined, kernel, iterations=2)
            
            # 填充轮廓
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            mask = np.zeros_like(gray)
            if contours:
                cv2.fillPoly(mask, contours, 255)
            
            return mask
            
        except Exception as e:
            print(f"⚠ AI边缘掩码失败: {e}")
            return None
    
    def _create_ai_texture_mask(self, image, ai_features, sensitivity=0.7):
        """创建AI自适应的纹理掩码"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 根据AI特征调整参数
            texture_complexity = ai_features['texture_complexity']
            
            # 动态调整纹理检测
            if texture_complexity > 70:
                # 高纹理复杂度：使用更精细的分析
                kernel_size = 11
                blur_sigma = 2
            else:
                # 标准参数
                kernel_size = 15
                blur_sigma = 3
            
            # 计算局部方差
            local_var = cv2.GaussianBlur(gray.astype(np.float32), (kernel_size, kernel_size), blur_sigma)
            local_variance = np.var(local_var)
            
            # 创建纹理掩码
            texture_threshold = local_variance * sensitivity
            texture_mask = (local_variance > texture_threshold).astype(np.uint8) * 255
            
            return texture_mask
            
        except Exception as e:
            print(f"⚠ AI纹理掩码失败: {e}")
            return None
    
    def _create_ai_region_growing_mask(self, image, ai_features, seed_points=5):
        """创建AI自适应的区域生长掩码"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 根据AI特征调整参数
            complexity = ai_features['complexity']
            
            # 动态调整区域生长参数
            if complexity > 70:
                threshold = 15  # 高复杂度使用更严格的阈值
                seed_points = max(seed_points, 15)
            else:
                threshold = 25  # 低复杂度使用更宽松的阈值
                seed_points = max(seed_points, 5)
            
            # 选择种子点
            height, width = gray.shape
            seeds = []
            for _ in range(seed_points):
                x = np.random.randint(width // 4, 3 * width // 4)
                y = np.random.randint(height // 4, 3 * height // 4)
                seeds.append((x, y))
            
            # 区域生长
            mask = np.zeros_like(gray)
            for seed_x, seed_y in seeds:
                region = self._grow_ai_region(gray, seed_x, seed_y, threshold)
                mask = cv2.bitwise_or(mask, region)
            
            return mask
            
        except Exception as e:
            print(f"⚠ AI区域生长掩码失败: {e}")
            return None
    
    def _grow_ai_region(self, gray, start_x, start_y, threshold):
        """AI区域生长算法"""
        try:
            height, width = gray.shape
            mask = np.zeros_like(gray)
            
            # 种子点
            seed_value = gray[start_y, start_x]
            stack = [(start_x, start_y)]
            mask[start_y, start_x] = 255
            
            # 8邻域
            neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            
            while stack:
                x, y = stack.pop()
                
                for dx, dy in neighbors:
                    nx, ny = x + dx, y + dy
                    
                    if (0 <= nx < width and 0 <= ny < height and 
                        mask[ny, nx] == 0 and 
                        abs(int(gray[ny, nx]) - int(seed_value)) <= threshold):
                        
                        mask[ny, nx] = 255
                        stack.append((nx, ny))
            
            return mask
            
        except Exception as e:
            return np.zeros_like(gray)
    
    def _intelligent_ai_mask_combination(self, masks, ai_features):
        """智能AI掩码组合"""
        try:
            if not masks:
                return np.ones((100, 100), dtype=np.uint8) * 255
            
            # 过滤有效掩码
            valid_masks = [m for m in masks if m is not None]
            if not valid_masks:
                return np.ones((100, 100), dtype=np.uint8) * 255
            
            # 根据AI特征调整权重
            complexity = ai_features['complexity']
            
            if complexity > 70:
                # 高复杂度：颜色掩码权重更高
                weights = [0.5, 0.3, 0.15, 0.05]
            elif complexity > 50:
                # 中等复杂度：平衡权重
                weights = [0.4, 0.3, 0.2, 0.1]
            else:
                # 低复杂度：边缘掩码权重更高
                weights = [0.3, 0.4, 0.2, 0.1]
            
            # 确保权重数量匹配
            weights = weights[:len(valid_masks)]
            weights = np.array(weights)
            weights = weights / np.sum(weights)
            
            # 加权组合
            combined_mask = np.zeros_like(valid_masks[0], dtype=np.float32)
            for mask, weight in zip(valid_masks, weights):
                combined_mask += mask.astype(np.float32) * weight
            
            # 转换为二值掩码
            final_mask = (combined_mask > 127).astype(np.uint8) * 255
            
            return final_mask
            
        except Exception as e:
            print(f"⚠ AI掩码组合失败: {e}")
            return masks[0] if masks and masks[0] is not None else np.ones((100, 100), dtype=np.uint8) * 255
    
    def _create_fallback_mask(self, image):
        """创建回退掩码"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 使用Otsu自适应阈值
            _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return mask
            
        except Exception as e:
            print(f"⚠ 回退掩码失败: {e}")
            return np.ones(image.shape[:2], dtype=np.uint8) * 255
    
    def _apply_mask_to_image(self, image, mask):
        """将掩码应用到图片"""
        try:
            # 确保掩码有效
            if mask is None:
                print("⚠ 掩码无效，使用全前景")
                mask = np.ones(image.shape[:2], dtype=np.uint8) * 255
            
            # 确保尺寸一致
            if mask.shape != image.shape[:2]:
                mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
            
            # 创建RGBA结果
            result = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
            result[:, :, :3] = image
            result[:, :, 3] = mask
            
            return result
            
        except Exception as e:
            print(f"⚠ 掩码应用失败: {e}")
            return image
    
    def _ai_specific_postprocess(self, result, original_path, ai_features):
        """AI专用后处理"""
        try:
            print("🔧 开始AI专用后处理...")
            
            if len(result.shape) != 3 or result.shape[2] != 4:
                return result
            
            alpha = result[:, :, 3]
            
            # 1. AI特征感知的前景扩展
            foreground_ratio = np.sum(alpha > 128) / alpha.size * 100
            if foreground_ratio < 30:
                print(f"⚠ 检测到过度抠图（前景区域: {foreground_ratio:.1f}%），开始AI智能扩展...")
                alpha = self._ai_smart_foreground_expansion(alpha, ai_features)
                result[:, :, 3] = alpha
                new_ratio = np.sum(alpha > 128) / alpha.size * 100
                print(f"✅ AI智能扩展完成，新前景区域: {new_ratio:.1f}%")
            
            # 2. AI感知的边缘优化
            alpha = self._ai_edge_optimization(alpha, ai_features)
            result[:, :, 3] = alpha
            
            # 3. AI色彩增强
            result = self._ai_color_enhancement(result, ai_features)
            
            # 4. AI细节恢复
            if ai_features['complexity'] > 60:
                result = self._ai_detail_restoration(result, original_path, ai_features)
            
            print("✅ AI专用后处理完成")
            return result
            
        except Exception as e:
            print(f"⚠ AI后处理失败: {e}")
            return result
    
    def _ai_smart_foreground_expansion(self, alpha, ai_features):
        """AI智能前景扩展"""
        try:
            # 前景掩码
            foreground = alpha > 128
            
            # 根据AI特征调整扩展参数
            complexity = ai_features['complexity']
            
            if complexity > 70:
                # 高复杂度：更激进的扩展
                kernel_size = 9
                iterations = 3
                blur_sigma = 4
            elif complexity > 50:
                # 中等复杂度：平衡扩展
                kernel_size = 7
                iterations = 2
                blur_sigma = 3
            else:
                # 低复杂度：保守扩展
                kernel_size = 5
                iterations = 1
                blur_sigma = 2
            
            # 形态学膨胀
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            expanded = cv2.dilate(foreground.astype(np.uint8), kernel, iterations=iterations)
            
            # 高斯模糊创建平滑过渡
            expanded = cv2.GaussianBlur(expanded.astype(np.float32), (15, 15), blur_sigma)
            
            # 重新映射到0-255
            expanded_alpha = (expanded * 255).astype(np.uint8)
            
            return expanded_alpha
            
        except Exception as e:
            print(f"⚠ AI智能前景扩展失败: {e}")
            return alpha
    
    def _ai_edge_optimization(self, alpha, ai_features):
        """AI感知的边缘优化"""
        try:
            # 根据AI特征调整边缘优化参数
            edge_complexity = ai_features['edge_complexity']
            
            if edge_complexity > 70:
                # 高边缘复杂度：更精细的优化
                bilateral_d = 9
                bilateral_sigma_color = 75
                bilateral_sigma_space = 75
                gaussian_kernel = 3
                gaussian_sigma = 0.5
            else:
                # 标准参数
                bilateral_d = 9
                bilateral_sigma_color = 75
                bilateral_sigma_space = 75
                gaussian_kernel = 3
                gaussian_sigma = 0.5
            
            # 双边滤波保持边缘
            optimized = cv2.bilateralFilter(alpha, bilateral_d, bilateral_sigma_color, bilateral_sigma_space)
            
            # 轻微高斯模糊
            optimized = cv2.GaussianBlur(optimized.astype(np.float32), (gaussian_kernel, gaussian_kernel), gaussian_sigma)
            
            return optimized.astype(np.uint8)
            
        except Exception as e:
            print(f"⚠ AI边缘优化失败: {e}")
            return alpha
    
    def _ai_color_enhancement(self, result, ai_features):
        """AI色彩增强"""
        try:
            # 根据AI特征调整色彩增强参数
            color_richness = ai_features['color_richness']
            ai_indicators = ai_features['ai_indicators']
            
            # 动态调整增强强度
            if color_richness > 70:
                saturation_factor = 1.3  # 高色彩丰富度：更强增强
                brightness_factor = 1.15
            elif color_richness > 50:
                saturation_factor = 1.2  # 中等色彩丰富度：标准增强
                brightness_factor = 1.1
            else:
                saturation_factor = 1.1  # 低色彩丰富度：轻微增强
                brightness_factor = 1.05
            
            # 根据AI生成指标调整
            if ai_indicators['smoothness'] > 0.7:
                # AI生成的图片通常更平滑，可以更强增强
                saturation_factor *= 1.1
                brightness_factor *= 1.05
            
            # 只处理RGB通道
            rgb = result[:, :, :3].astype(np.float32)
            
            # 转换为HSV
            hsv = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            
            # 增强饱和度
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_factor, 0, 255)
            
            # 增强亮度
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * brightness_factor, 0, 255)
            
            # 转换回RGB
            enhanced_rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            result[:, :, :3] = enhanced_rgb
            
            return result
            
        except Exception as e:
            print(f"⚠ AI色彩增强失败: {e}")
            return result
    
    def _ai_detail_restoration(self, result, original_path, ai_features):
        """AI细节恢复"""
        try:
            # 读取原始图片
            original = cv2.imread(original_path)
            if original is None:
                return result
            
            # 转换为RGB
            original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
            
            # 创建细节掩码（完全不透明区域）
            alpha = result[:, :, 3]
            detail_mask = (alpha > 200).astype(np.float32)
            
            # 在完全不透明区域恢复原始细节
            for i in range(3):
                result[:, :, i] = (result[:, :, i] * (1 - detail_mask) + 
                                  original_rgb[:, :, i] * detail_mask).astype(np.uint8)
            
            return result
            
        except Exception as e:
            print(f"⚠ AI细节恢复失败: {e}")
            return result
    
    def _save_result(self, result, output_path):
        """保存结果"""
        try:
            # 转换为PIL Image
            if len(result.shape) == 3 and result.shape[2] == 4:
                image = Image.fromarray(result, 'RGBA')
            else:
                image = Image.fromarray(result)
            
            # 保存
            image.save(output_path, 'PNG')
            
            return True
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("AI生成图片专用抠图解决方案")
    print("专门解决复杂AI生成图片抠图效果不好的问题")
    print("=" * 60)
    
    # 创建AI抠图器
    matting = AIGeneratedImageMatting()
    
    # 测试图片
    test_images = [
        "./images/bomb.png",
        "./images/resume_pressed.png"
    ]
    
    # 过滤存在的图片
    existing_images = [img for img in test_images if os.path.exists(img)]
    
    if not existing_images:
        print("❌ 未找到测试图片")
        return
    
    print(f"📸 找到测试图片: {len(existing_images)} 张")
    
    # 测试每张图片
    for i, test_image in enumerate(existing_images):
        print(f"\n🎭 测试图片 {i+1}: {os.path.basename(test_image)}")
        print("-" * 60)
        
        output_path = f"ai_matting_{i+1}_{os.path.basename(test_image)}"
        
        try:
            # 使用AI专用抠图
            result = matting.process_ai_generated_image(test_image, output_path)
            
            if result:
                print(f"✅ AI生成图片抠图成功: {output_path}")
                
                # 清理演示文件
                try:
                    os.remove(output_path)
                    print("✓ 演示文件已清理")
                except:
                    pass
            else:
                print("❌ AI生成图片抠图失败")
                
        except Exception as e:
            print(f"❌ 处理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 AI生成图片专用抠图测试完成！")
    print("\n💡 主要特性:")
    print("• AI特征智能分析")
    print("• 复杂度自适应参数调整")
    print("• 多策略智能掩码创建")
    print("• AI专用后处理优化")
    print("• 智能前景扩展和边缘优化")
    print("• AI色彩增强和细节恢复")
    print("\n🎯 现在应该能更好地处理复杂的AI生成图片！")
    print("=" * 60)

if __name__ == "__main__":
    main()
