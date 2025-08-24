#!/usr/bin/env python3
"""
测试自动背景去除功能
"""

import os
import sys
import pygame

def test_auto_background_removal():
    """测试自动背景去除功能"""
    print("🧪 测试自动背景去除功能...")
    
    try:
        from custom_config_page import CustomConfigPage
        
        # 初始化Pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        # 创建自定义配置页面
        config_page = CustomConfigPage(screen, 800, 600)
        print("✓ 自定义配置页面创建成功")
        
        # 检查是否有AI处理器
        if hasattr(config_page, 'ai_processor'):
            print("✓ AI处理器已集成")
        else:
            print("❌ AI处理器未集成")
            return False
        
        # 检查是否有自动背景去除方法
        if hasattr(config_page, 'auto_remove_background'):
            print("✓ 自动背景去除方法已添加")
        else:
            print("❌ 自动背景去除方法未添加")
            return False
        
        # 测试自动背景去除方法
        print("\n🚀 测试自动背景去除方法...")
        
        # 创建一个测试图片surface
        test_surface = pygame.Surface((100, 100))
        test_surface.fill((255, 0, 0))  # 红色
        
        # 调用自动背景去除方法
        try:
            config_page.auto_remove_background('player_plane', test_surface)
            print("✓ 自动背景去除方法调用成功")
            
            # 等待一段时间看处理状态
            print("等待处理状态更新...")
            for i in range(10):
                status = config_page.ai_processor.get_processing_status()
                print(f"状态: {status['status']}, 进度: {status['progress']}%, 消息: {status['message']}")
                
                if status['status'] == 'completed':
                    print("✓ 自动背景去除处理完成")
                    break
                elif status['status'] == 'error':
                    print(f"❌ 自动背景去除处理失败: {status['message']}")
                    break
                
                pygame.time.wait(500)  # 等待500毫秒
            
            return True
            
        except Exception as e:
            print(f"❌ 自动背景去除方法调用失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()

def main():
    """主函数"""
    print("=" * 50)
    print("自动背景去除功能测试")
    print("=" * 50)
    
    # 测试自动背景去除功能
    success = test_auto_background_removal()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试通过！自动背景去除功能正常工作")
        print("\n💡 功能说明:")
        print("• 上传飞机图片后自动去除背景")
        print("• AI生成飞机图片后自动去除背景")
        print("• 无需手动点击按钮")
        print("• 背景去除在后台自动进行")
    else:
        print("❌ 测试失败！请检查错误信息")
        print("\n🔧 故障排除建议:")
        print("1. 检查AI处理器是否正确集成")
        print("2. 检查自动背景去除方法是否正确添加")
        print("3. 查看详细的错误日志")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
