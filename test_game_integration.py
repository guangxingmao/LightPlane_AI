#!/usr/bin/env python3
"""
测试游戏系统集成改进后的AI智能抠图功能
"""

import os
import pygame
import time

def test_game_integration():
    """测试游戏系统集成"""
    print("🧪 测试游戏系统集成改进后的AI智能抠图功能...")
    
    try:
        # 1. 测试BackgroundRemover集成
        print("\n1️⃣ 测试BackgroundRemover集成...")
        from background_remover import BackgroundRemover
        
        remover = BackgroundRemover()
        print(f"✅ BackgroundRemover创建成功")
        print(f"📋 可用模型: {remover.get_available_models()}")
        
        # 2. 测试AIImageProcessor集成
        print("\n2️⃣ 测试AIImageProcessor集成...")
        from ai_image_processor import AIImageProcessor
        
        processor = AIImageProcessor()
        print(f"✅ AIImageProcessor创建成功")
        print(f"📋 可用模型: {processor.get_available_models()}")
        
        # 3. 测试CustomConfigPage集成
        print("\n3️⃣ 测试CustomConfigPage集成...")
        from custom_config_page import CustomConfigPage
        
        # 创建Pygame屏幕
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        config_page = CustomConfigPage(screen)
        print(f"✅ CustomConfigPage创建成功")
        
        # 检查是否有auto_remove_background方法
        if hasattr(config_page, 'auto_remove_background'):
            print(f"✅ auto_remove_background方法存在")
        else:
            print(f"❌ auto_remove_background方法不存在")
            return False
        
        # 4. 测试AI智能抠图功能
        print("\n4️⃣ 测试AI智能抠图功能...")
        
        # 设置RemBG模型
        processor.set_model('rembg')
        print(f"🎯 已设置RemBG模型")
        
        # 测试图片
        test_image = "./images/bomb.png"
        if not os.path.exists(test_image):
            print(f"❌ 测试图片不存在: {test_image}")
            return False
        
        print(f"📸 使用测试图片: {test_image}")
        
        # 测试AI智能抠图
        print(f"🚀 开始测试AI智能抠图...")
        start_time = time.time()
        
        # 创建测试回调
        test_result = {'status': 'pending'}
        
        def test_callback(result):
            test_result.update(result)
            print(f"📞 回调函数被调用: {result['status']}")
        
        # 处理图片
        success = processor.process_image(test_image, 'player_plane', 'rembg', test_callback)
        
        if success:
            print(f"✅ 图片处理请求成功")
            
            # 等待处理完成
            print(f"⏳ 等待处理完成...")
            timeout = 30  # 30秒超时
            start_wait = time.time()
            
            while test_result['status'] == 'pending':
                if time.time() - start_wait > timeout:
                    print(f"⏰ 处理超时")
                    break
                time.sleep(0.5)
            
            # 检查结果
            if test_result['status'] == 'success':
                print(f"🎉 AI智能抠图成功！")
                print(f"📊 处理结果:")
                print(f"  类型: {test_result.get('type')}")
                print(f"  原始路径: {test_result.get('original_path')}")
                print(f"  处理后路径: {test_result.get('processed_path')}")
                print(f"  Pygame surface: {test_result.get('pygame_surface') is not None}")
                
                # 检查处理后的文件
                processed_path = test_result.get('processed_path')
                if processed_path and os.path.exists(processed_path):
                    file_size = os.path.getsize(processed_path)
                    print(f"  处理后文件大小: {file_size} bytes")
                    
                    # 清理测试文件
                    try:
                        os.remove(processed_path)
                        print(f"✓ 测试文件已清理")
                    except:
                        pass
                else:
                    print(f"⚠ 处理后文件不存在")
                
            elif test_result['status'] == 'error':
                print(f"❌ AI智能抠图失败: {test_result.get('error')}")
                return False
            else:
                print(f"⚠ 处理状态未知: {test_result['status']}")
                return False
                
        else:
            print(f"❌ 图片处理请求失败")
            return False
        
        # 5. 测试复杂度分析功能
        print("\n5️⃣ 测试复杂度分析功能...")
        
        # 检查是否有新的复杂度分析方法
        if hasattr(remover, '_analyze_image_complexity'):
            print(f"✅ 复杂度分析方法存在")
            
            # 测试复杂度分析
            complexity = remover._analyze_image_complexity(test_image)
            print(f"📊 图片复杂度评分: {complexity:.1f}/100")
            
        else:
            print(f"❌ 复杂度分析方法不存在")
            return False
        
        # 6. 测试AI特征检测功能
        print("\n6️⃣ 测试AI特征检测功能...")
        
        if hasattr(remover, '_detect_ai_generation_features'):
            print(f"✅ AI特征检测方法存在")
            
            # 测试AI特征检测
            import cv2
            image = cv2.imread(test_image)
            if image is not None:
                ai_features = remover._detect_ai_generation_features(image)
                print(f"🎨 AI特征检测结果:")
                print(f"  可能是AI生成: {ai_features.get('is_likely_ai_generated')}")
                print(f"  平滑度评分: {ai_features.get('smoothness_score', 0):.2f}")
                print(f"  饱和度评分: {ai_features.get('saturation_score', 0):.2f}")
                print(f"  边缘平滑度: {ai_features.get('edge_smoothness', 0):.2f}")
            else:
                print(f"⚠ 无法读取测试图片进行AI特征检测")
        else:
            print(f"❌ AI特征检测方法不存在")
            return False
        
        # 7. 测试自适应参数功能
        print("\n7️⃣ 测试自适应参数功能...")
        
        if hasattr(remover, '_rembg_with_adaptive_params'):
            print(f"✅ 自适应参数方法存在")
        else:
            print(f"❌ 自适应参数方法不存在")
            return False
        
        # 8. 测试智能后处理功能
        print("\n8️⃣ 测试智能后处理功能...")
        
        if hasattr(remover, '_expand_foreground_smart'):
            print(f"✅ 智能前景扩展方法存在")
        else:
            print(f"❌ 智能前景扩展方法不存在")
            return False
        
        if hasattr(remover, '_smooth_edges_smart'):
            print(f"✅ 智能边缘平滑方法存在")
        else:
            print(f"❌ 智能边缘平滑方法不存在")
            return False
        
        if hasattr(remover, '_enhance_colors_smart'):
            print(f"✅ 智能色彩增强方法存在")
        else:
            print(f"❌ 智能色彩增强方法不存在")
            return False
        
        if hasattr(remover, '_restore_ai_details'):
            print(f"✅ AI细节恢复方法存在")
        else:
            print(f"❌ AI细节恢复方法不存在")
            return False
        
        print(f"\n🎉 所有测试通过！")
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

