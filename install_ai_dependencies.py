#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装AI系统所需的依赖包
"""

import subprocess
import sys
import os

def install_package(package_name, pip_name=None):
    """安装Python包"""
    if pip_name is None:
        pip_name = package_name
    
    print(f"📦 安装 {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        print(f"✅ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {package_name} 安装失败")
        return False

def main():
    print("🚀 开始安装AI系统依赖...")
    
    # 必需的依赖包
    required_packages = [
        ("PyTorch", "torch"),
        ("NumPy", "numpy"),
        ("Matplotlib", "matplotlib"),
        ("Dataclasses", "dataclasses"),  # Python 3.7+ 内置
    ]
    
    # 可选但推荐的依赖包
    optional_packages = [
        ("CUDA支持", "torchvision"),
        ("科学计算", "scipy"),
        ("数据可视化", "seaborn"),
        ("进度条", "tqdm"),
    ]
    
    print("\n📋 安装必需的依赖包:")
    success_count = 0
    total_required = len(required_packages)
    
    for package_name, pip_name in required_packages:
        if install_package(package_name, pip_name):
            success_count += 1
    
    print(f"\n📊 必需依赖安装结果: {success_count}/{total_required}")
    
    if success_count < total_required:
        print("❌ 部分必需依赖安装失败，AI系统可能无法正常工作")
        return False
    
    print("\n📋 安装可选的依赖包:")
    optional_success = 0
    total_optional = len(optional_packages)
    
    for package_name, pip_name in optional_packages:
        if install_package(package_name, pip_name):
            optional_success += 1
    
    print(f"\n📊 可选依赖安装结果: {optional_success}/{total_optional}")
    
    # 检查PyTorch安装
    print("\n🔍 检查PyTorch安装...")
    try:
        import torch
        print(f"✅ PyTorch版本: {torch.__version__}")
        print(f"✅ CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✅ CUDA版本: {torch.version.cuda}")
            print(f"✅ GPU数量: {torch.cuda.device_count()}")
    except ImportError:
        print("❌ PyTorch导入失败")
        return False
    
    # 检查NumPy安装
    print("\n🔍 检查NumPy安装...")
    try:
        import numpy as np
        print(f"✅ NumPy版本: {np.__version__}")
    except ImportError:
        print("❌ NumPy导入失败")
        return False
    
    # 创建模型目录
    print("\n📁 创建模型目录...")
    models_dir = "./models"
    os.makedirs(models_dir, exist_ok=True)
    print(f"✅ 模型目录已创建: {models_dir}")
    
    # 测试AI系统导入
    print("\n🧪 测试AI系统导入...")
    try:
        from ml_game_ai import MLGameAI
        from rl_game_ai import RLGameAI
        from intelligent_decision_system import IntelligentDecisionSystem
        from ai_learning_optimizer import AILearningOptimizer
        from ai_master_controller import AIMasterController
        print("✅ 所有AI系统模块导入成功")
    except ImportError as e:
        print(f"❌ AI系统模块导入失败: {e}")
        return False
    
    print("\n🎉 AI系统依赖安装完成！")
    print("\n📖 使用说明:")
    print("1. 运行 'python3 ml_game_ai.py' 测试机器学习AI")
    print("2. 运行 'python3 rl_game_ai.py' 测试强化学习AI")
    print("3. 运行 'python3 intelligent_decision_system.py' 测试智能决策系统")
    print("4. 运行 'python3 ai_learning_optimizer.py' 测试学习优化系统")
    print("5. 运行 'python3 ai_master_controller.py' 测试主控制器")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 所有依赖安装成功，AI系统可以正常使用！")
    else:
        print("\n❌ 依赖安装失败，请检查错误信息并重试")
        sys.exit(1)
