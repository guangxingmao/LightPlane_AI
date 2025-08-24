#!/usr/bin/env python3
"""
自定义配置页面 - 支持图片上传和AI生成
"""

import pygame
import os
import sys
import threading
import time
from pyqt5_file_selector import select_file
from local_image_generator import generate_image_local

class CustomConfigPage:
    def __init__(self, screen, width=None, height=None):
        self.screen = screen
        if width and height:
            self.width, self.height = width, height
        else:
            self.width, self.height = screen.get_size()
        
        # 初始化配置
        self.initialize_config()
    
    def initialize_config(self, preserve_cache=False):
        """初始化配置页面"""
        print("🔄 初始化自定义配置页面...")
        
        # 字体
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # 颜色
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (100, 150, 255)
        self.GREEN = (100, 255, 100)
        self.RED = (255, 100, 100)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (100, 100, 100)
        
        # 传统模式图片尺寸 - 修正为实际图片尺寸
        self.TRADITIONAL_SIZES = {
            'player_plane': (57, 46),    # life.png 实际尺寸（玩家生命值图标）
            'enemy_plane': (43, 57),     # enemy1.png 实际尺寸
            'background': (700, 480)     # background.png 实际尺寸
        }
        
        # 默认提示词 - 简单直接，强调高清完整飞机
        self.default_prompts = {
            'player_plane': 'airplane, high resolution, complete aircraft, full plane',
            'enemy_plane': 'airplane, high resolution, complete aircraft, full plane',
            'background': 'space, stars, high resolution'
        }
        
        # 保留或重置配置缓存
        if not preserve_cache or not hasattr(self, 'config_cache'):
            self.config_cache = {
                'player_plane': None,
                'enemy_plane': None,
                'background': None
            }
            print("🗑️ 配置缓存已重置")
        else:
            print("💾 保留现有配置缓存")
        
        # 重置输入框
        self.input_boxes = []
        self.selected_input = None
        
        # 重置预览区域
        self.preview_areas = {}
        
        # 重置按钮
        self.buttons = {}
        
        # 重置状态信息
        self.status_message = ""
        self.status_color = self.GREEN
        self.show_status_flag = False  # 改名避免与方法冲突
        self.status_timer = 0
        
        # 重置AI生成状态
        self.generating = False
        self.generation_progress = 0
        
        # 重置待上传文件
        self.pending_upload = None
        
        # 重置强制重绘标志
        self.force_redraw = False
        
        # 创建UI元素
        self.create_ui_elements()
        
        # 恢复预览图片（如果保留缓存）
        if preserve_cache and hasattr(self, 'config_cache'):
            self.restore_preview_images()
        
        # 加载背景
        self.background = self.load_background()
        
        print("✅ 自定义配置页面初始化完成")
    
    def restore_preview_images(self):
        """恢复预览图片到预览区域"""
        print("🔄 恢复预览图片...")
        for image_type, cached_image in self.config_cache.items():
            if cached_image and image_type in self.preview_areas:
                # 使用保存的预览尺寸
                preview_size = self.preview_areas[image_type].get('preview_size', (512, 512))
                
                # 缩放到预览尺寸
                preview_image = pygame.transform.smoothscale(cached_image, preview_size)
                self.preview_areas[image_type]['image'] = preview_image
                print(f"✅ 恢复 {image_type} 预览图片，预览尺寸: {preview_size}")
    
    def load_background(self):
        """加载背景图片"""
        try:
            bg_path = os.path.join('images', 'background.png')
            if os.path.exists(bg_path):
                bg = pygame.image.load(bg_path)
                return pygame.transform.scale(bg, (self.width, self.height))
            else:
                return None
        except:
            return None
    
    def create_ui_elements(self):
        """创建UI元素"""
        # 创建输入框
        self.create_input_boxes()
        
        # 创建预览区域
        self.create_preview_areas()
        
        # 创建按钮
        self.create_buttons()
    
    def create_input_boxes(self):
        """创建输入框"""
        self.input_boxes = []
        
        # 输入框高度 - 确保能容纳4行文字
        line_height = 32  # 文字行高
        input_height = line_height * 4 + 20  # 4行文字 + 上下边距
        
        # 三栏布局，改进间距
        column_width = (self.width - 120) // 3  # 留出更多边距
        start_x = 60
        
        # 栏目标题
        titles = ['Player Plane', 'Enemy Plane', 'Background']
        
        for i, (image_type, prompt) in enumerate(self.default_prompts.items()):
            x = start_x + i * column_width
            y = 200  # 调整Y位置，为标题和按钮留出空间
            
            # 输入框宽度调整
            input_width = column_width - 80
            
            # 输入框
            input_box = {
                'rect': pygame.Rect(x, y, input_width, input_height),
                'text': '',
                'placeholder': prompt,
                'active': False,
                'type': image_type,
                'title': titles[i]
            }
            self.input_boxes.append(input_box)
            
            # 清除按钮位置调整
            clear_button = {
                'rect': pygame.Rect(x + input_width + 10, y + (input_height - 30) // 2, 60, 30),
                'text': 'Clear',
                'type': f'clear_{image_type}'
            }
            self.buttons[f'clear_{image_type}'] = clear_button
    
    def create_preview_areas(self):
        """创建预览区域"""
        self.preview_areas = {}
        
        # 三栏布局，与输入框保持一致
        column_width = (self.width - 120) // 3
        start_x = 60
        
        for i, (image_type, size) in enumerate(self.TRADITIONAL_SIZES.items()):
            x = start_x + i * column_width
            y = 460  # 调整位置，在按钮下方
            
            # 预览区域大小与preview尺寸一致
            # 对于background，使用较小的预览尺寸以避免过大
            if image_type == 'background':
                # background使用较小的预览尺寸，保持宽高比
                max_preview_width = 200  # 最大预览宽度
                scale_factor = max_preview_width / size[0]
                preview_size = (int(size[0] * scale_factor), int(size[1] * scale_factor))
            else:
                # 其他图片使用3倍目标尺寸
                preview_size = (size[0] * 3, size[1] * 3)
            
            # 计算预览框位置，使其与输入框水平居中
            input_width = column_width - 80  # 输入框宽度
            preview_x = x + (input_width - preview_size[0]) // 2  # 水平居中
            
            preview_rect = pygame.Rect(preview_x, y, preview_size[0], preview_size[1])
            self.preview_areas[image_type] = {
                'rect': preview_rect,
                'image': None,
                'size': size,
                'preview_size': preview_size  # 保存预览尺寸信息
            }
    
    def create_buttons(self):
        """创建按钮"""
        # 三栏布局，与输入框保持一致
        column_width = (self.width - 120) // 3
        start_x = 60
        
        for i, image_type in enumerate(self.default_prompts.keys()):
            x = start_x + i * column_width
            y = 360  # 调整位置，在输入框下方
            
            # 计算输入框宽度用于居中计算
            input_width = column_width - 80
            
            # 两个按钮的总宽度
            total_button_width = 90 + 90 + 20  # 两个按钮宽度 + 间距
            
            # 计算按钮组的起始位置，使其在输入框内水平居中
            buttons_start_x = x + (input_width - total_button_width) // 2
            
            # Upload按钮
            upload_button = {
                'rect': pygame.Rect(buttons_start_x, y, 90, 35),
                'text': 'Upload',
                'type': f'upload_{image_type}'
            }
            self.buttons[f'upload_{image_type}'] = upload_button
            
            # AI Gen按钮 - 在upload按钮右侧
            ai_gen_button = {
                'rect': pygame.Rect(buttons_start_x + 110, y, 90, 35),
                'text': 'AI Gen',
                'type': f'ai_gen_{image_type}'
            }
            self.buttons[f'ai_gen_{image_type}'] = ai_gen_button
        
        # 顶部按钮 - 与标题垂直居中
        button_y = 25  # 标题在Y=50，按钮高度50，所以从Y=25开始
        
        # Back按钮 - 改进样式，放在左上角，小一号
        back_button = {
            'rect': pygame.Rect(60, button_y, 120, 40),  # 从140x50改为120x40
            'text': 'Back',
            'type': 'back'
        }
        self.buttons['back'] = back_button
        
        # Complete按钮 - 改进样式，放在右上角，小一号
        complete_button = {
            'rect': pygame.Rect(self.width - 180, button_y, 120, 40),  # 从140x50改为120x40，位置也相应调整
            'text': 'Complete',
            'type': 'complete'
        }
        self.buttons['complete'] = complete_button
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                result = self.handle_click(event.pos)
                if result:
                    return result
        
        elif event.type == pygame.KEYDOWN:
            if self.selected_input is not None:
                if event.key == pygame.K_RETURN:
                    self.selected_input = None
                elif event.key == pygame.K_BACKSPACE:
                    self.input_boxes[self.selected_input]['text'] = self.input_boxes[self.selected_input]['text'][:-1]
                else:
                    # 智能输入处理，支持换行
                    current_text = self.input_boxes[self.selected_input]['text']
                    new_char = event.unicode
                    
                    # 如果按了回车键，添加换行符
                    if event.unicode == '\r':
                        new_char = '\n'
                    
                    # 计算添加新字符后的文字
                    test_text = current_text + new_char
                    
                    # 检查是否需要换行
                    if new_char == '\n':
                        # 换行符直接添加
                        self.input_boxes[self.selected_input]['text'] = test_text
                    else:
                        # 检查当前行是否会超出宽度
                        lines = test_text.split('\n')
                        current_line = lines[-1]  # 当前行
                        
                        # 计算当前行的宽度
                        line_surface = self.text_font.render(current_line, True, self.BLACK)
                        line_width = line_surface.get_width()
                        
                        # 如果当前行超出宽度，自动换行
                        if line_width > self.input_boxes[self.selected_input]['rect'].width - 20:
                            # 自动换行
                            test_text = current_text + '\n' + new_char
                        
                        # 检查总行数是否超过4行
                        total_lines = len(test_text.split('\n'))
                        if total_lines <= 4:
                            self.input_boxes[self.selected_input]['text'] = test_text
                    
                self.force_redraw = True
        
        return None
    
    def handle_click(self, pos):
        """处理点击事件"""
        # 检查输入框点击
        for i, input_box in enumerate(self.input_boxes):
            if input_box['rect'].collidepoint(pos):
                self.select_input(i)
                return None
        
        # 检查按钮点击
        for button in self.buttons.values():
            if button['rect'].collidepoint(pos):
                result = self.handle_button_click(button['type'])
                return result
        
        # 点击其他地方，取消选择
        self.selected_input = None
        self.force_redraw = True
        return None
    
    def select_input(self, index):
        """选择输入框"""
        self.selected_input = index
        for i, input_box in enumerate(self.input_boxes):
            input_box['active'] = (i == index)
        self.force_redraw = True
    
    def handle_button_click(self, button_type):
        """处理按钮点击"""
        if button_type == 'back':
            print("🔄 点击Back按钮，清除缓存并返回主菜单")
            self.clear_cache()
            return 'back'
        
        elif button_type == 'complete':
            print("✅ 点击Complete按钮，返回配置信息")
            config = self.get_config()
            print(f"📋 当前配置: {config}")
            return {
                'type': 'custom_game',
                'config': config
            }
        
        elif button_type.startswith('upload_'):
            image_type = button_type.replace('upload_', '')
            print(f"📁 点击Upload按钮: {image_type}")
            self.start_upload(image_type)
        
        elif button_type.startswith('ai_gen_'):
            image_type = button_type.replace('ai_gen_', '')
            print(f"🎨 点击AI Gen按钮: {image_type}")
            self.start_ai_generation(image_type)
        
        elif button_type.startswith('clear_'):
            image_type = button_type.replace('clear_', '')
            print(f"🧹 点击Clear按钮: {image_type}")
            self.clear_input_text(image_type)
    
    def clear_input_text(self, image_type):
        """清除输入框文字"""
        for input_box in self.input_boxes:
            if input_box['type'] == image_type:
                input_box['text'] = ''
                self.force_redraw = True
                break
    
    def start_upload(self, image_type):
        """开始上传"""
        print(f"🔄 开始上传 {image_type} 图片...")
        
        def upload_thread():
            try:
                # 显示上传中状态
                self.show_status(f"正在选择 {image_type} 图片...", self.BLUE)
                
                # 调用文件选择器
                file_path = select_file(image_type)
                
                if file_path and os.path.exists(file_path):
                    print(f"✅ 选择文件: {file_path}")
                    self.pending_upload = (image_type, file_path)
                else:
                    if file_path:
                        print(f"❌ 文件不存在: {file_path}")
                        self.show_status(f"文件不存在: {file_path}", self.RED)
                    else:
                        print("ℹ️ 用户取消了文件选择")
                        self.show_status("已取消文件选择", self.BLUE)
                        
            except Exception as e:
                print(f"❌ 上传失败: {e}")
                self.show_status(f"上传失败: {str(e)}", self.RED)
        
        # 启动上传线程
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def start_ai_generation(self, image_type):
        """开始AI生成"""
        if self.generating:
            return
        
        self.generating = True
        self.generation_progress = 0
        
        def generation_thread():
            try:
                # 获取用户输入
                user_input = ""
                for input_box in self.input_boxes:
                    if input_box['type'] == image_type:
                        user_input = input_box['text'].strip()
                        break
                
                # 构建提示词 - 包含target尺寸的8倍信息
                target_size = self.TRADITIONAL_SIZES.get(image_type, (512, 512))
                target_width, target_height = target_size
                size_info = f"size {target_width * 8}x{target_height * 8} pixels"
                
                if user_input:
                    prompt = f"{user_input}, {self.default_prompts[image_type]}, {size_info}"
                else:
                    prompt = f"{self.default_prompts[image_type]}, {size_info}"
                
                # 获取目标尺寸，但使用更大的生成尺寸以提高质量
                target_size = self.TRADITIONAL_SIZES.get(image_type, (512, 512))
                original_width, original_height = target_size
                
                # 使用更大的生成尺寸以提高AI生成质量
                # 计算合适的生成尺寸（至少512x512或保持宽高比）
                if image_type == 'background':
                    # 背景使用较大尺寸
                    gen_width = 512
                    gen_height = int(512 * original_height / original_width)
                else:
                    # 飞机图片使用固定的较大尺寸
                    gen_width = 512
                    gen_height = 512
                
                # 调整为8的倍数（Stable Diffusion要求）
                width = ((gen_width + 7) // 8) * 8
                height = ((gen_height + 7) // 8) * 8
                
                print(f"📐 目标尺寸: {original_width}x{original_height}")
                print(f"📐 生成尺寸（提高质量）: {width}x{height}")
                
                # 生成图片 - 增加步数提高质量
                self.generation_progress = 5
                
                # 模拟AI生成的不同阶段进度
                # 阶段1: 模型加载和初始化 (5% -> 20%)
                for i in range(5, 21, 3):
                    self.generation_progress = i
                    time.sleep(0.1)  # 短暂延迟让进度条可见
                
                # 阶段2: 文本编码 (20% -> 40%)
                for i in range(20, 41, 4):
                    self.generation_progress = i
                    time.sleep(0.1)
                
                # 阶段3: 扩散过程 (40% -> 90%)
                for i in range(40, 91, 5):
                    self.generation_progress = i
                    time.sleep(0.2)  # 扩散过程需要更多时间
                
                # 阶段4: 图像生成 (90% -> 95%)
                for i in range(90, 96, 1):
                    self.generation_progress = i
                    time.sleep(0.1)
                
                # 实际生成图片
                image = generate_image_local(prompt, width, height, steps=20)
                
                # 阶段5: 后处理 (95% -> 100%)
                self.generation_progress = 95
                time.sleep(0.1)
                self.generation_progress = 100
                time.sleep(0.2)  # 让100%状态保持一下
                
                if image:
                    # 总是需要缩放到目标尺寸（因为我们用了更大的生成尺寸）
                    print(f"🔄 缩放图片: {width}x{height} -> {target_size}")
                    # 使用高质量缩放算法
                    scaled_image = pygame.transform.smoothscale(image, target_size)
                    
                    # 更新预览区域（缩放到预览尺寸）
                    if image_type in self.preview_areas:
                        # 获取预览尺寸
                        preview_size = self.preview_areas[image_type].get('preview_size', (target_size[0] * 3, target_size[1] * 3))
                        preview_image = pygame.transform.smoothscale(scaled_image, preview_size)
                        self.preview_areas[image_type]['image'] = preview_image
                        print(f"✅ 更新AI预览区域: {image_type}，预览尺寸: {preview_size}")
                    
                    # 更新配置缓存（保存目标尺寸的图片）
                    self.config_cache[image_type] = scaled_image
                    print(f"✅ 更新AI配置缓存: {image_type}，目标尺寸: {target_size}")
                    
                    self.show_status(f"{image_type} AI生成成功！", self.GREEN)
                else:
                    self.show_status(f"{image_type} AI生成失败", self.RED)
                
            except Exception as e:
                print(f"AI生成失败: {e}")
                self.show_status(f"AI生成失败: {e}", self.RED)
            finally:
                self.generating = False
                self.generation_progress = 0
        
        threading.Thread(target=generation_thread, daemon=True).start()
    
    def show_status(self, message, color):
        """显示状态信息"""
        self.status_message = message
        self.status_color = color
        self.show_status_flag = True
        self.status_timer = time.time()
    
    def clear_cache(self):
        """清除缓存"""
        self.config_cache = {
            'player_plane': None,
            'enemy_plane': None,
            'background': None
        }
        for preview in self.preview_areas.values():
            preview['image'] = None
        self.force_redraw = True
    
    def get_config(self):
        """获取配置"""
        return self.config_cache
    
    def update(self):
        """更新状态"""
        current_time = time.time()
        
        # 检查状态信息显示时间
        if self.show_status_flag and current_time - self.status_timer > 3:
            self.show_status_flag = False
        
        # 处理待上传文件
        if self.pending_upload:
            image_type, file_path = self.pending_upload
            self.pending_upload = None
            self.process_uploaded_file(image_type, file_path)
        
        # 更新AI生成进度 - 现在由生成线程控制，这里不需要自动递增
        # 进度条更新逻辑已移到AI生成线程中，确保与实际生成过程同步
    
    def process_uploaded_file(self, image_type, file_path):
        """处理上传的文件"""
        try:
            print(f"🔄 处理上传文件: {image_type} - {file_path}")
            
            if not os.path.exists(file_path):
                self.show_status(f"文件不存在: {file_path}", self.RED)
                return
            
            # 检查文件类型
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
            file_ext = os.path.splitext(file_path.lower())[1]
            if file_ext not in valid_extensions:
                self.show_status(f"不支持的文件格式: {file_ext}", self.RED)
                return
            
            # 加载图片
            try:
                image = pygame.image.load(file_path)
                print(f"✅ 成功加载图片，原始尺寸: {image.get_size()}")
            except pygame.error as e:
                self.show_status(f"无法加载图片: {str(e)}", self.RED)
                return
            
            # 获取目标尺寸
            target_size = self.TRADITIONAL_SIZES.get(image_type, (512, 512))
            target_width, target_height = target_size
            
            # 缩放图片到目标尺寸 - 使用高质量缩放
            scaled_image = pygame.transform.smoothscale(image, target_size)
            print(f"✅ 图片已缩放至目标尺寸: {target_size}")
            
            # 更新预览区域（缩放到预览尺寸）
            if image_type in self.preview_areas:
                # 获取预览尺寸
                preview_size = self.preview_areas[image_type].get('preview_size', (target_size[0] * 3, target_size[1] * 3))
                preview_image = pygame.transform.smoothscale(scaled_image, preview_size)
                self.preview_areas[image_type]['image'] = preview_image
                print(f"✅ 更新预览区域: {image_type}，预览尺寸: {preview_size}")
            
            # 更新配置缓存（保存目标尺寸的图片）
            self.config_cache[image_type] = scaled_image
            print(f"✅ 更新配置缓存: {image_type}，目标尺寸: {target_size}")
            
            # 显示成功消息
            self.show_status(f"{image_type} 上传成功！", self.GREEN)
            self.force_redraw = True
            
        except Exception as e:
            print(f"❌ 处理上传文件失败: {e}")
            import traceback
            traceback.print_exc()
            self.show_status(f"处理文件失败: {str(e)}", self.RED)
    
    def draw(self):
        """绘制页面"""
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BLACK)
        
        # 绘制标题
        title = self.title_font.render("Custom Configuration", True, self.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # 绘制输入框
        self.draw_input_boxes()
        
        # 绘制预览区域
        self.draw_preview_areas()
        
        # 绘制按钮
        self.draw_buttons()
        
        # 绘制状态信息
        if self.show_status_flag:
            self.draw_status_info()
        
        # 绘制AI生成进度
        if self.generating:
            self.draw_generation_progress()
        
        # 重置强制重绘标志
        self.force_redraw = False
    
    def draw_input_boxes(self):
        """绘制输入框"""
        for i, input_box in enumerate(self.input_boxes):
            # 绘制栏目标题 - 与输入框水平居中
            title_text = self.text_font.render(input_box['title'], True, self.WHITE)
            title_rect = title_text.get_rect(
                centerx=input_box['rect'].centerx,  # 水平居中
                y=input_box['rect'].y - 35
            )
            self.screen.blit(title_text, title_rect)
            
            # 输入框背景 - 透明效果
            if input_box['active']:
                # 活跃状态：半透明白色背景，蓝色边框
                transparent_white = (255, 255, 255, 128)  # 半透明白色
                s = pygame.Surface((input_box['rect'].width, input_box['rect'].height))
                s.set_alpha(128)
                s.fill((255, 255, 255))
                self.screen.blit(s, input_box['rect'])
                pygame.draw.rect(self.screen, self.BLUE, input_box['rect'], 3)
            else:
                # 非活跃状态：半透明浅灰色背景，深灰色边框
                s = pygame.Surface((input_box['rect'].width, input_box['rect'].height))
                s.set_alpha(80)  # 更透明
                s.fill((200, 200, 200))
                self.screen.blit(s, input_box['rect'])
                pygame.draw.rect(self.screen, self.DARK_GRAY, input_box['rect'], 2)
            
            # 输入框文字
            if input_box['active']:
                display_text = input_box['text']
                text_color = self.BLACK
            else:
                display_text = input_box['text'] or input_box['placeholder']
                text_color = self.DARK_GRAY if not input_box['text'] else self.BLACK
            
            # 使用换行文字绘制
            self.draw_wrapped_text(input_box['rect'], display_text, text_color)
            
            # 绘制清除按钮 - 改进样式
            clear_button = self.buttons.get(f"clear_{input_box['type']}")
            if clear_button:
                # 渐变效果
                pygame.draw.rect(self.screen, (220, 80, 80), clear_button['rect'])
                pygame.draw.rect(self.screen, self.BLACK, clear_button['rect'], 2)
                
                clear_text = self.small_font.render(clear_button['text'], True, self.WHITE)
                clear_rect = clear_text.get_rect(center=clear_button['rect'].center)
                self.screen.blit(clear_text, clear_rect)
    
    def draw_wrapped_text(self, rect, text, color):
        """绘制换行文字 - 支持手动换行和自动换行，最多4行"""
        if not text:
            return
        
        line_height = self.text_font.get_height()
        available_width = rect.width - 20
        
        # 首先按换行符分割文字
        manual_lines = text.split('\n')
        lines = []
        
        for manual_line in manual_lines:
            if not manual_line:
                # 空行
                lines.append("")
                continue
                
            # 检查手动换行的行是否需要进一步分割
            line_surface = self.text_font.render(manual_line, True, color)
            if line_surface.get_width() <= available_width:
                # 行宽度合适，直接添加
                lines.append(manual_line)
            else:
                # 行太宽，需要自动分割
                current_line = ""
                for char in manual_line:
                    test_line = current_line + char
                    test_surface = self.text_font.render(test_line, True, color)
                    
                    if test_surface.get_width() <= available_width:
                        current_line = test_line
                    else:
                        # 当前行已满，保存并开始新行
                        if current_line:
                            lines.append(current_line)
                        current_line = char
                
                # 添加最后一部分
                if current_line:
                    lines.append(current_line)
        
        # 严格限制最大行数为4行
        max_lines = 4
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            # 如果第4行太长，截断并添加...
            last_line = lines[-1]
            while last_line and self.text_font.render(last_line + "...", True, color).get_width() > available_width:
                last_line = last_line[:-1]
            lines[-1] = last_line + "..."
        
        # 绘制每一行
        start_y = rect.y + 10
        
        for i, line in enumerate(lines):
            # 检查是否会超出输入框底部
            if start_y + i * line_height > rect.bottom - 10:
                break
            
            # 渲染文字
            text_surface = self.text_font.render(line, True, color)
            
            # 绘制文字
            text_rect = text_surface.get_rect(
                x=rect.x + 10,
                y=start_y + i * line_height
            )
            self.screen.blit(text_surface, text_rect)
    
    def draw_preview_areas(self):
        """绘制预览区域"""
        for image_type, preview in self.preview_areas.items():
            rect = preview['rect']
            size = preview['size']
            preview_size = preview.get('preview_size', (size[0] * 3, size[1] * 3))
            
            # 预览框背景 - 透明效果
            s = pygame.Surface((rect.width, rect.height))
            s.set_alpha(100)  # 半透明
            s.fill((150, 150, 150))
            self.screen.blit(s, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2)
            
            # 预览图片
            if preview['image']:
                # 使用保存的预览尺寸
                scaled_image = pygame.transform.smoothscale(preview['image'], preview_size)
                
                # 居中显示
                image_rect = scaled_image.get_rect(center=rect.center)
                self.screen.blit(scaled_image, image_rect)
            else:
                # 显示"No Image" - 无背景色
                no_image_text = self.text_font.render("No Image", True, self.DARK_GRAY)
                no_image_rect = no_image_text.get_rect(center=rect.center)
                self.screen.blit(no_image_text, no_image_rect)
            
            # 显示尺寸信息
            size_text = f"Target: {size[0]}x{size[1]}"
            size_surface = self.small_font.render(size_text, True, self.WHITE)
            size_rect = size_surface.get_rect(
                x=rect.x,
                y=rect.bottom + 15
            )
            self.screen.blit(size_surface, size_rect)
            
            # 显示预览尺寸
            preview_text = f"Preview: {preview_size[0]}x{preview_size[1]}"
            preview_surface = self.small_font.render(preview_text, True, self.WHITE)
            preview_rect = preview_surface.get_rect(
                x=rect.x,
                y=size_rect.bottom + 5
            )
            self.screen.blit(preview_surface, preview_rect)
    
    def draw_buttons(self):
        """绘制按钮"""
        for button_name, button in self.buttons.items():
            # 根据按钮类型设置不同颜色
            if button['type'] == 'back':
                # Back按钮 - 灰色
                bg_color = (120, 120, 120)
                border_color = self.BLACK
            elif button['type'] == 'complete':
                # Complete按钮 - 绿色
                bg_color = (80, 180, 80)
                border_color = self.BLACK
            elif 'upload' in button['type']:
                # Upload按钮 - 蓝色
                bg_color = (80, 120, 200)
                border_color = self.BLACK
            elif 'ai_gen' in button['type']:
                # AI Gen按钮 - 紫色
                bg_color = (150, 80, 200)
                border_color = self.BLACK
            elif 'clear' in button['type']:
                # Clear按钮已在input_boxes中处理
                continue
            else:
                # 默认按钮
                bg_color = self.BLUE
                border_color = self.BLACK
            
            # 绘制按钮背景和边框
            pygame.draw.rect(self.screen, bg_color, button['rect'])
            pygame.draw.rect(self.screen, border_color, button['rect'], 2)
            
            # 添加光泽效果
            highlight_rect = pygame.Rect(
                button['rect'].x + 2, 
                button['rect'].y + 2, 
                button['rect'].width - 4, 
                button['rect'].height // 3
            )
            highlight_color = tuple(min(255, c + 40) for c in bg_color)
            pygame.draw.rect(self.screen, highlight_color, highlight_rect)
            
            # 按钮文字
            font_size = self.small_font if len(button['text']) > 8 else self.text_font
            button_text = font_size.render(button['text'], True, self.WHITE)
            button_text_rect = button_text.get_rect(center=button['rect'].center)
            self.screen.blit(button_text, button_text_rect)
    
    def draw_status_info(self):
        """绘制状态信息"""
        if self.status_message:
            # 状态框背景
            status_rect = pygame.Rect(50, 50, self.width - 100, 60)
            pygame.draw.rect(self.screen, self.status_color, status_rect)
            pygame.draw.rect(self.screen, self.BLACK, status_rect, 2)
            
            # 状态文字
            status_text = self.text_font.render(self.status_message, True, self.WHITE)
            status_text_rect = status_text.get_rect(center=status_rect.center)
            self.screen.blit(status_text, status_text_rect)
    
    def draw_generation_progress(self):
        """绘制AI生成进度"""
        if self.generating:
            # 创建半透明遮罩背景
            overlay_surface = pygame.Surface((self.width, self.height))
            overlay_surface.set_alpha(128)  # 半透明
            overlay_surface.fill(self.BLACK)
            self.screen.blit(overlay_surface, (0, 0))
            
            # 计算进度条尺寸和位置 - 居中显示，宽度为屏幕的1/3
            progress_width = self.width // 3
            progress_height = 30
            progress_x = (self.width - progress_width) // 2
            progress_y = (self.height - progress_height) // 2
            
            # 进度条背景
            progress_bg_rect = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
            pygame.draw.rect(self.screen, self.GRAY, progress_bg_rect)
            pygame.draw.rect(self.screen, self.BLACK, progress_bg_rect, 2)
            
            # 进度条填充
            if self.generation_progress > 0:
                fill_width = int(progress_width * self.generation_progress / 100)
                if fill_width > 0:
                    progress_fill_rect = pygame.Rect(progress_x, progress_y, fill_width, progress_height)
                    # 使用渐变色效果
                    gradient_color = (
                        int(100 + (self.generation_progress * 1.55)),  # 绿色渐变
                        int(255 - (self.generation_progress * 0.5)),   # 绿色渐变
                        int(100 + (self.generation_progress * 0.5))    # 绿色渐变
                    )
                    pygame.draw.rect(self.screen, gradient_color, progress_fill_rect)
                    
                    # 添加高光效果
                    highlight_height = progress_height // 3
                    highlight_rect = pygame.Rect(progress_x, progress_y, fill_width, highlight_height)
                    highlight_color = tuple(min(255, c + 40) for c in gradient_color)
                    pygame.draw.rect(self.screen, highlight_color, highlight_rect)
            
            # 进度文字 - 居中显示，包含阶段信息
            stage_text = self.get_generation_stage_text()
            progress_text = f"AI生成中... {self.generation_progress}% - {stage_text}"
            progress_surface = self.text_font.render(progress_text, True, self.WHITE)
            progress_text_rect = progress_surface.get_rect(center=(self.width // 2, progress_y + progress_height + 30))
            self.screen.blit(progress_surface, progress_text_rect)
    
    def get_generation_stage_text(self):
        """获取AI生成的阶段文字"""
        if self.generation_progress <= 5:
            return "准备中..."
        elif self.generation_progress <= 20:
            return "模型加载中..."
        elif self.generation_progress <= 40:
            return "文本编码中..."
        elif self.generation_progress <= 90:
            return "扩散过程中..."
        elif self.generation_progress <= 95:
            return "图像生成中..."
        else:
            return "后处理中..."
    
    def run(self):
        """运行配置页面 - 用于与启动器集成"""
        print("自定义配置页面开始运行")
        
        # 创建时钟对象
        clock = pygame.time.Clock()
        
        while True:
            # 1. 设置刷新帧率
            clock.tick(60)
            
            # 2. 事件监听
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                # 处理页面事件
                result = self.handle_event(event)
                if result:
                    return result
            
            # 3. 更新状态
            self.update()
            
            # 4. 绘制页面
            self.draw()
            
            # 5. 更新屏幕显示
            pygame.display.update()
