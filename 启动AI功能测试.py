#!/usr/bin/env python3
"""
AI背景去除功能快速启动脚本
"""

import os
import sys
import subprocess

def main():
    """主函数"""
    print("🚀 AI背景去除功能快速启动")
    print("=" * 40)
    
    # 检查Python环境
    print("🔍 检查Python环境...")
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return
    
    print("✓ Python版本符合要求")
    
    # 检查必要文件
    print("\n🔍 检查必要文件...")
    required_files = [
        'background_remover.py',
        'ai_image_processor.py', 
        'custom_config_page.py',
        'install_ai_dependencies.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 缺少必要文件: {', '.join(missing_files)}")
        return
    
    print("✓ 所有必要文件都存在")
    
    # 检查依赖
    print("\n🔍 检查AI依赖...")
    try:
        import pygame
        print("✓ Pygame已安装")
    except ImportError:
        print("✗ Pygame未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            print("✓ Pygame安装成功")
        except:
            print("❌ Pygame安装失败")
            return
    
    # 检查AI依赖
    try:
        import PIL
        print("✓ PIL已安装")
    except ImportError:
        print("⚠ PIL未安装，建议运行依赖安装脚本")
    
    # 提供选项
    print("\n🎯 选择操作:")
    print("1. 安装AI依赖包")
    print("2. 测试AI集成功能")
    print("3. 运行完整测试")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == '1':
                print("\n📦 开始安装AI依赖包...")
                if os.path.exists('install_ai_dependencies.py'):
                    subprocess.run([sys.executable, 'install_ai_dependencies.py'])
                else:
                    print("❌ 安装脚本不存在")
                break
                
            elif choice == '2':
                print("\n🧪 开始测试AI集成功能...")
                if os.path.exists('test_ai_integration.py'):
                    subprocess.run([sys.executable, 'test_ai_integration.py'])
                else:
                    print("❌ 测试脚本不存在")
                break
                
            elif choice == '3':
                print("\n🔬 运行完整测试...")
                print("这将测试所有组件并显示详细结果")
                if os.path.exists('test_ai_integration.py'):
                    subprocess.run([sys.executable, 'test_ai_integration.py'])
                else:
                    print("❌ 测试脚本不存在")
                break
                
            elif choice == '4':
                print("👋 再见！")
                break
                
            else:
                print("❌ 无效选择，请输入1-4")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            break
    
    print("\n" + "=" * 40)
    print("💡 使用提示:")
    print("• 首次使用建议先选择选项1安装依赖")
    print("• 安装完成后选择选项2或3测试功能")
    print("• 如果遇到问题，查看错误信息和日志")
    print("• 详细使用说明请参考: AI图片处理使用指南.md")

if __name__ == "__main__":
    main()
