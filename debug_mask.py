#!/usr/bin/env python3
"""
调试掩码内容
"""

import cv2
import numpy as np
from PIL import Image
import os

def debug_mask():
    """调试掩码内容"""
    print("🔍 调试掩码内容...")
    
    try:
        from background_remover import BackgroundRemover
        
        # 创建背景去除器
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
        
        # 测试各个掩码创建方法
        print("\n🔬 测试各个掩码创建方法...")
        
        # 1. 颜色掩码
        print("\n1. 颜色掩码:")
        color_mask = remover._create_color_mask(hsv)
        if color_mask is not None:
            print(f"  尺寸: {color_mask.shape}")
            print(f"  值范围: {np.min(color_mask)} - {np.max(color_mask)}")
            print(f"  非零像素数量: {np.sum(color_mask > 0)}")
            print(f"  零像素数量: {np.sum(color_mask == 0)}")
            
            # 保存颜色掩码
            cv2.imwrite("debug_color_mask.png", color_mask)
            print("  已保存到: debug_color_mask.png")
        
        # 2. 边缘检测掩码
        print("\n2. 边缘检测掩码:")
        edge_mask = remover._create_edge_mask(image_rgb)
        if edge_mask is not None:
            print(f"  尺寸: {edge_mask.shape}")
            print(f"  值范围: {np.min(edge_mask)} - {np.max(edge_mask)}")
            print(f"  非零像素数量: {np.sum(edge_mask > 0)}")
            print(f"  零像素数量: {np.sum(edge_mask == 0)}")
            
            # 保存边缘检测掩码
            cv2.imwrite("debug_edge_mask.png", edge_mask)
            print("  已保存到: debug_edge_mask.png")
        
        # 3. 轮廓检测掩码
        print("\n3. 轮廓检测掩码:")
        contour_mask = remover._create_contour_mask(image_rgb)
        if contour_mask is not None:
            print(f"  尺寸: {contour_mask.shape}")
            print(f"  值范围: {np.min(contour_mask)} - {np.max(contour_mask)}")
            print(f"  非零像素数量: {np.sum(contour_mask > 0)}")
            print(f"  零像素数量: {np.sum(contour_mask == 0)}")
            
            # 保存轮廓检测掩码
            cv2.imwrite("debug_contour_mask.png", contour_mask)
            print("  已保存到: debug_contour_mask.png")
        
        # 4. 组合掩码
        print("\n4. 组合掩码:")
        combined_mask = remover._combine_masks([color_mask, edge_mask, contour_mask])
        if combined_mask is not None:
            print(f"  尺寸: {combined_mask.shape}")
            print(f"  值范围: {np.min(combined_mask)} - {np.max(combined_mask)}")
            print(f"  非零像素数量: {np.sum(combined_mask > 0)}")
            print(f"  零像素数量: {np.sum(combined_mask == 0)}")
            
            # 保存组合掩码
            cv2.imwrite("debug_combined_mask.png", combined_mask)
            print("  已保存到: debug_combined_mask.png")
        
        # 5. 后处理掩码
        print("\n5. 后处理掩码:")
        final_mask = remover._post_process_mask(combined_mask)
        if final_mask is not None:
            print(f"  尺寸: {final_mask.shape}")
            print(f"  值范围: {np.min(final_mask)} - {np.max(final_mask)}")
            print(f"  非零像素数量: {np.sum(final_mask > 0)}")
            print(f"  零像素数量: {np.sum(final_mask == 0)}")
            
            # 保存最终掩码
            cv2.imwrite("debug_final_mask.png", final_mask)
            print("  已保存到: debug_final_mask.png")
        
        # 6. 测试掩码应用
        print("\n6. 测试掩码应用:")
        try:
            result = remover._apply_mask(image_rgb, final_mask)
            if result is not None:
                print(f"  结果尺寸: {result.shape}")
                print(f"  Alpha通道范围: {np.min(result[:, :, 3])} - {np.max(result[:, :, 3])}")
                
                # 保存结果
                pil_image = Image.fromarray(result, 'RGBA')
                pil_image.save("debug_result_rgba.png")
                print("  已保存到: debug_result_rgba.png")
                
                # 分析Alpha通道
                alpha = result[:, :, 3]
                transparent_pixels = np.sum(alpha < 128)
                total_pixels = alpha.shape[0] * alpha.shape[1]
                transparent_ratio = transparent_pixels / total_pixels * 100
                print(f"  透明区域比例: {transparent_ratio:.1f}%")
                
            else:
                print("  掩码应用失败")
        except Exception as e:
            print(f"  掩码应用失败: {e}")
        
    except Exception as e:
        print(f"调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("=" * 50)
    print("掩码内容调试")
    print("=" * 50)
    
    debug_mask()
    
    print("\n" + "=" * 50)
    print("调试完成！请查看生成的调试文件")
    print("=" * 50)

if __name__ == "__main__":
    main()
