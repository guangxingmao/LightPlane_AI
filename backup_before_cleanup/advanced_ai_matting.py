#!/usr/bin/env python3
"""
高级AI抠图解决方案 - 专门针对复杂AI生成图片
"""

import os
import cv2
import numpy as np
from PIL import Image
import time
import threading
from typing import Tuple, Optional, Dict, Any
import io

class AdvancedAIMatting:
    """高级AI抠图解决方案"""
    
    def __init__(self):
        self.available_methods = self._check_available_methods()
        print(f"🔍 可用抠图方法: {list(self.available_methods.keys())}")
    
    def _check_available_methods(self) -> Dict[str, bool]:
        """检查可用的抠图方法"""
        methods = {}
        
        # 检查RemBG
        try:
            import rembg
            methods['rembg'] = True
            print("✅ RemBG可用")
        except ImportError:
            methods['rembg'] = False
            print("❌ RemBG不可用")
        
        # 检查OpenCV
        try:
            import cv2
            methods['opencv'] = True
            print("✅ OpenCV可用")
        except ImportError:
            methods['opencv'] = False
            print("❌ OpenCV不可用")
        
        # 检查SAM
        try:
            import segment_anything
            methods['sam'] = True
            print("✅ SAM可用")
        except ImportError:
            methods['sam'] = False
            print("❌ SAM不可用")
        
        # 检查MediaPipe
        try:
            import mediapipe as mp
            methods['mediapipe'] = True
            print("✅ MediaPipe可用")
        except ImportError:
            methods['mediapipe'] = False
            print("❌ MediaPipe不可用")
        
        return methods
    
    def process_complex_image(self, image_path: str, output_path: str, 
                            method: str = 'auto', **kwargs) -> Optional[str]:
        """处理复杂AI生成图片的抠图"""
        print(f"🎨 开始处理复杂AI生成图片: {os.path.basename(image_path)}")
        
        # 分析图片复杂度
        complexity_score = self._analyze_image_complexity(image_path)
        print(f"📊 图片复杂度评分: {complexity_score:.1f}/100")
        
        # 根据复杂度选择最佳方法
        if method == 'auto':
            method = self._select_best_method(complexity_score)
        
        print(f"🎯 选择抠图方法: {method}")
        
        # 执行抠图
        result = self._execute_matting(method, image_path, output_path, complexity_score, **kwargs)
        
        if result:
            # 后处理优化
            final_result = self._advanced_post_process(result, image_path, complexity_score)
            
            # 保存最终结果
            if self._save_result(final_result, output_path):
                print(f"✅ 复杂图片抠图完成: {output_path}")
                return output_path
        
        return None
    
    def _analyze_image_complexity(self, image_path: str) -> float:
        """分析图片复杂度"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                return 50.0
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 1. 边缘复杂度
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size * 100
            
            # 2. 纹理复杂度
            # 使用拉普拉斯算子检测纹理
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            texture_variance = np.var(laplacian)
            
            # 3. 色彩复杂度
            if len(image.shape) == 3:
                # 计算色彩通道的方差
                color_variance = np.var(image, axis=(0, 1))
                total_color_variance = np.sum(color_variance)
            else:
                total_color_variance = 0
            
            # 4. 局部方差（检测细节丰富度）
            local_variance = cv2.GaussianBlur(gray.astype(np.float32), (15, 15), 3)
            local_variance = np.var(local_variance)
            
            # 5. 梯度复杂度
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            avg_gradient = np.mean(gradient_magnitude)
            
            # 综合评分
            complexity_score = (
                edge_density * 0.25 +
                min(texture_variance / 1000, 25) +
                min(total_color_variance / 10000, 20) +
                min(local_variance / 100, 15) +
                min(avg_gradient / 10, 15)
            )
            
            return min(complexity_score, 100.0)
            
        except Exception as e:
            print(f"⚠ 复杂度分析失败: {e}")
            return 50.0
    
    def _select_best_method(self, complexity_score: float) -> str:
        """根据复杂度选择最佳抠图方法"""
        if complexity_score < 30:
            # 简单图片：OpenCV足够
            return 'opencv'
        elif complexity_score < 60:
            # 中等复杂度：RemBG
            return 'rembg'
        elif complexity_score < 80:
            # 高复杂度：尝试SAM
            if self.available_methods.get('sam', False):
                return 'sam'
            else:
                return 'rembg'
        else:
            # 极高复杂度：组合方法
            return 'hybrid'
    
    def _execute_matting(self, method: str, image_path: str, output_path: str, 
                         complexity_score: float, **kwargs) -> Optional[np.ndarray]:
        """执行抠图"""
        try:
            if method == 'opencv':
                return self._opencv_matting(image_path, complexity_score)
            elif method == 'rembg':
                return self._rembg_matting(image_path, complexity_score)
            elif method == 'sam':
                return self._sam_matting(image_path, complexity_score)
            elif method == 'hybrid':
                return self._hybrid_matting(image_path, complexity_score)
            else:
                print(f"❌ 未知的抠图方法: {method}")
                return None
                
        except Exception as e:
            print(f"❌ 抠图执行失败: {e}")
            return None
    
    def _opencv_matting(self, image_path: str, complexity_score: float) -> Optional[np.ndarray]:
        """OpenCV抠图（针对复杂图片优化）"""
        try:
            print("🔧 使用OpenCV高级抠图...")
            
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # 根据复杂度调整参数
            if complexity_score > 70:
                # 高复杂度：使用更精细的参数
                mask = self._create_advanced_opencv_mask(image, 'high')
            elif complexity_score > 40:
                # 中等复杂度：平衡参数
                mask = self._create_advanced_opencv_mask(image, 'medium')
            else:
                # 低复杂度：标准参数
                mask = self._create_advanced_opencv_mask(image, 'low')
            
            # 应用掩码
            result = self._apply_mask_to_image(image, mask)
            
            return result
            
        except Exception as e:
            print(f"❌ OpenCV抠图失败: {e}")
            return None
    
    def _create_advanced_opencv_mask(self, image: np.ndarray, complexity_level: str) -> np.ndarray:
        """创建高级OpenCV掩码"""
        try:
            # 转换为HSV色彩空间
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 根据复杂度选择不同的掩码创建策略
            if complexity_level == 'high':
                # 高复杂度：多策略组合
                masks = []
                
                # 策略1: 改进的颜色阈值
                color_mask = self._create_adaptive_color_mask(hsv, sensitivity=0.8)
                masks.append(color_mask)
                
                # 策略2: 边缘检测
                edge_mask = self._create_edge_based_mask(image, threshold=0.6)
                masks.append(edge_mask)
                
                # 策略3: 纹理分析
                texture_mask = self._create_texture_based_mask(image, sensitivity=0.7)
                masks.append(texture_mask)
                
                # 策略4: 区域生长
                region_mask = self._create_region_growing_mask(image, seed_points=5)
                masks.append(region_mask)
                
                # 智能组合掩码
                final_mask = self._intelligent_mask_combination(masks, weights=[0.4, 0.3, 0.2, 0.1])
                
            elif complexity_level == 'medium':
                # 中等复杂度：三策略组合
                masks = []
                
                color_mask = self._create_adaptive_color_mask(hsv, sensitivity=0.7)
                masks.append(color_mask)
                
                edge_mask = self._create_edge_based_mask(image, threshold=0.5)
                masks.append(edge_mask)
                
                texture_mask = self._create_texture_based_mask(image, sensitivity=0.6)
                masks.append(texture_mask)
                
                final_mask = self._intelligent_mask_combination(masks, weights=[0.5, 0.3, 0.2])
                
            else:
                # 低复杂度：双策略
                color_mask = self._create_adaptive_color_mask(hsv, sensitivity=0.6)
                edge_mask = self._create_edge_based_mask(image, threshold=0.4)
                
                final_mask = self._intelligent_mask_combination([color_mask, edge_mask], weights=[0.7, 0.3])
            
            # 后处理掩码
            final_mask = self._post_process_mask(final_mask, complexity_level)
            
            return final_mask
            
        except Exception as e:
            print(f"⚠ 高级掩码创建失败: {e}")
            # 回退到简单方法
            return self._create_simple_mask(image)
    
    def _create_adaptive_color_mask(self, hsv: np.ndarray, sensitivity: float) -> np.ndarray:
        """创建自适应颜色掩码"""
        try:
            # 计算HSV通道的统计信息
            h_mean, s_mean, v_mean = np.mean(hsv, axis=(0, 1))
            h_std, s_std, v_std = np.std(hsv, axis=(0, 1))
            
            # 自适应阈值
            h_lower = max(0, h_mean - h_std * sensitivity)
            h_upper = min(179, h_mean + h_std * sensitivity)
            s_lower = max(0, s_mean - s_std * sensitivity)
            s_upper = min(255, s_mean + s_std * sensitivity)
            v_lower = max(0, v_mean - v_std * sensitivity)
            v_upper = min(255, v_mean + v_std * sensitivity)
            
            # 创建掩码
            mask = cv2.inRange(hsv, np.array([h_lower, s_lower, v_lower]), 
                              np.array([h_upper, s_upper, v_upper]))
            
            return mask
            
        except Exception as e:
            print(f"⚠ 自适应颜色掩码失败: {e}")
            return np.ones(hsv.shape[:2], dtype=np.uint8) * 255
    
    def _create_edge_based_mask(self, image: np.ndarray, threshold: float) -> np.ndarray:
        """创建基于边缘的掩码"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 多尺度边缘检测
            edges_small = cv2.Canny(gray, 30, 100)
            edges_medium = cv2.Canny(gray, 50, 150)
            edges_large = cv2.Canny(gray, 70, 200)
            
            # 组合边缘
            combined_edges = cv2.bitwise_or(edges_small, edges_medium)
            combined_edges = cv2.bitwise_or(combined_edges, edges_large)
            
            # 膨胀边缘
            kernel = np.ones((3, 3), np.uint8)
            dilated_edges = cv2.dilate(combined_edges, kernel, iterations=2)
            
            # 填充边缘内部
            mask = cv2.fillPoly(dilated_edges, [cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]], 255)
            
            return mask
            
        except Exception as e:
            print(f"⚠ 边缘掩码失败: {e}")
            return np.ones(image.shape[:2], dtype=np.uint8) * 255
    
    def _create_texture_based_mask(self, image: np.ndarray, sensitivity: float) -> np.ndarray:
        """创建基于纹理的掩码"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 计算局部方差（纹理检测）
            kernel_size = int(15 * sensitivity)
            if kernel_size % 2 == 0:
                kernel_size += 1
            
            local_variance = cv2.GaussianBlur(gray.astype(np.float32), (kernel_size, kernel_size), 3)
            local_variance = np.var(local_variance)
            
            # 创建纹理掩码
            texture_threshold = local_variance * sensitivity
            texture_mask = (local_variance > texture_threshold).astype(np.uint8) * 255
            
            return texture_mask
            
        except Exception as e:
            print(f"⚠ 纹理掩码失败: {e}")
            return np.ones(image.shape[:2], dtype=np.uint8) * 255
    
    def _create_region_growing_mask(self, image: np.ndarray, seed_points: int) -> np.ndarray:
        """创建基于区域生长的掩码"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
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
                region = self._grow_region(gray, seed_x, seed_y, threshold=20)
                mask = cv2.bitwise_or(mask, region)
            
            return mask
            
        except Exception as e:
            print(f"⚠ 区域生长掩码失败: {e}")
            return np.ones(image.shape[:2], dtype=np.uint8) * 255
    
    def _grow_region(self, gray: np.ndarray, start_x: int, start_y: int, threshold: int) -> np.ndarray:
        """区域生长算法"""
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
    
    def _intelligent_mask_combination(self, masks: list, weights: list) -> np.ndarray:
        """智能掩码组合"""
        try:
            if not masks or len(masks) != len(weights):
                return np.ones((100, 100), dtype=np.uint8) * 255
            
            # 归一化权重
            weights = np.array(weights)
            weights = weights / np.sum(weights)
            
            # 加权组合
            combined_mask = np.zeros_like(masks[0], dtype=np.float32)
            for mask, weight in zip(masks, weights):
                combined_mask += mask.astype(np.float32) * weight
            
            # 转换为二值掩码
            final_mask = (combined_mask > 127).astype(np.uint8) * 255
            
            return final_mask
            
        except Exception as e:
            print(f"⚠ 掩码组合失败: {e}")
            return masks[0] if masks else np.ones((100, 100), dtype=np.uint8) * 255
    
    def _post_process_mask(self, mask: np.ndarray, complexity_level: str) -> np.ndarray:
        """后处理掩码"""
        try:
            # 根据复杂度选择后处理策略
            if complexity_level == 'high':
                # 高复杂度：精细后处理
                # 形态学操作
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                # 边缘平滑
                mask = cv2.GaussianBlur(mask.astype(np.float32), (5, 5), 1)
                mask = (mask > 127).astype(np.uint8) * 255
                
                # 小区域去除
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    if cv2.contourArea(contour) < 100:
                        cv2.fillPoly(mask, [contour], 0)
                
            elif complexity_level == 'medium':
                # 中等复杂度：标准后处理
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.GaussianBlur(mask.astype(np.float32), (3, 3), 0.5)
                mask = (mask > 127).astype(np.uint8) * 255
                
            else:
                # 低复杂度：简单后处理
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            return mask
            
        except Exception as e:
            print(f"⚠ 掩码后处理失败: {e}")
            return mask
    
    def _create_simple_mask(self, image: np.ndarray) -> np.ndarray:
        """创建简单掩码（回退方法）"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 简单阈值
            _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            return mask
            
        except Exception as e:
            print(f"⚠ 简单掩码失败: {e}")
            return np.ones(image.shape[:2], dtype=np.uint8) * 255
    
    def _apply_mask_to_image(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """将掩码应用到图片"""
        try:
            # 确保掩码和图片尺寸一致
            if mask.shape != image.shape[:2]:
                mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
            
            # 创建RGBA图片
            result = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
            result[:, :, :3] = image
            result[:, :, 3] = mask
            
            return result
            
        except Exception as e:
            print(f"⚠ 掩码应用失败: {e}")
            return image
    
    def _rembg_matting(self, image_path: str, complexity_score: float) -> Optional[np.ndarray]:
        """RemBG抠图"""
        try:
            if not self.available_methods.get('rembg', False):
                print("❌ RemBG不可用")
                return None
            
            print("🚀 使用RemBG AI抠图...")
            import rembg
            
            # 读取图片
            with open(image_path, 'rb') as f:
                input_data = f.read()
            
            # 根据复杂度调整参数
            if complexity_score > 70:
                # 高复杂度：使用更保守的参数
                output_data = rembg.remove(input_data, alpha_matting=True, 
                                         alpha_matting_foreground_threshold=240,
                                         alpha_matting_background_threshold=10,
                                         alpha_matting_erode_size=15)
            else:
                # 标准参数
                output_data = rembg.remove(input_data)
            
            # 转换为numpy数组
            output_image = Image.open(io.BytesIO(output_data))
            result = np.array(output_image)
            
            return result
            
        except Exception as e:
            print(f"❌ RemBG抠图失败: {e}")
            return None
    
    def _sam_matting(self, image_path: str, complexity_score: float) -> Optional[np.ndarray]:
        """SAM抠图"""
        try:
            if not self.available_methods.get('sam', False):
                print("❌ SAM不可用")
                return None
            
            print("🧠 使用SAM先进分割...")
            # SAM实现代码（需要安装segment-anything）
            # 这里只是占位符
            return None
            
        except Exception as e:
            print(f"❌ SAM抠图失败: {e}")
            return None
    
    def _hybrid_matting(self, image_path: str, complexity_score: float) -> Optional[np.ndarray]:
        """混合抠图方法"""
        try:
            print("🔄 使用混合抠图方法...")
            
            # 尝试多种方法
            results = []
            
            # 方法1: RemBG
            if self.available_methods.get('rembg', False):
                rembg_result = self._rembg_matting(image_path, complexity_score)
                if rembg_result is not None:
                    results.append(('rembg', rembg_result))
            
            # 方法2: OpenCV
            opencv_result = self._opencv_matting(image_path, complexity_score)
            if opencv_result is not None:
                results.append(('opencv', opencv_result))
            
            # 选择最佳结果
            if results:
                best_result = self._select_best_result(results, complexity_score)
                return best_result
            
            return None
            
        except Exception as e:
            print(f"❌ 混合抠图失败: {e}")
            return None
    
    def _select_best_result(self, results: list, complexity_score: float) -> np.ndarray:
        """选择最佳结果"""
        try:
            if len(results) == 1:
                return results[0][1]
            
            # 评估每个结果的质量
            best_score = 0
            best_result = results[0][1]
            
            for method, result in results:
                score = self._evaluate_result_quality(result, complexity_score)
                print(f"  {method} 质量评分: {score:.1f}")
                
                if score > best_score:
                    best_score = score
                    best_result = result
            
            print(f"✅ 选择最佳结果: 评分 {best_score:.1f}")
            return best_result
            
        except Exception as e:
            print(f"⚠ 结果选择失败: {e}")
            return results[0][1]
    
    def _evaluate_result_quality(self, result: np.ndarray, complexity_score: float) -> float:
        """评估结果质量"""
        try:
            if len(result.shape) != 3 or result.shape[2] != 4:
                return 0
            
            alpha = result[:, :, 3]
            
            # 前景区域比例
            foreground_ratio = np.sum(alpha > 128) / alpha.size * 100
            
            # 边缘质量
            edge_quality = self._analyze_edge_quality(alpha)
            
            # 根据复杂度调整评分标准
            if complexity_score > 70:
                # 高复杂度：更宽松的标准
                if 20 <= foreground_ratio <= 80:
                    foreground_score = 100
                else:
                    foreground_score = max(0, 100 - abs(foreground_ratio - 50) * 2)
            else:
                # 低复杂度：更严格的标准
                if 30 <= foreground_ratio <= 70:
                    foreground_score = 100
                else:
                    foreground_score = max(0, 100 - abs(foreground_ratio - 50) * 3)
            
            # 综合评分
            total_score = foreground_score * 0.7 + edge_quality * 20 * 0.3
            
            return total_score
            
        except Exception as e:
            print(f"⚠ 质量评估失败: {e}")
            return 0
    
    def _analyze_edge_quality(self, alpha_mask: np.ndarray) -> float:
        """分析边缘质量"""
        try:
            # 使用Sobel算子检测边缘
            sobel_x = cv2.Sobel(alpha_mask, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(alpha_mask, cv2.CV_64F, 0, 1, ksize=3)
            
            # 计算边缘强度
            edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            
            # 计算平均边缘强度
            avg_edge_strength = np.mean(edge_magnitude)
            
            return avg_edge_strength
            
        except Exception as e:
            return 0
    
    def _advanced_post_process(self, result: np.ndarray, original_path: str, 
                              complexity_score: float) -> np.ndarray:
        """高级后处理"""
        try:
            print("🔧 开始高级后处理...")
            
            if len(result.shape) != 3 or result.shape[2] != 4:
                return result
            
            # 1. 智能前景扩展
            if complexity_score > 60:
                result = self._smart_foreground_expansion(result)
            
            # 2. 边缘优化
            result = self._optimize_edges(result)
            
            # 3. 色彩增强
            result = self._enhance_colors_advanced(result)
            
            # 4. 细节恢复
            if complexity_score > 70:
                result = self._restore_details(result, original_path)
            
            print("✅ 高级后处理完成")
            return result
            
        except Exception as e:
            print(f"⚠ 高级后处理失败: {e}")
            return result
    
    def _smart_foreground_expansion(self, result: np.ndarray) -> np.ndarray:
        """智能前景扩展"""
        try:
            alpha = result[:, :, 3]
            
            # 检测前景边界
            foreground_mask = alpha > 128
            
            # 使用距离变换进行智能扩展
            dist_transform = cv2.distanceTransform(foreground_mask.astype(np.uint8), cv2.DIST_L2, 5)
            
            # 创建扩展掩码
            expansion_mask = (dist_transform < 10).astype(np.uint8) * 255
            
            # 平滑过渡
            expanded_alpha = cv2.GaussianBlur(expansion_mask.astype(np.float32), (15, 15), 3)
            
            # 应用扩展
            result[:, :, 3] = expanded_alpha.astype(np.uint8)
            
            return result
            
        except Exception as e:
            print(f"⚠ 智能前景扩展失败: {e}")
            return result
    
    def _optimize_edges(self, result: np.ndarray) -> np.ndarray:
        """优化边缘"""
        try:
            alpha = result[:, :, 3]
            
            # 双边滤波保持边缘
            optimized_alpha = cv2.bilateralFilter(alpha, 9, 75, 75)
            
            # 轻微的高斯模糊
            optimized_alpha = cv2.GaussianBlur(optimized_alpha.astype(np.float32), (3, 3), 0.5)
            
            result[:, :, 3] = optimized_alpha.astype(np.uint8)
            
            return result
            
        except Exception as e:
            print(f"⚠ 边缘优化失败: {e}")
            return result
    
    def _enhance_colors_advanced(self, result: np.ndarray) -> np.ndarray:
        """高级色彩增强"""
        try:
            # 只处理RGB通道
            rgb = result[:, :, :3].astype(np.float32)
            
            # 转换为HSV
            hsv = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            
            # 增强饱和度
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.15, 0, 255)
            
            # 轻微增强亮度
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.05, 0, 255)
            
            # 转换回RGB
            enhanced_rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            result[:, :, :3] = enhanced_rgb
            
            return result
            
        except Exception as e:
            print(f"⚠ 高级色彩增强失败: {e}")
            return result
    
    def _restore_details(self, result: np.ndarray, original_path: str) -> np.ndarray:
        """恢复细节"""
        try:
            # 读取原始图片
            original = cv2.imread(original_path)
            if original is None:
                return result
            
            # 转换为RGB
            original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
            
            # 创建细节掩码
            alpha = result[:, :, 3]
            detail_mask = (alpha > 200).astype(np.float32)  # 完全不透明的区域
            
            # 在完全不透明区域恢复原始细节
            for i in range(3):
                result[:, :, i] = (result[:, :, i] * (1 - detail_mask) + 
                                  original_rgb[:, :, i] * detail_mask).astype(np.uint8)
            
            return result
            
        except Exception as e:
            print(f"⚠ 细节恢复失败: {e}")
            return result
    
    def _save_result(self, result: np.ndarray, output_path: str) -> bool:
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
            print(f"❌ 保存结果失败: {e}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("高级AI抠图解决方案 - 专门针对复杂AI生成图片")
    print("=" * 60)
    
    # 创建高级抠图器
    matting = AdvancedAIMatting()
    
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
        
        output_path = f"advanced_matting_{i+1}_{os.path.basename(test_image)}"
        
        try:
            # 使用高级抠图
            result = matting.process_complex_image(test_image, output_path)
            
            if result:
                print(f"✅ 高级抠图成功: {output_path}")
                
                # 清理演示文件
                try:
                    os.remove(output_path)
                    print("✓ 演示文件已清理")
                except:
                    pass
            else:
                print("❌ 高级抠图失败")
                
        except Exception as e:
            print(f"❌ 处理过程中发生错误: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 高级AI抠图测试完成！")
    print("\n💡 主要特性:")
    print("• 智能复杂度分析")
    print("• 自适应参数调整")
    print("• 多策略掩码创建")
    print("• 高级后处理优化")
    print("• 智能结果选择")
    print("\n🎯 现在应该能更好地处理复杂的AI生成图片！")
    print("=" * 60)

if __name__ == "__main__":
    main()
