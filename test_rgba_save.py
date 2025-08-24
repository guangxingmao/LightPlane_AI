#!/usr/bin/env python3
"""
测试RGBA图片保存和读取
"""

import cv2
import numpy as np
from PIL import Image
import os

def test_rgba_save():
    """测试RGBA图片保存"""
    print("🧪 测试RGBA图片保存和读取...")
    
    # 创建一个测试RGBA图片
    width, height = 100, 100
    
    # 创建RGB通道（红色圆形）
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    center = (width // 2, height // 2)
    radius = 40
    
    # 绘制红色圆形
    for y in range(height):
        for x in range(width):
            if (x - center[0])**2 + (y - center[1])**2 <= radius**2:
                rgb[y, x] = [255, 0, 0]  # 红色
    
    # 创建Alpha通道（圆形内部不透明，外部透明）
    alpha = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            if (x - center[0])**2 + (y - center[1])**2 <= radius**2:
                alpha[y, x] = 255  # 不透明
            else:
                alpha[y, x] = 0    # 透明
    
    # 组合为RGBA
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    rgba[:, :, :3] = rgb
    rgba[:, :, 3] = alpha
    
    print(f"创建的RGBA图片尺寸: {rgba.shape}")
    print(f"Alpha通道范围: {np.min(alpha)} - {np.max(alpha)}")
    
    # 测试保存方法1: 使用PIL
    pil_path = "test_rgba_pil.png"
    try:
        pil_image = Image.fromarray(rgba, 'RGBA')
        pil_image.save(pil_path, 'PNG')
        print(f"✓ PIL保存成功: {pil_path}")
        
        # 检查文件大小
        if os.path.exists(pil_path):
            file_size = os.path.getsize(pil_path)
            print(f"文件大小: {file_size} bytes")
        
        # 测试读取
        test_read_pil(pil_path)
        
    except Exception as e:
        print(f"❌ PIL保存失败: {e}")
    
    # 测试保存方法2: 使用OpenCV
    cv2_path = "test_rgba_cv2.png"
    try:
        # OpenCV保存RGBA
        cv2.imwrite(cv2_path, rgba)
        print(f"✓ OpenCV保存成功: {cv2_path}")
        
        # 检查文件大小
        if os.path.exists(cv2_path):
            file_size = os.path.getsize(cv2_path)
            print(f"文件大小: {file_size} bytes")
        
        # 测试读取
        test_read_cv2(cv2_path)
        
    except Exception as e:
        print(f"❌ OpenCV保存失败: {e}")
    
    # 清理测试文件
    for path in [pil_path, cv2_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"✓ 清理测试文件: {path}")
            except:
                pass

def test_read_pil(path):
    """测试PIL读取"""
    try:
        pil_image = Image.open(path)
        print(f"PIL读取 - 尺寸: {pil_image.size}, 模式: {pil_image.mode}")
        
        if pil_image.mode == 'RGBA':
            # 转换为numpy数组
            rgba = np.array(pil_image)
            alpha = rgba[:, :, 3]
            print(f"PIL读取 - Alpha通道范围: {np.min(alpha)} - {np.max(alpha)}")
            
            # 计算透明区域
            transparent_pixels = np.sum(alpha < 128)
            total_pixels = alpha.shape[0] * alpha.shape[1]
            transparent_ratio = transparent_pixels / total_pixels * 100
            print(f"PIL读取 - 透明区域比例: {transparent_ratio:.1f}%")
        else:
            print("PIL读取 - 没有Alpha通道")
            
    except Exception as e:
        print(f"PIL读取失败: {e}")

def test_read_cv2(path):
    """测试OpenCV读取"""
    try:
        # 使用IMREAD_UNCHANGED读取
        rgba = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if rgba is not None:
            print(f"OpenCV读取 - 尺寸: {rgba.shape}")
            
            if len(rgba.shape) == 3 and rgba.shape[2] == 4:
                alpha = rgba[:, :, 3]
                print(f"OpenCV读取 - Alpha通道范围: {np.min(alpha)} - {np.max(alpha)}")
                
                # 计算透明区域
                transparent_pixels = np.sum(alpha < 128)
                total_pixels = alpha.shape[0] * alpha.shape[1]
                transparent_ratio = transparent_pixels / total_pixels * 100
                print(f"OpenCV读取 - 透明区域比例: {transparent_ratio:.1f}%")
            else:
                print("OpenCV读取 - 没有Alpha通道")
        else:
            print("OpenCV读取失败")
            
    except Exception as e:
        print(f"OpenCV读取失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("RGBA图片保存和读取测试")
    print("=" * 50)
    
    test_rgba_save()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
