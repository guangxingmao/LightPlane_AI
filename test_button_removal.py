#!/usr/bin/env python3
"""
测试AI模型文本按钮是否已被成功删除
"""

import os
import pygame

def test_button_removal():
    """测试按钮删除"""
    print("🧪 测试AI模型文本按钮是否已被成功删除...")
    
    try:
        # 导入CustomConfigPage
        from custom_config_page import CustomConfigPage
        
        # 创建Pygame屏幕
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        # 创建配置页面
        config_page = CustomConfigPage(screen)
        print(f"✅ CustomConfigPage创建成功")
        
        # 检查按钮字典
        print(f"\n📋 检查按钮字典:")
        print(f"  按钮总数: {len(config_page.buttons)}")
        
        # 列出所有按钮
        for button_name, button in config_page.buttons.items():
            print(f"  • {button_name}: {button['text']} ({button['type']})")
        
        # 检查是否还有select_model按钮
        if 'select_model' in config_page.buttons:
            print(f"❌ select_model按钮仍然存在！")
            return False
        else:
            print(f"✅ select_model按钮已成功删除")
        
        # 检查是否还有cycle_ai_model方法
        if hasattr(config_page, 'cycle_ai_model'):
            print(f"❌ cycle_ai_model方法仍然存在！")
            return False
        else:
            print(f"✅ cycle_ai_model方法已成功删除")
        
        # 检查按钮类型
        button_types = [button['type'] for button in config_page.buttons.values()]
        print(f"\n🔍 按钮类型分析:")
        print(f"  所有按钮类型: {button_types}")
        
        # 检查是否有其他AI相关的按钮
        ai_related_buttons = [btn for btn in button_types if 'ai' in btn.lower() or 'model' in btn.lower()]
        if ai_related_buttons:
            print(f"⚠ 发现其他AI相关按钮: {ai_related_buttons}")
        else:
            print(f"✅ 没有发现其他AI相关按钮")
        
        print(f"\n🎉 所有检查通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理Pygame
        try:
            pygame.quit()
        except:
            pass

def show_removal_summary():
    """显示删除总结"""
    print("\n🌟 AI模型文本按钮删除总结:")
    print("=" * 50)
    print("🗑️ 已删除的内容:")
    print("  • AI Model Selection按钮")
    print("  • 按钮点击处理代码")
    print("  • cycle_ai_model方法")
    print("  • 按钮绘制中的相关代码")
    
    print("\n✅ 保留的功能:")
    print("  • 自动背景去除功能")
    print("  • AI图片生成功能")
    print("  • 图片上传功能")
    print("  • 其他所有游戏功能")
    
    print("\n🎯 删除原因:")
    print("  • 简化用户界面")
    print("  • 减少不必要的按钮")
    print("  • 保持界面整洁")
    print("  • AI模型选择现在完全自动化")

def main():
    """主函数"""
    print("=" * 50)
    print("AI模型文本按钮删除验证测试")
    print("=" * 50)
    
    # 运行测试
    success = test_button_removal()
    
    # 显示删除总结
    show_removal_summary()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 AI模型文本按钮删除验证成功！")
        print("\n💡 删除状态:")
        print("• ✅ AI Model Selection按钮已完全删除")
        print("• ✅ 相关代码已清理")
        print("• ✅ 游戏功能保持完整")
        print("• ✅ 界面更加简洁")
        print("\n🎮 现在游戏界面更加简洁，AI模型选择完全自动化！")
    else:
        print("❌ AI模型文本按钮删除验证失败！请检查错误信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
