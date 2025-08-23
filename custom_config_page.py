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
    
    def initialize_config(self):
        """初始化配置页面 - 每次进入时都重新初始化"""
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
        
        # 传统模式图片尺寸
        self.TRADITIONAL_SIZES = {
            'player_plane': (45, 56),
            'enemy_plane': (69, 36),
            'background': (480, 700)
        }
        
        # 默认提示词
        self.default_prompts = {
            'player_plane': 'fighter jet, military aircraft, size 45x56 pixels',
            'enemy_plane': 'enemy fighter, dark aircraft, size 69x36 pixels',
            'background': 'space background, stars, cosmic, size 480x700 pixels'
        }
        
        # 重置配置缓存
        self.config_cache = {
            'player_plane': None,
            'enemy_plane': None,
            'background': None
        }
        
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
        
        # 加载背景
        self.background = self.load_background()
        
        print("✅ 自定义配置页面初始化完成")
    
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
        
        # 输入框高度
        input_height = 120
        
        # 三栏布局，改进间距
        column_width = (self.width - 120) // 3  # 留出更多边距
        start_x = 60
        
        # 栏目标题
        titles = ['Player Plane', 'Enemy Plane', 'Background']
        
        for i, (image_type, prompt) in enumerate(self.default_prompts.items()):
            x = start_x + i * column_width
            y = 180  # 调整Y位置，为标题留出空间
            
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
            y = 420  # 调整位置
            
            # 预览区域，调整大小
            preview_width = min(column_width - 80, 180)
            preview_height = 140
            preview_rect = pygame.Rect(x, y, preview_width, preview_height)
            self.preview_areas[image_type] = {
                'rect': preview_rect,
                'image': None,
                'size': size
            }
    
    def create_buttons(self):
        """创建按钮"""
        # 三栏布局，与输入框保持一致
        column_width = (self.width - 120) // 3
        start_x = 60
        
        for i, image_type in enumerate(self.default_prompts.keys()):
            x = start_x + i * column_width
            y = 320  # 调整位置，在输入框下方
            
            # Upload按钮 - 更好看的样式
            upload_button = {
                'rect': pygame.Rect(x, y, 90, 35),
                'text': 'Upload',
                'type': f'upload_{image_type}'
            }
            self.buttons[f'upload_{image_type}'] = upload_button
            
            # AI Gen按钮
            ai_gen_button = {
                'rect': pygame.Rect(x + 100, y, 90, 35),
                'text': 'AI Gen',
                'type': f'ai_gen_{image_type}'
            }
            self.buttons[f'ai_gen_{image_type}'] = ai_gen_button
        
        # 底部按钮 - 位置调整
        button_y = 620
        
        # Back按钮 - 改进样式
        back_button = {
            'rect': pygame.Rect(60, button_y, 140, 50),
            'text': 'Back to Menu',
            'type': 'back'
        }
        self.buttons['back'] = back_button
        
        # Complete按钮 - 改进样式
        complete_button = {
            'rect': pygame.Rect(self.width - 200, button_y, 140, 50),
            'text': 'Complete',
            'type': 'complete'
        }
        self.buttons['complete'] = complete_button
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                self.handle_click(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            if self.selected_input is not None:
                if event.key == pygame.K_RETURN:
                    self.selected_input = None
                elif event.key == pygame.K_BACKSPACE:
                    self.input_boxes[self.selected_input]['text'] = self.input_boxes[self.selected_input]['text'][:-1]
                else:
                    self.input_boxes[self.selected_input]['text'] += event.unicode
                self.force_redraw = True
    
    def handle_click(self, pos):
        """处理点击事件"""
        # 检查输入框点击
        for i, input_box in enumerate(self.input_boxes):
            if input_box['rect'].collidepoint(pos):
                self.select_input(i)
                return
        
        # 检查按钮点击
        for button in self.buttons.values():
            if button['rect'].collidepoint(pos):
                self.handle_button_click(button['type'])
                return
        
        # 点击其他地方，取消选择
        self.selected_input = None
        self.force_redraw = True
    
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
            return 'main_menu'
        
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
                
                # 构建提示词
                if user_input:
                    prompt = f"{user_input}, {self.default_prompts[image_type]}"
                else:
                    prompt = self.default_prompts[image_type]
                
                # 获取目标尺寸并调整为8的倍数（Stable Diffusion要求）
                target_size = self.TRADITIONAL_SIZES.get(image_type, (512, 512))
                original_width, original_height = target_size
                
                # 调整为8的倍数
                width = ((original_width + 7) // 8) * 8
                height = ((original_height + 7) // 8) * 8
                
                print(f"📐 原始尺寸: {original_width}x{original_height}")
                print(f"📐 调整后尺寸（8的倍数）: {width}x{height}")
                
                # 生成图片
                self.generation_progress = 5
                image = generate_image_local(prompt, width, height, steps=8)
                
                if image:
                    # 如果生成尺寸与目标尺寸不同，需要缩放回目标尺寸
                    if (width, height) != target_size:
                        print(f"🔄 缩放图片: {width}x{height} -> {target_size}")
                        scaled_image = pygame.transform.scale(image, target_size)
                    else:
                        scaled_image = image
                    
                    # 更新预览
                    self.preview_areas[image_type]['image'] = scaled_image
                    # 更新配置缓存
                    self.config_cache[image_type] = scaled_image
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
        
        # 更新AI生成进度
        if self.generating:
            if self.generation_progress < 100:
                self.generation_progress += 1
    
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
            
            # 缩放图片到目标尺寸
            scaled_image = pygame.transform.scale(image, target_size)
            print(f"✅ 图片已缩放至目标尺寸: {target_size}")
            
            # 更新预览区域
            if image_type in self.preview_areas:
                self.preview_areas[image_type]['image'] = scaled_image
                print(f"✅ 更新预览区域: {image_type}")
            
            # 更新配置缓存
            self.config_cache[image_type] = scaled_image
            print(f"✅ 更新配置缓存: {image_type}")
            
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
            # 绘制栏目标题
            title_text = self.text_font.render(input_box['title'], True, self.WHITE)
            title_rect = title_text.get_rect(
                x=input_box['rect'].x,
                y=input_box['rect'].y - 35
            )
            self.screen.blit(title_text, title_rect)
            
            # 输入框背景 - 改进视觉效果
            if input_box['active']:
                # 活跃状态：白色背景，蓝色边框
                pygame.draw.rect(self.screen, self.WHITE, input_box['rect'])
                pygame.draw.rect(self.screen, self.BLUE, input_box['rect'], 3)
            else:
                # 非活跃状态：浅灰色背景，深灰色边框
                pygame.draw.rect(self.screen, self.GRAY, input_box['rect'])
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
        """绘制换行文字"""
        if not text:
            return
        
        # 计算每行字符数
        test_surface = self.text_font.render("A", True, color)
        char_width = test_surface.get_width()
        available_width = rect.width - 20  # 留出边距
        chars_per_line = max(1, int(available_width / char_width))
        
        # 分行
        lines = []
        current_line = ""
        words = text.split()
        
        for word in words:
            if len(current_line + word) <= chars_per_line:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # 限制最大行数
        max_lines = 4
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = lines[-1][:chars_per_line-3] + "..."
        
        # 绘制每一行
        line_height = self.text_font.get_height()
        start_y = rect.y + 10
        
        for i, line in enumerate(lines):
            if start_y + i * line_height > rect.bottom - 10:
                break
            
            text_surface = self.text_font.render(line, True, color)
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
            
            # 预览框背景
            pygame.draw.rect(self.screen, self.GRAY, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2)
            
            # 预览图片
            if preview['image']:
                # 计算预览尺寸（放大3倍）
                preview_width = size[0] * 3
                preview_height = size[1] * 3
                
                # 缩放图片
                scaled_image = pygame.transform.scale(preview['image'], (preview_width, preview_height))
                
                # 居中显示
                image_rect = scaled_image.get_rect(center=rect.center)
                self.screen.blit(scaled_image, image_rect)
            else:
                # 显示"No Image"
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
            preview_text = f"Preview: {size[0]*3}x{size[1]*3}"
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
            # 进度条背景
            progress_bg_rect = pygame.Rect(50, 120, self.width - 100, 20)
            pygame.draw.rect(self.screen, self.GRAY, progress_bg_rect)
            pygame.draw.rect(self.screen, self.BLACK, progress_bg_rect, 2)
            
            # 进度条
            progress_width = int((self.width - 100) * self.generation_progress / 100)
            if progress_width > 0:
                progress_rect = pygame.Rect(50, 120, progress_width, 20)
                pygame.draw.rect(self.screen, self.GREEN, progress_rect)
            
            # 进度文字
            progress_text = f"AI生成中... {self.generation_progress}%"
            progress_surface = self.text_font.render(progress_text, True, self.WHITE)
            progress_text_rect = progress_surface.get_rect(
                x=50,
                y=145
            )
            self.screen.blit(progress_surface, progress_text_rect)
    
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
