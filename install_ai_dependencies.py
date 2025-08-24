#!/usr/bin/env python3
"""
AI图片识别和背景去除依赖安装脚本
"""

import subprocess
import sys
import os

def install_package(package_name, pip_name=None):
    """安装Python包"""
    if pip_name is None:
        pip_name = package_name
    
    print(f"正在安装 {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        print(f"✓ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {package_name} 安装失败: {e}")
        return False

def main():
    """主安装函数"""
    print("🚀 开始安装AI图片识别和背景去除依赖包...")
    print("=" * 50)
    
    # 基础依赖包
    packages = [
        ("Pillow", "Pillow"),  # PIL图像处理
        ("numpy", "numpy"),    # 数值计算
    ]
    
    # AI模型依赖包
    ai_packages = [
        ("rembg", "rembg"),                    # 背景去除
        ("opencv-python", "opencv-python"),    # 计算机视觉
        ("torch", "torch"),                    # PyTorch (SAM需要)
        ("torchvision", "torchvision"),        # PyTorch视觉工具
    ]
    
    # 可选的高级包
    optional_packages = [
        ("segment-anything", "git+https://github.com/facebookresearch/segment-anything.git"),  # SAM模型
        ("scikit-image", "scikit-image"),      # 图像处理
    ]
    
    print("📦 安装基础依赖包...")
    success_count = 0
    for package, pip_name in packages:
        if install_package(package, pip_name):
            success_count += 1
    
    print(f"\n📦 安装AI模型依赖包...")
    for package, pip_name in ai_packages:
        if install_package(package, pip_name):
            success_count += 1
    
    print(f"\n📦 安装可选的高级包...")
    print("注意: 这些包可能需要较长时间下载")
    for package, pip_name in optional_packages:
        if install_package(package, pip_name):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 安装完成! 成功安装 {success_count} 个包")
    
    # 检查安装结果
    print("\n🔍 检查安装结果...")
    check_installations()
    
    print("\n📚 使用说明:")
    print("1. RemBG: 最简单的背景去除，效果很好")
    print("2. OpenCV: 基于颜色阈值的背景去除，速度快")
    print("3. SAM: 最精确的分割模型，需要下载预训练模型")
    
    print("\n💡 快速开始:")
    print("from background_remover import BackgroundRemover")
    print("remover = BackgroundRemover()")
    print("result = remover.remove_background('your_image.png')")

def check_installations():
    """检查包安装状态"""
    packages_to_check = [
        ("PIL", "Pillow"),
        ("numpy", "numpy"),
        ("rembg", "rembg"),
        ("cv2", "opencv-python"),
        ("torch", "torch"),
    ]
    
    for import_name, package_name in packages_to_check:
        try:
            __import__(import_name)
            print(f"✓ {package_name} 可用")
        except ImportError:
            print(f"✗ {package_name} 不可用")

if __name__ == "__main__":
    main()
