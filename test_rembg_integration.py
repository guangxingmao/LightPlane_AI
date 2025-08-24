#!/usr/bin/env python3
"""
测试RemBG AI抠图集成
"""

import os
import cv2
import numpy as np
from PIL import Image

def test_rembg_integration():
    """测试RemBG集成"""
    print("🧪 测试RemBG AI抠图集成...")
    
    try:
        from background_remover import BackgroundRemover
        
        # 创建背景去除器
        remover = BackgroundRemover()
        print(f"✓ 背景去除器创建成功")
        print(f"📋 可用模型: {remover.get_available_models()}")
        print(f"🎯 当前模型: {remover.current_model}")
        
        # 检查RemBG是否可用
        if 'rembg' not in remover.get_available_models():
            print("❌ RemBG模型不可用")
            return False
        
        # 设置RemBG为当前模型
        remover.set_model('rembg')
        print(f"✓ 已设置RemBG模型")
        
        # 查找测试图片
        test_images = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # 排除一些特殊文件
                    if not file.startswith('.') and 'test' not in file.lower() and 'debug' not in file.lower():
                        test_images.append(os.path.join(root, file))
                        if len(test_images) >= 3:  # 取前3张图片测试
                            break
            if len(test_images) >= 3:
                break
        
        if not test_images:
            print("❌ 未找到测试图片")
            return False
        
        print(f"✓ 找到测试图片: {test_images[:3]}")
        
        # 测试每张图片
        for i, test_image in enumerate(test_images[:2]):  # 测试前2张
            print(f"\n🔍 测试图片 {i+1}: {test_image}")
            
            # 检查文件信息
            if os.path.exists(test_image):
                file_size = os.path.getsize(test_image)
                print(f"文件大小: {file_size} bytes")
                
                # 使用RemBG去除背景
                output_path = f"rembg_result_{i+1}_{os.path.basename(test_image)}"
                print(f"开始RemBG AI抠图...")
                
                try:
                    result = remover.remove_background(test_image, output_path)
                    
                    if result:
                        print(f"✓ RemBG AI抠图成功！")
                        
                        # 检查输出文件
                        if os.path.exists(output_path):
                            output_size = os.path.getsize(output_path)
                            print(f"输出文件大小: {output_size} bytes")
                            
                            # 分析结果
                            analyze_rembg_result(test_image, output_path)
                            
                            # 清理测试文件
                            try:
                                os.remove(output_path)
                                print("✓ 测试文件已清理")
                            except:
                                pass
                        else:
                            print("❌ 输出文件不存在")
                            return False
                    else:
                        print("❌ RemBG AI抠图失败")
                        return False
                        
                except Exception as e:
                    print(f"❌ RemBG AI抠图过程中发生错误: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print(f"❌ 测试图片不存在: {test_image}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_rembg_result(original_path, processed_path):
    """分析RemBG处理结果"""
    try:
        print(f"\n🔍 分析RemBG处理结果...")
        
        # 读取原始图片
        original = cv2.imread(original_path)
        if original is not None:
            print(f"原始图片尺寸: {original.shape}")
        
        # 尝试多种方式读取处理后的图片
        processed = None
        
        # 方法1: 使用cv2.IMREAD_UNCHANGED
        processed = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
        if processed is not None:
            print(f"✓ 使用cv2.IMREAD_UNCHANGED读取成功")
        else:
            # 方法2: 使用PIL读取
            try:
                pil_image = Image.open(processed_path)
                processed = np.array(pil_image)
                print(f"✓ 使用PIL读取成功")
            except Exception as e:
                print(f"❌ PIL读取失败: {e}")
                return
        
        if processed is None:
            print("❌ 无法读取处理后的图片")
            return
        
        print(f"处理后图片尺寸: {processed.shape}")
        
        # 检查是否有透明通道
        if len(processed.shape) == 3 and processed.shape[2] == 4:
            print("✓ 图片有4个通道（RGBA）")
            
            # 提取Alpha通道
            alpha = processed[:, :, 3]
            print(f"Alpha通道范围: {np.min(alpha)} - {np.max(alpha)}")
            
            # 计算透明区域比例
            transparent_pixels = np.sum(alpha < 128)
            total_pixels = alpha.shape[0] * alpha.shape[1]
            transparent_ratio = transparent_pixels / total_pixels * 100
            
            print(f"透明区域比例: {transparent_ratio:.1f}%")
            
            # 分析前景区域
            foreground_pixels = np.sum(alpha > 128)
            foreground_ratio = foreground_pixels / total_pixels * 100
            print(f"前景区域比例: {foreground_ratio:.1f}%")
            
            # 检查边缘质量
            edge_quality = analyze_edge_quality(alpha)
            print(f"边缘质量: {edge_quality}")
            
            # 保存Alpha通道用于查看
            alpha_path = f"rembg_alpha_{os.path.basename(processed_path)}"
            cv2.imwrite(alpha_path, alpha)
            print(f"Alpha通道已保存到: {alpha_path}")
            
            # 清理Alpha通道文件
            try:
                os.remove(alpha_path)
                print("✓ Alpha通道文件已清理")
            except:
                pass
            
        elif len(processed.shape) == 3 and processed.shape[2] == 3:
            print("⚠ 图片有3个通道（RGB），没有透明通道")
        else:
            print(f"⚠ 图片格式异常: {processed.shape}")
            
    except Exception as e:
        print(f"❌ 分析结果失败: {e}")
        import traceback
        traceback.print_exc()

def analyze_edge_quality(alpha_mask):
    """分析边缘质量"""
    try:
        # 使用Sobel算子检测边缘
        sobel_x = cv2.Sobel(alpha_mask, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(alpha_mask, cv2.CV_64F, 0, 1, ksize=3)
        
        # 计算边缘强度
        edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # 计算平均边缘强度
        avg_edge_strength = np.mean(edge_magnitude)
        
        if avg_edge_strength < 10:
            return "模糊"
        elif avg_edge_strength < 30:
            return "一般"
        elif avg_edge_strength < 60:
            return "清晰"
        else:
            return "非常清晰"
            
    except Exception as e:
        return f"分析失败: {e}"

def test_model_comparison():
    """测试不同模型的对比"""
    print("\n🔬 测试不同模型的对比...")
    
    try:
        from background_remover import BackgroundRemover
        
        remover = BackgroundRemover()
        available_models = remover.get_available_models()
        
        if len(available_models) < 2:
            print("⚠ 可用模型少于2个，无法进行对比测试")
            return
        
        # 测试图片
        test_image = "./images/bomb.png"
        if not os.path.exists(test_image):
            print(f"测试图片不存在: {test_image}")
            return
        
        print(f"📸 对比测试图片: {test_image}")
        
        # 测试每个模型
        for model in available_models:
            print(f"\n🎯 测试模型: {model}")
            remover.set_model(model)
            
            output_path = f"comparison_{model}_{os.path.basename(test_image)}"
            
            try:
                result = remover.remove_background(test_image, output_path)
                if result:
                    print(f"✓ {model} 模型测试成功")
                    
                    # 检查文件大小
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        print(f"  文件大小: {file_size} bytes")
                        
                        # 清理测试文件
                        try:
                            os.remove(output_path)
                        except:
                            pass
                else:
                    print(f"❌ {model} 模型测试失败")
                    
            except Exception as e:
                print(f"❌ {model} 模型测试出错: {e}")
        
    except Exception as e:
        print(f"❌ 模型对比测试失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("RemBG AI抠图集成测试")
    print("=" * 50)
    
    # 测试RemBG集成
    success = test_rembg_integration()
    
    # 测试模型对比
    test_model_comparison()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 RemBG集成测试成功！")
        print("\n💡 RemBG优势:")
        print("• 🚀 基于深度学习的AI抠图")
        print("• 🎯 自动识别前景物体")
        print("• ✨ 高质量的透明背景")
        print("• 🔄 支持多种图片格式")
        print("• ⚡ 处理速度快")
    else:
        print("❌ RemBG集成测试失败！")
        print("\n🔧 故障排除建议:")
        print("1. 检查RemBG是否正确安装")
        print("2. 检查Python环境和依赖包")
        print("3. 查看错误日志")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
