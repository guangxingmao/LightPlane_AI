#!/usr/bin/env python3
"""
复杂AI生成图片抠图解决方案 - 修复版
"""

import os
import cv2
import numpy as np
from PIL import Image
import time
import io

class ComplexImageMattingFixed:
    """复杂图片抠图解决方案（修复版）"""
    
    def __init__(self):
        self.available_methods = self._check_available_methods()
    
    def _check_available_methods(self):
        """检查可用方法"""
        methods = {}
        
        try:
            import rembg
            methods['rembg'] = True
            print("✅ RemBG可用")
        except:
            methods['rembg'] = False
            print("❌ RemBG不可用")
        
        methods['opencv'] = True
        print("✅ OpenCV可用")
        
        return methods
    
    def process_complex_image(self, image_path, output_path):
        """处理复杂AI生成图片"""
        print(f"🎨 处理复杂图片: {os.path.basename(image_path)}")
        
        # 分析复杂度
        complexity = self._analyze_complexity(image_path)
        print(f"📊 复杂度评分: {complexity:.1f}/100")
        
        # 选择最佳方法
        if complexity > 70 and self.available_methods.get('rembg'):
            print("🚀 使用RemBG + 高级后处理")
            result = self._rembg_with_advanced_postprocess(image_path)
        else:
            print("🔧 使用OpenCV高级算法")
            result = self._opencv_advanced(image_path)
        
        if result is not None:
            # 保存结果
            if self._save_result(result, output_path):
                print(f"✅ 复杂图片抠图完成: {output_path}")
                return output_path
        
        return None
    
    def _analyze_complexity(self, image_path):
        """分析图片复杂度"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 50.0
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 边缘复杂度
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size * 100
            
            # 纹理复杂度
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            texture_variance = np.var(laplacian)
            
            # 色彩复杂度
            if len(image.shape) == 3:
                color_variance = np.var(image, axis=(0, 1))
                total_color_variance = np.sum(color_variance)
            else:
                total_color_variance = 0
            
            # 综合评分
            complexity = (
                edge_density * 0.3 +
                min(texture_variance / 1000, 30) +
                min(total_color_variance / 10000, 40)
            )
            
            return min(complexity, 100.0)
            
        except Exception as e:
            print(f"⚠ 复杂度分析失败: {e}")
            return 50.0
    
    def _rembg_with_advanced_postprocess(self, image_path):
        """RemBG + 高级后处理"""
        try:
            import rembg
            
            print("🔍 开始RemBG AI抠图...")
            with open(image_path, 'rb') as f:
                input_data = f.read()
            
            # 使用保守参数
            output_data = rembg.remove(input_data, alpha_matting=True, 
                                     alpha_matting_foreground_threshold=240,
                                     alpha_matting_background_threshold=10,
                                     alpha_matting_erode_size=15)
            
            # 转换为numpy数组
            output_image = Image.open(io.BytesIO(output_data))
            result = np.array(output_image)
            
            # 高级后处理
            result = self._advanced_postprocess(result, image_path)
            
            return result
            
        except Exception as e:
            print(f"❌ RemBG处理失败: {e}")
            return None
    
    def _opencv_advanced(self, image_path):
        """OpenCV高级抠图"""
        try:
            print("🔧 使用OpenCV高级算法...")
            
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # 多策略掩码创建
            masks = []
            
            # 策略1: 改进的颜色阈值
            color_mask = self._create_adaptive_color_mask(image)
            if color_mask is not None:
                masks.append(color_mask)
            
            # 策略2: 边缘检测
            edge_mask = self._create_edge_mask(image)
            if edge_mask is not None:
                masks.append(edge_mask)
            
            # 策略3: 纹理分析
            texture_mask = self._create_texture_mask(image)
            if texture_mask is not None:
                masks.append(texture_mask)
            
            # 智能组合掩码
            if masks:
                final_mask = self._combine_masks_intelligently(masks)
            else:
                # 回退到简单方法
                final_mask = self._create_simple_mask(image)
            
            # 应用掩码
            result = self._apply_mask(image, final_mask)
            
            # 高级后处理
            result = self._advanced_postprocess(result, image_path)
            
            return result
            
        except Exception as e:
            print(f"❌ OpenCV处理失败: {e}")
            return None
    
    def _create_adaptive_color_mask(self, image):
        """创建自适应颜色掩码"""
        try:
            # 转换为HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 计算统计信息
            h_mean, s_mean, v_mean = np.mean(hsv, axis=(0, 1))
            h_std, s_std, v_std = np.std(hsv, axis=(0, 1))
            
            # 确保阈值在有效范围内
            h_lower = max(0, int(h_mean - h_std * 0.8))
            h_upper = min(179, int(h_mean + h_std * 0.8))
            s_lower = max(0, int(s_mean - s_std * 0.8))
            s_upper = min(255, int(s_mean + s_std * 0.8))
            v_lower = max(0, int(v_mean - v_std * 0.8))
            v_upper = min(255, int(v_mean + v_std * 0.8))
            
            # 确保上下限类型一致
            lower_bound = np.array([h_lower, s_lower, v_lower], dtype=np.uint8)
            upper_bound = np.array([h_upper, s_upper, v_upper], dtype=np.uint8)
            
            # 创建掩码
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            
            return mask
            
        except Exception as e:
            print(f"⚠ 颜色掩码失败: {e}")
            return None
    
    def _create_edge_mask(self, image):
        """创建边缘掩码"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 多尺度边缘检测
            edges1 = cv2.Canny(gray, 30, 100)
            edges2 = cv2.Canny(gray, 50, 150)
            edges3 = cv2.Canny(gray, 70, 200)
            
            # 组合边缘
            combined = cv2.bitwise_or(edges1, edges2)
            combined = cv2.bitwise_or(combined, edges3)
            
            # 膨胀和填充
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(combined, kernel, iterations=2)
            
            # 填充轮廓
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            mask = np.zeros_like(gray)
            if contours:
                cv2.fillPoly(mask, contours, 255)
            
            return mask
            
        except Exception as e:
            print(f"⚠ 边缘掩码失败: {e}")
            return None
    
    def _create_texture_mask(self, image):
        """创建纹理掩码"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 计算局部方差
            local_var = cv2.GaussianBlur(gray.astype(np.float32), (15, 15), 3)
            local_var = np.var(local_var)
            
            # 创建纹理掩码
            texture_threshold = local_var * 0.7
            texture_mask = (local_var > texture_threshold).astype(np.uint8) * 255
            
            return texture_mask
            
        except Exception as e:
            print(f"⚠ 纹理掩码失败: {e}")
            return None
    
    def _create_simple_mask(self, image):
        """创建简单掩码（回退方法）"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 使用Otsu自适应阈值
            _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return mask
            
        except Exception as e:
            print(f"⚠ 简单掩码失败: {e}")
            return np.ones(image.shape[:2], dtype=np.uint8) * 255
    
    def _combine_masks_intelligently(self, masks):
        """智能组合掩码"""
        try:
            if not masks:
                return np.ones((100, 100), dtype=np.uint8) * 255
            
            # 过滤掉None的掩码
            valid_masks = [m for m in masks if m is not None]
            if not valid_masks:
                return np.ones((100, 100), dtype=np.uint8) * 255
            
            # 使用第一个有效掩码作为基础
            base_mask = valid_masks[0].copy()
            
            # 结合其他掩码
            for mask in valid_masks[1:]:
                if mask is not None and mask.shape == base_mask.shape:
                    # 智能组合策略：使用OR操作
                    base_mask = cv2.bitwise_or(base_mask, mask)
            
            return base_mask
            
        except Exception as e:
            print(f"⚠ 掩码组合失败: {e}")
            return masks[0] if masks and masks[0] is not None else np.ones((100, 100), dtype=np.uint8) * 255
    
    def _apply_mask(self, image, mask):
        """应用掩码到图片"""
        try:
            # 确保掩码是有效的
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
    
    def _advanced_postprocess(self, result, original_path):
        """高级后处理"""
        try:
            print("🔧 开始高级后处理...")
            
            if len(result.shape) != 3 or result.shape[2] != 4:
                return result
            
            alpha = result[:, :, 3]
            
            # 1. 智能前景扩展
            foreground_ratio = np.sum(alpha > 128) / alpha.size * 100
            if foreground_ratio < 30:
                print(f"⚠ 检测到过度抠图（前景区域: {foreground_ratio:.1f}%），开始扩展前景...")
                alpha = self._expand_foreground(alpha)
                result[:, :, 3] = alpha
                new_ratio = np.sum(alpha > 128) / alpha.size * 100
                print(f"✅ 前景扩展完成，新前景区域: {new_ratio:.1f}%")
            
            # 2. 边缘优化
            alpha = self._optimize_edges(alpha)
            result[:, :, 3] = alpha
            
            # 3. 色彩增强
            result = self._enhance_colors(result)
            
            print("✅ 高级后处理完成")
            return result
            
        except Exception as e:
            print(f"⚠ 后处理失败: {e}")
            return result
    
    def _expand_foreground(self, alpha):
        """扩展前景区域"""
        try:
            # 前景掩码
            foreground = alpha > 128
            
            # 形态学膨胀
            kernel = np.ones((7, 7), np.uint8)
            expanded = cv2.dilate(foreground.astype(np.uint8), kernel, iterations=2)
            
            # 高斯模糊创建平滑过渡
            expanded = cv2.GaussianBlur(expanded.astype(np.float32), (15, 15), 3)
            
            # 重新映射到0-255
            expanded_alpha = (expanded * 255).astype(np.uint8)
            
            return expanded_alpha
            
        except Exception as e:
            print(f"⚠ 前景扩展失败: {e}")
            return alpha
    
    def _optimize_edges(self, alpha):
        """优化边缘"""
        try:
            # 双边滤波保持边缘
            optimized = cv2.bilateralFilter(alpha, 9, 75, 75)
            
            # 轻微高斯模糊
            optimized = cv2.GaussianBlur(optimized.astype(np.float32), (3, 3), 0.5)
            
            return optimized.astype(np.uint8)
            
        except Exception as e:
            print(f"⚠ 边缘优化失败: {e}")
            return alpha
    
    def _enhance_colors(self, result):
        """增强色彩"""
        try:
            # 只处理RGB通道
            rgb = result[:, :, :3].astype(np.float32)
            
            # 转换为HSV
            hsv = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            
            # 增强饱和度
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)
            
            # 轻微增强亮度
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255)
            
            # 转换回RGB
            enhanced_rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            result[:, :, :3] = enhanced_rgb
            
            return result
            
        except Exception as e:
            print(f"⚠ 色彩增强失败: {e}")
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
    print("=" * 50)
    print("复杂AI生成图片抠图解决方案 - 修复版")
    print("=" * 50)
    
    # 创建抠图器
    matting = ComplexImageMattingFixed()
    
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
        print("-" * 50)
        
        output_path = f"complex_matting_fixed_{i+1}_{os.path.basename(test_image)}"
        
        try:
            # 使用复杂图片抠图
            result = matting.process_complex_image(test_image, output_path)
            
            if result:
                print(f"✅ 复杂图片抠图成功: {output_path}")
                
                # 清理演示文件
                try:
                    os.remove(output_path)
                    print("✓ 演示文件已清理")
                except:
                    pass
            else:
                print("❌ 复杂图片抠图失败")
                
        except Exception as e:
            print(f"❌ 处理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 复杂图片抠图测试完成！")
    print("\n💡 主要特性:")
    print("• 智能复杂度分析")
    print("• 自适应参数调整")
    print("• 多策略掩码创建")
    print("• 高级后处理优化")
    print("• 智能前景扩展")
    print("• 错误处理和回退")
    print("\n🎯 现在应该能更好地处理复杂的AI生成图片！")
    print("=" * 50)

if __name__ == "__main__":
    main()