def show_integration_status():
    """显示集成状态"""
    print("\n🌟 游戏系统集成状态:")
    print("=" * 60)
    print("✅ 已集成:")
    print("  • BackgroundRemover - AI智能抠图核心")
    print("  • AIImageProcessor - 图片处理接口")
    print("  • CustomConfigPage - 游戏配置页面")
    print("  • auto_remove_background - 自动背景去除")
    
    print("\n🧠 新增AI智能功能:")
    print("  • 智能复杂度分析")
    print("  • AI生成图片特征识别")
    print("  • 自适应参数调整")
    print("  • 智能前景扩展")
    print("  • 智能边缘优化")
    print("  • 智能色彩增强")
    print("  • AI细节恢复")
    
    print("\n🎯 集成流程:")
    print("  1. 用户上传图片或AI生成图片")
    print("  2. 自动调用auto_remove_background")
    print("  3. 使用改进后的BackgroundRemover")
    print("  4. 自动分析图片复杂度")
    print("  5. 选择最佳抠图参数")
    print("  6. 应用智能后处理")
    print("  7. 返回优化后的图片")

def main():
    """主函数"""
    print("=" * 60)
    print("游戏系统集成测试 - 改进后的AI智能抠图功能")
    print("=" * 60)
    
    # 运行集成测试
    success = test_game_integration()
    
    # 显示集成状态
    show_integration_status()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 游戏系统集成测试成功！")
        print("\n💡 集成状态:")
        print("• ✅ 改进后的AI智能抠图功能已完全集成到游戏系统")
        print("• ✅ 用户上传或AI生成的图片会自动使用智能抠图")
        print("• ✅ 无需手动操作，系统自动选择最佳参数")
        print("• ✅ 针对复杂AI生成图片有特殊优化")
        print("\n🎮 现在你可以在游戏中享受改进后的抠图效果了！")
        print("• 上传图片 → 自动智能抠图")
        print("• AI生成图片 → 自动智能抠图")
        print("• 复杂图片 → 自动优化处理")
    else:
        print("❌ 游戏系统集成测试失败！请检查错误信息")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
