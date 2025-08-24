#!/usr/bin/env python3
"""
AI图片处理器 - 集成到飞机大战游戏中
用于处理AI生成的图片和上传的图片，自动去除背景
"""

import os
import pygame
import threading
import time
from background_remover import BackgroundRemover

class AIImageProcessor:
    """AI图片处理器类"""
    
    def __init__(self):
        self.background_remover = BackgroundRemover()
        self.processing_queue = []
        self.is_processing = False
        self.current_task = None
        
        # 处理状态
        self.processing_status = "idle"  # idle, processing, completed, error
        self.progress = 0
        self.status_message = ""
        
        # 支持的图片类型
        self.supported_types = ['player_plane', 'enemy_plane', 'background']
        
        # 输出目录
        self.output_dir = "processed_images"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 当前AI模型
        self.current_model = self.background_remover.current_model
    
    def get_available_models(self):
        """获取可用的AI模型"""
        return self.background_remover.get_available_models()
    
    def set_model(self, model_name):
        """设置AI模型"""
        success = self.background_remover.set_model(model_name)
        if success:
            self.current_model = model_name
        return success
    
    def process_image(self, image_path, image_type, model_name=None, callback=None):
        """处理图片 - 去除背景"""
        if not os.path.exists(image_path):
            print(f"图片文件不存在: {image_path}")
            return None
        
        # 添加到处理队列
        task = {
            'image_path': image_path,
            'image_type': image_type,
            'model_name': model_name,
            'callback': callback,
            'timestamp': time.time()
        }
        
        self.processing_queue.append(task)
        
        # 如果没有在处理，开始处理
        if not self.is_processing:
            self._start_processing()
        
        return True
    
    def _start_processing(self):
        """开始处理队列中的任务"""
        if self.is_processing or not self.processing_queue:
            return
        
        self.is_processing = True
        
        def processing_thread():
            while self.processing_queue:
                task = self.processing_queue.pop(0)
                self.current_task = task
                
                try:
                    self._process_single_image(task)
                except Exception as e:
                    print(f"处理图片失败: {e}")
                    self.processing_status = "error"
                    self.status_message = f"处理失败: {str(e)}"
                
                self.current_task = None
            
            self.is_processing = False
            self.processing_status = "idle"
        
        threading.Thread(target=processing_thread, daemon=True).start()
    
    def _process_single_image(self, task):
        """处理单个图片"""
        image_path = task['image_path']
        image_type = task['image_type']
        model_name = task['model_name']
        callback = task['callback']
        
        print(f"开始处理图片: {image_type} - {image_path}")
        
        self.processing_status = "processing"
        self.progress = 0
        self.status_message = f"正在处理 {image_type}..."
        
        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_name = f"{image_type}_{base_name}_processed.png"
        output_path = os.path.join(self.output_dir, output_name)
        
        # 更新进度
        self.progress = 20
        self.status_message = f"正在加载 {image_type} 图片..."
        
        # 去除背景
        self.progress = 40
        self.status_message = f"正在使用AI模型去除背景..."
        
        try:
            result = self.background_remover.remove_background(
                image_path, 
                output_path, 
                model_name
            )
            
            if result:
                self.progress = 80
                self.status_message = f"正在优化 {image_type} 图片..."
                
                # 转换为Pygame surface
                pygame_surface = self._load_processed_image(output_path)
                
                if pygame_surface:
                    self.progress = 100
                    self.status_message = f"{image_type} 处理完成!"
                    self.processing_status = "completed"
                    
                    # 调用回调函数
                    if callback:
                        callback({
                            'type': image_type,
                            'original_path': image_path,
                            'processed_path': output_path,
                            'pygame_surface': pygame_surface,
                            'status': 'success'
                        })
                    
                    print(f"图片处理成功: {output_path}")
                else:
                    raise Exception("无法加载处理后的图片")
            else:
                raise Exception("背景去除失败")
                
        except Exception as e:
            self.processing_status = "error"
            self.status_message = f"处理失败: {str(e)}"
            print(f"图片处理失败: {e}")
            
            # 调用回调函数（失败情况）
            if callback:
                callback({
                    'type': image_type,
                    'original_path': image_path,
                    'processed_path': None,
                    'pygame_surface': None,
                    'status': 'error',
                    'error': str(e)
                })
    
    def _load_processed_image(self, image_path):
        """加载处理后的图片为Pygame surface"""
        try:
            if os.path.exists(image_path):
                surface = pygame.image.load(image_path)
                # 确保图片有透明通道
                if surface.get_alpha() is None:
                    # 如果没有透明通道，创建一个
                    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                    new_surface.blit(surface, (0, 0))
                    return new_surface
                return surface
        except Exception as e:
            print(f"加载处理后的图片失败: {e}")
        
        return None
    
    def process_pygame_surface(self, surface, image_type, model_name=None, callback=None):
        """处理Pygame surface - 去除背景"""
        # 保存为临时文件
        temp_path = f"temp_{image_type}_{int(time.time())}.png"
        
        try:
            # 尝试保存Pygame surface
            print(f"正在保存Pygame surface到临时文件: {temp_path}")
            pygame.image.save(surface, temp_path)
            
            # 检查文件是否成功保存
            if not os.path.exists(temp_path):
                raise Exception("临时文件保存失败")
            
            file_size = os.path.getsize(temp_path)
            if file_size == 0:
                raise Exception("临时文件为空")
            
            print(f"临时文件保存成功，大小: {file_size} bytes")
            
            # 创建一个包装回调函数，在处理完成后清理临时文件
            def wrapped_callback(result):
                try:
                    # 调用原始回调函数
                    if callback:
                        callback(result)
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                            print(f"临时文件已清理: {temp_path}")
                        except Exception as e:
                            print(f"清理临时文件失败: {e}")
            
            # 处理临时文件，使用包装的回调函数
            return self.process_image(temp_path, image_type, model_name, wrapped_callback)
            
        except Exception as e:
            print(f"保存Pygame surface失败: {e}")
            # 尝试使用PIL保存
            try:
                print("尝试使用PIL保存...")
                from PIL import Image
                import numpy as np
                
                # 将Pygame surface转换为PIL Image
                pil_image = self._pygame_to_pil(surface)
                pil_image.save(temp_path)
                
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    print("使用PIL保存成功")
                    
                    # 创建包装回调函数
                    def wrapped_callback(result):
                        try:
                            if callback:
                                callback(result)
                        finally:
                            if os.path.exists(temp_path):
                                try:
                                    os.remove(temp_path)
                                    print(f"临时文件已清理: {temp_path}")
                                except Exception as e:
                                    print(f"清理临时文件失败: {e}")
                    
                    return self.process_image(temp_path, image_type, model_name, wrapped_callback)
                else:
                    raise Exception("PIL保存也失败")
                    
            except Exception as pil_error:
                print(f"PIL保存也失败: {pil_error}")
                # 清理临时文件
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                raise Exception(f"无法保存Pygame surface: {e}, PIL也失败: {pil_error}")
    
    def get_processing_status(self):
        """获取处理状态"""
        return {
            'status': self.processing_status,
            'progress': self.progress,
            'message': self.status_message,
            'is_processing': self.is_processing,
            'queue_length': len(self.processing_queue),
            'current_task': self.current_task
        }
    
    def clear_queue(self):
        """清空处理队列"""
        self.processing_queue.clear()
        self.processing_status = "idle"
        self.progress = 0
        self.status_message = "队列已清空"
    
    def get_processed_images(self):
        """获取已处理的图片列表"""
        processed_images = {}
        
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                if filename.endswith('_processed.png'):
                    # 解析文件名获取类型
                    parts = filename.replace('_processed.png', '').split('_', 1)
                    if len(parts) == 2:
                        image_type, base_name = parts
                        if image_type in self.supported_types:
                            if image_type not in processed_images:
                                processed_images[image_type] = []
                            processed_images[image_type].append({
                                'filename': filename,
                                'path': os.path.join(self.output_dir, filename),
                                'base_name': base_name
                            })
        
        return processed_images
    
    def _pygame_to_pil(self, pygame_surface):
        """将Pygame surface转换为PIL Image"""
        try:
            # 获取surface数据
            string_image = pygame.image.tostring(pygame_surface, "RGBA", False)
            
            # 创建PIL Image
            pil_image = Image.frombytes("RGBA", pygame_surface.get_size(), string_image)
            
            return pil_image
        except Exception as e:
            print(f"Pygame to PIL转换失败: {e}")
            # 尝试使用RGB模式
            try:
                string_image = pygame.image.tostring(pygame_surface, "RGB", False)
                pil_image = Image.frombytes("RGB", pygame_surface.get_size(), string_image)
                return pil_image
            except Exception as e2:
                print(f"RGB转换也失败: {e2}")
                raise Exception(f"无法转换Pygame surface: {e}, RGB也失败: {e2}")
    
    def load_processed_image(self, image_type, base_name):
        """加载已处理的图片"""
        processed_images = self.get_processed_images()
        
        if image_type in processed_images:
            for img_info in processed_images[image_type]:
                if img_info['base_name'] == base_name:
                    return self._load_processed_image(img_info['path'])
        
        return None

# 使用示例
if __name__ == "__main__":
    # 创建AI图片处理器
    processor = AIImageProcessor()
    
    # 检查可用模型
    print("可用模型:", processor.get_available_models())
    
    # 测试处理图片
    test_image = "test_airplane.png"
    if os.path.exists(test_image):
        print(f"测试处理图片: {test_image}")
        
        def on_complete(result):
            print(f"处理完成: {result}")
        
        # 处理图片
        processor.process_image(test_image, "player_plane", callback=on_complete)
        
        # 等待处理完成
        while processor.is_processing:
            status = processor.get_processing_status()
            print(f"状态: {status['status']}, 进度: {status['progress']}%, 消息: {status['message']}")
            time.sleep(0.5)
        
        print("处理完成!")
    else:
        print(f"测试图片 {test_image} 不存在")
