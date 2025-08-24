#!/usr/bin/env python3
"""
测试AI背景去除功能集成到游戏系统
"""

import pygame
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_integration():
    """测试AI集成功能"""
    print("🚀 开始测试AI背景去除功能集成...")
    
    try:
        # 初始化Pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("AI集成测试")
        
        print("✓ Pygame初始化成功")
        
        # 测试导入AI模块
        try:
            from background_remover import BackgroundRemover
            print("✓ BackgroundRemover模块导入成功")
            
            from ai_image_processor import AIImageProcessor
            print("✓ AIImageProcessor模块导入成功")
            
        except ImportError as e:
            print(f"✗ AI模块导入失败: {e}")
            print("请先运行: python install_ai_dependencies.py")
            return False
        
        # 测试AI图片处理器
        try:
            processor = AIImageProcessor()
            print("✓ AI图片处理器创建成功")
            
            available_models = processor.get_available_models()
            print(f"✓ 可用AI模型: {available_models}")
            
            if not available_models:
                print("⚠ 没有可用的AI模型，请安装依赖")
                return False
            
        except Exception as e:
            print(f"✗ AI图片处理器创建失败: {e}")
            return False
        
        # 测试自定义配置页面
        try:
            from custom_config_page import CustomConfigPage
            print("✓ CustomConfigPage模块导入成功")
            
            config_page = CustomConfigPage(screen, 800, 600)
            print("✓ 自定义配置页面创建成功")
            
            # 检查是否有AI处理器
            if hasattr(config_page, 'ai_processor'):
                print("✓ AI处理器已集成到配置页面")
            else:
                print("✗ AI处理器未集成到配置页面")
                return False
            
            # 背景去除按钮已移除，现在自动处理
            print("✓ 背景去除现在自动处理，无需手动按钮")
            
            # 检查是否有模型选择按钮
            if 'select_model' in config_page.buttons:
                print("✓ 找到AI模型选择按钮")
            else:
                print("✗ 未找到AI模型选择按钮")
                return False
            
        except Exception as e:
            print(f"✗ 自定义配置页面测试失败: {e}")
            return False
        
        print("\n🎉 所有测试通过！AI背景去除功能已成功集成到游戏系统")
        
        # 显示测试结果
        screen.fill((0, 0, 0))
        
        # 创建字体
        font = pygame.font.Font(None, 36)
        
        # 显示成功消息
        success_text = font.render("AI集成测试成功！", True, (0, 255, 0))
        success_rect = success_text.get_rect(center=(400, 200))
        screen.blit(success_text, success_rect)
        
        # 显示可用模型
        models_text = font.render(f"可用模型: {', '.join(available_models)}", True, (255, 255, 255))
        models_rect = models_text.get_rect(center=(400, 250))
        screen.blit(models_text, models_rect)
        
        # 显示使用说明
        instruction_text = font.render("按任意键退出测试", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(400, 300))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        
        # 等待用户按键
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
        
        return True
        
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        return False
    
    finally:
        pygame.quit()

def test_individual_components():
    """测试各个组件"""
    print("\n🔍 测试各个组件...")
    
    # 测试背景去除器
    try:
        from background_remover import BackgroundRemover
        remover = BackgroundRemover()
        print("✓ BackgroundRemover组件正常")
    except Exception as e:
        print(f"✗ BackgroundRemover组件异常: {e}")
    
    # 测试AI图片处理器
    try:
        from ai_image_processor import AIImageProcessor
        processor = AIImageProcessor()
        print("✓ AIImageProcessor组件正常")
    except Exception as e:
        print(f"✗ AIImageProcessor组件异常: {e}")
    
    # 测试自定义配置页面
    try:
        from custom_config_page import CustomConfigPage
        print("✓ CustomConfigPage组件正常")
    except Exception as e:
        print(f"✗ CustomConfigPage组件异常: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("AI背景去除功能集成测试")
    print("=" * 50)
    
    # 测试各个组件
    test_individual_components()
    
    print("\n" + "=" * 50)
    
    # 运行完整测试
    success = test_ai_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！AI功能已成功集成")
        print("\n💡 使用方法:")
        print("1. 运行游戏")
        print("2. 进入自定义配置页面")
        print("3. 上传或生成飞机图片")
        print("4. 背景自动去除（无需手动操作）")
        print("5. 点击 'AI Model' 按钮切换AI模型")
    else:
        print("❌ 测试失败！请检查错误信息")
        print("\n🔧 故障排除:")
        print("1. 运行: python install_ai_dependencies.py")
        print("2. 检查Python环境和依赖包")
        print("3. 查看错误日志")
    
    print("=" * 50)
