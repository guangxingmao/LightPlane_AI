#!/usr/bin/env python3
"""
Custom Configuration Page - Supports image upload and AI generation
"""

import pygame
import os
import sys
import threading
import time
from pyqt5_file_selector import select_file
from local_image_generator import generate_image_local
from ai_image_processor import AIImageProcessor

class CustomConfigPage:
    def __init__(self, screen, width=None, height=None):
        self.screen = screen
        if width and height:
            self.width, self.height = width, height
        else:
            self.width, self.height = screen.get_size()
        
        # Initialize configuration
        self.initialize_config()
    
    def initialize_config(self, preserve_cache=False):
        """Initialize configuration page"""
        print("正在初始化自定义配置页面...")
        
        # Fonts - 使用字体管理器支持中文
        try:
            from font_manager import get_chinese_font
            self.title_font = get_chinese_font(48)
            self.text_font = get_chinese_font(32)
            self.small_font = get_chinese_font(24)
        except ImportError:
            # 如果字体管理器不可用，回退到默认字体
            self.title_font = pygame.font.Font(None, 48)
            self.text_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
        
        # Colors - 现代化配色方案
        self.WHITE = (255, 255, 255)
        self.BLACK = (18, 18, 18)  # 深黑色，更现代
        self.DARK_BLUE = (25, 35, 60)  # 深蓝色背景
        self.BLUE = (64, 156, 255)  # 明亮的蓝色
        self.LIGHT_BLUE = (100, 180, 255)  # 浅蓝色
        self.GREEN = (76, 217, 100)  # 苹果风格的绿色
        self.LIGHT_GREEN = (120, 255, 120)  # 浅绿色
        self.RED = (255, 69, 58)  # 苹果风格的红色
        self.ORANGE = (255, 149, 0)  # 橙色
        self.PURPLE = (175, 82, 222)  # 紫色
        self.GRAY = (142, 142, 147)  # 中性灰色
        self.LIGHT_GRAY = (229, 229, 234)  # 浅灰色
        self.DARK_GRAY = (58, 58, 60)  # 深灰色
        self.TRANSPARENT_WHITE = (255, 255, 255, 180)  # 半透明白色
        self.TRANSPARENT_BLACK = (0, 0, 0, 120)  # 半透明黑色
        
        # Traditional mode image sizes - corrected to actual image sizes
        self.TRADITIONAL_SIZES = {
            'player_plane': (57, 46),    # life.png actual size (player life icon)
            'enemy_plane': (43, 57),     # enemy1.png actual size
            'background': (700, 480)     # background.png actual size
        }
        
        # Default prompts - simple and direct, emphasizing high-resolution complete aircraft
        self.default_prompts = {
            'player_plane': 'airplane, high resolution, complete aircraft, full plane',
            'enemy_plane': 'airplane, high resolution, complete aircraft, full plane',
            'background': 'space, stars, high resolution'
        }
        
        # Preserve or reset configuration cache
        if not preserve_cache or not hasattr(self, 'config_cache'):
            self.config_cache = {
                'player_plane': None,
                'enemy_plane': None,
                'background': None
            }
            # 添加图片来源标识
            self.image_sources = {
                'player_plane': None,  # 'ai_generated', 'uploaded', 'default'
                'enemy_plane': None,
                'background': None
            }
            print("配置缓存已重置")
        else:
            print("保留现有配置缓存")
        
        # Reset input boxes
        self.input_boxes = []
        self.selected_input = None
        
        # Reset preview areas
        self.preview_areas = {}
        
        # Reset buttons
        self.buttons = {}
        
        # Reset status information
        self.status_message = ""
        self.status_color = self.GREEN
        self.show_status_flag = False  # Renamed to avoid conflict with method
        self.status_timer = 0
        
        # Reset AI generation status
        self.generating = False
        self.generation_progress = 0
        
        # Reset pending upload file
        self.pending_upload = None
        
        # Reset force redraw flag
        self.force_redraw = False
        
        # Initialize AI image processor
        self.ai_processor = AIImageProcessor()
        
        # 创建文本渲染辅助函数
        self.render_text = self._create_render_text_function()
        
        # Create UI elements
        self.create_ui_elements()
        
        # Restore preview images (if cache preserved)
        if preserve_cache and hasattr(self, 'config_cache'):
            self.restore_preview_images()
        
        # Load background
        self.background = self.load_background()
        
        print("Custom configuration page initialization completed")
    
    def _create_render_text_function(self):
        """创建文本渲染辅助函数，优先使用字体管理器"""
        try:
            from font_manager import render_chinese_text
            return lambda text, size, color, antialias=True: render_chinese_text(text, size, color, antialias)
        except ImportError:
            # 如果字体管理器不可用，使用默认字体渲染
            def fallback_render(text, size, color, antialias=True):
                # 根据size选择合适的字体
                if size >= 40:
                    font = self.title_font
                elif size >= 25:
                    font = self.text_font
                else:
                    font = self.small_font
                return font.render(text, antialias, color)
            return fallback_render
    
    def restore_preview_images(self):
        """Restore preview images to preview areas"""
        print("Restoring preview images...")
        for image_type, cached_image in self.config_cache.items():
            if cached_image and image_type in self.preview_areas:
                # Use saved preview size
                preview_size = self.preview_areas[image_type].get('preview_size', (512, 512))
                
                # Scale to preview size
                preview_image = pygame.transform.smoothscale(cached_image, preview_size)
                self.preview_areas[image_type]['image'] = preview_image
                print(f"Restored {image_type} preview image, preview size: {preview_size}")
    
    def load_background(self):
        """Load background image or create modern gradient background"""
        try:
            bg_path = os.path.join('images', 'background.png')
            if os.path.exists(bg_path):
                bg = pygame.image.load(bg_path)
                return pygame.transform.scale(bg, (self.width, self.height))
            else:
                return None
        except:
            return None
    
    def draw_modern_background(self):
        """绘制现代化的渐变背景"""
        # 创建渐变背景
        for y in range(self.height):
            # 从深蓝色到深黑色的渐变
            ratio = y / self.height
            r = int(25 + (18 - 25) * ratio)
            g = int(35 + (18 - 35) * ratio)
            b = int(60 + (18 - 60) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
        
        # 添加一些装饰性的光点效果
        import random
        random.seed(42)  # 固定种子，确保每次显示效果一致
        for _ in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            alpha = random.randint(30, 80)
            
            # 创建半透明的光点
            light_surface = pygame.Surface((size * 2, size * 2))
            light_surface.set_alpha(alpha)
            light_surface.fill(self.WHITE)
            self.screen.blit(light_surface, (x - size, y - size))
    
    def create_ui_elements(self):
        """Create UI elements"""
        # Create input boxes
        self.create_input_boxes()
        
        # Create preview areas
        self.create_preview_areas()
        
        # Create buttons
        self.create_buttons()
    
    def create_input_boxes(self):
        """Create input boxes"""
        self.input_boxes = []
        
        # Input box height - ensure it can accommodate 4 lines of text
        line_height = 32  # Text line height
        input_height = line_height * 4 + 20  # 4 lines of text + top and bottom margins
        
        # Three-column layout, improved spacing
        column_width = (self.width - 120) // 3  # Leave more margins
        start_x = 60
        
        # Column titles
        titles = ['玩家战机', '敌机', '背景']
        
        for i, (image_type, prompt) in enumerate(self.default_prompts.items()):
            x = start_x + i * column_width
            y = 200  # Adjust Y position to leave space for titles and buttons
            
            # Input box width adjustment
            input_width = column_width - 80
            
            # Input box
            input_box = {
                'rect': pygame.Rect(x, y, input_width, input_height),
                'text': '',
                'placeholder': prompt,
                'active': False,
                'type': image_type,
                'title': titles[i]
            }
            self.input_boxes.append(input_box)
            
            # Clear button position adjustment
            clear_button = {
                'rect': pygame.Rect(x + input_width + 10, y + (input_height - 30) // 2, 60, 30),
                'text': '清除',
                'type': f'clear_{image_type}'
            }
            self.buttons[f'clear_{image_type}'] = clear_button
    
    def create_preview_areas(self):
        """Create preview areas"""
        self.preview_areas = {}
        
        # Three-column layout, consistent with input boxes
        column_width = (self.width - 120) // 3
        start_x = 60
        
        for i, (image_type, size) in enumerate(self.TRADITIONAL_SIZES.items()):
            x = start_x + i * column_width
            y = 460  # Adjust position, below buttons
            
            # Preview area size matches preview size
            # For background, use smaller preview size to avoid being too large
            if image_type == 'background':
                # Background uses smaller preview size, maintaining aspect ratio
                max_preview_width = 200  # Maximum preview width
                scale_factor = max_preview_width / size[0]
                preview_size = (int(size[0] * scale_factor), int(size[1] * scale_factor))
            else:
                # Other images use 3x target size
                preview_size = (size[0] * 3, size[1] * 3)
            
            # Calculate preview box position to center it horizontally with input box
            input_width = column_width - 80  # Input box width
            preview_x = x + (input_width - preview_size[0]) // 2  # Horizontal center
            
            preview_rect = pygame.Rect(preview_x, y, preview_size[0], preview_size[1])
            self.preview_areas[image_type] = {
                'rect': preview_rect,
                'image': None,
                'size': size,
                'preview_size': preview_size  # Save preview size information
            }
    
    def create_buttons(self):
        """Create buttons"""
        # Three-column layout, consistent with input boxes
        column_width = (self.width - 120) // 3
        start_x = 60
        
        for i, image_type in enumerate(self.default_prompts.keys()):
            x = start_x + i * column_width
            y = 360  # Adjust position, below input box
            
            # Calculate input box width for centering calculation
            input_width = column_width - 80
            
            # Total width of two buttons
            total_button_width = 90 + 90 + 20  # Two button widths + spacing
            
            # Calculate the starting position of button group to center it horizontally within input box
            buttons_start_x = x + (input_width - total_button_width) // 2
            
            # Upload button
            upload_button = {
                'rect': pygame.Rect(buttons_start_x, y, 90, 35),
                'text': '上传',
                'type': f'upload_{image_type}'
            }
            self.buttons[f'upload_{image_type}'] = upload_button
            
            # AI Gen button - to the right of upload button
            ai_gen_button = {
                'rect': pygame.Rect(buttons_start_x + 110, y, 90, 35),
                'text': 'AI生成',
                'type': f'ai_gen_{image_type}'
            }
            self.buttons[f'ai_gen_{image_type}'] = ai_gen_button
            
            # 移除背景去除按钮，现在自动处理
            # 如果需要手动控制，可以保留这些按钮
        
        # Top buttons - vertically centered with title
        button_y = 25  # Title at Y=50, button height 50, so start from Y=25
        

        
        # Back button - improved style, placed in top-left corner, smaller size
        back_button = {
            'rect': pygame.Rect(60, button_y, 120, 40),  # Changed from 140x50 to 120x40
            'text': '返回',
            'type': 'back'
        }
        self.buttons['back'] = back_button
        
        # Complete button - improved style, placed in top-right corner, smaller size
        complete_button = {
            'rect': pygame.Rect(self.width - 180, button_y, 120, 40),  # Changed from 140x50 to 120x40, position adjusted accordingly
            'text': '完成',
            'type': 'complete'
        }
        self.buttons['complete'] = complete_button
    
    def handle_event(self, event):
        """Handle events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
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
                    # Smart input handling, supports line breaks
                    current_text = self.input_boxes[self.selected_input]['text']
                    new_char = event.unicode
                    
                    # If Enter key is pressed, add line break
                    if event.unicode == '\r':
                        new_char = '\n'
                    
                    # Calculate text after adding new character
                    test_text = current_text + new_char
                    
                    # Check if line break is needed
                    if new_char == '\n':
                        # Line break directly added
                        self.input_boxes[self.selected_input]['text'] = test_text
                    else:
                        # Check if current line will exceed width
                        lines = test_text.split('\n')
                        current_line = lines[-1]  # Current line
                        
                        # Calculate current line width
                        line_surface = self.text_font.render(current_line, True, self.BLACK)
                        line_width = line_surface.get_width()
                        
                        # If current line exceeds width, auto-wrap
                        if line_width > self.input_boxes[self.selected_input]['rect'].width - 20:
                            # Auto-wrap
                            test_text = current_text + '\n' + new_char
                        
                        # Check if total lines exceed 4
                        total_lines = len(test_text.split('\n'))
                        if total_lines <= 4:
                            self.input_boxes[self.selected_input]['text'] = test_text
                    
                self.force_redraw = True
        
        return None
    
    def handle_click(self, pos):
        """Handle click events"""
        # Check input box clicks
        for i, input_box in enumerate(self.input_boxes):
            if input_box['rect'].collidepoint(pos):
                self.select_input(i)
                return None
        
        # Check button clicks
        for button in self.buttons.values():
            if button['rect'].collidepoint(pos):
                result = self.handle_button_click(button['type'])
                return result
        
        # Click elsewhere, cancel selection
        self.selected_input = None
        self.force_redraw = True
        return None
    
    def select_input(self, index):
        """Select input box"""
        self.selected_input = index
        for i, input_box in enumerate(self.input_boxes):
            input_box['active'] = (i == index)
        self.force_redraw = True
    
    def handle_button_click(self, button_type):
        """Handle button clicks"""
        if button_type == 'back':
            print("点击了返回按钮，清除缓存并返回主菜单")
            self.clear_cache()
            return 'back'
        
        elif button_type == 'complete':
            print("Clicked Complete button, returning configuration information")
            config = self.get_config()
            print(f"Current configuration: {config}")
            return {
                'type': 'custom_game',
                'config': config
            }
        
        elif button_type.startswith('upload_'):
            image_type = button_type.replace('upload_', '')
            print(f"点击了上传按钮: {image_type}")
            self.start_upload(image_type)
        
        elif button_type.startswith('ai_gen_'):
            image_type = button_type.replace('ai_gen_', '')
            print(f"点击了AI生成按钮: {image_type}")
            self.start_ai_generation(image_type)
        
        elif button_type.startswith('clear_'):
            image_type = button_type.replace('clear_', '')
            print(f"点击了清除按钮: {image_type}")
            self.clear_input_text(image_type)
        
        # 背景去除现在自动处理，不需要手动按钮
        # elif button_type.startswith('remove_bg_'):
        #     image_type = button_type.replace('remove_bg_', '')
        #     print(f"Clicked Remove BG button: {image_type}")
        #     self.start_background_removal(image_type)
        

    
    def clear_input_text(self, image_type):
        """Clear input box text"""
        for input_box in self.input_boxes:
            if input_box['type'] == image_type:
                input_box['text'] = ''
                self.force_redraw = True
                break
    
    def start_upload(self, image_type):
        """Start upload"""
        print(f"开始上传 {image_type} 图片...")
        
        def upload_thread():
            try:
                # 显示上传状态
                self.show_status(f"正在选择 {image_type} 图片...", self.BLUE)
                
                # Call file selector
                file_path = select_file(image_type)
                
                if file_path and os.path.exists(file_path):
                    print(f"Selected file: {file_path}")
                    self.pending_upload = (image_type, file_path)
                else:
                    if file_path:
                        print(f"File does not exist: {file_path}")
                        self.show_status(f"文件不存在: {file_path}", self.RED)
                    else:
                        print("用户取消了文件选择")
                        self.show_status("文件选择已取消", self.BLUE)
                        
            except Exception as e:
                print(f"Upload failed: {e}")
                self.show_status(f"上传失败: {str(e)}", self.RED)
        
        # Start upload thread
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def start_background_removal(self, image_type):
        """Start background removal process"""
        if image_type not in ['player_plane', 'enemy_plane']:
            self.show_status("背景去除功能仅适用于飞机图片", self.RED)
            return
        
        if image_type not in self.config_cache or not self.config_cache[image_type]:
            self.show_status(f"请先上传或生成 {image_type} 图片", self.RED)
            return
        
        print(f"开始为 {image_type} 去除背景...")
        
        def background_removal_thread():
            try:
                # Show processing status
                self.show_status(f"正在处理 {image_type} 背景去除...", self.BLUE)
                
                # Get current image
                current_image = self.config_cache[image_type]
                
                def on_complete(result):
                    if result['status'] == 'success':
                        # Update configuration cache with processed image
                        self.config_cache[image_type] = result['pygame_surface']
                        
                        # Update preview area
                        if image_type in self.preview_areas:
                            preview_size = self.preview_areas[image_type].get('preview_size', (512, 512))
                            preview_image = pygame.transform.smoothscale(result['pygame_surface'], preview_size)
                            self.preview_areas[image_type]['image'] = preview_image
                        
                        self.show_status(f"{image_type} 背景去除完成!", self.GREEN)
                        self.force_redraw = True
                        print(f"Background removal completed for {image_type}")
                    else:
                        self.show_status(f"{image_type} 背景去除失败: {result['error']}", self.RED)
                        print(f"Background removal failed for {image_type}: {result['error']}")
                
                # Start background removal
                self.ai_processor.process_pygame_surface(
                    current_image, 
                    image_type, 
                    callback=on_complete
                )
                
            except Exception as e:
                print(f"Background removal failed: {e}")
                self.show_status(f"背景去除失败: {str(e)}", self.RED)
        
        # Start background removal thread
        threading.Thread(target=background_removal_thread, daemon=True).start()
    

    
    def auto_remove_background(self, image_type, image_surface):
        """自动去除背景"""
        if image_type not in ['player_plane', 'enemy_plane']:
            return
        
        print(f"自动去除 {image_type} 背景...")
        
        def auto_background_removal_thread():
            try:
                # 获取当前图片
                current_image = image_surface
                
                def on_complete(result):
                    if result['status'] == 'success':
                        # 更新配置缓存
                        self.config_cache[image_type] = result['pygame_surface']
                        
                        # 更新预览区域
                        if image_type in self.preview_areas:
                            preview_size = self.preview_areas[image_type].get('preview_size', (512, 512))
                            preview_image = pygame.transform.smoothscale(result['pygame_surface'], preview_size)
                            self.preview_areas[image_type]['image'] = preview_image
                        
                        self.show_status(f"{image_type} 自动背景去除完成!", self.GREEN)
                        self.force_redraw = True
                        print(f"Automatic background removal completed: {image_type}")
                    else:
                        self.show_status(f"{image_type} 自动背景去除失败: {result['error']}", self.RED)
                        print(f"Automatic background removal failed: {image_type}: {result['error']}")
                
                # 开始背景去除
                self.ai_processor.process_pygame_surface(
                    current_image, 
                    image_type, 
                    callback=on_complete
                )
                
            except Exception as e:
                print(f"Automatic background removal failed: {e}")
                self.show_status(f"自动背景去除失败: {str(e)}", self.RED)
        
        # 启动自动背景去除线程
        threading.Thread(target=auto_background_removal_thread, daemon=True).start()
    
    def start_ai_generation(self, image_type):
        """Start AI generation"""
        if self.generating:
            return
        
        self.generating = True
        self.generation_progress = 0
        
        def generation_thread():
            try:
                # Get user input
                user_input = ""
                for input_box in self.input_boxes:
                    if input_box['type'] == image_type:
                        user_input = input_box['text'].strip()
                        break
                
                # Build prompt - includes 8x target size information
                target_size = self.TRADITIONAL_SIZES.get(image_type, (512, 512))
                target_width, target_height = target_size
                size_info = f"size {target_width * 8}x{target_height * 8} pixels"
                
                if user_input:
                    prompt = f"{user_input}, {self.default_prompts[image_type]}, {size_info}"
                else:
                    prompt = f"{self.default_prompts[image_type]}, {size_info}"
                
                # Get target size, but use larger generation size to improve quality
                target_size = self.TRADITIONAL_SIZES.get(image_type, (512, 512))
                original_width, original_height = target_size
                
                # Use larger generation size to improve AI generation quality
                # Calculate appropriate generation size (at least 512x512 or maintain aspect ratio)
                if image_type == 'background':
                    # Background uses larger size
                    gen_width = 512
                    gen_height = int(512 * original_height / original_width)
                else:
                    # Aircraft images use fixed larger size
                    gen_width = 512
                    gen_height = 512
                
                # Adjust to multiples of 8 (Stable Diffusion requirement)
                width = ((gen_width + 7) // 8) * 8
                height = ((gen_height + 7) // 8) * 8
                
                print(f"目标尺寸: {original_width}x{original_height}")
                print(f"生成尺寸(提升质量): {width}x{height}")
                
                # Generate image - increase steps to improve quality
                self.generation_progress = 5
                
                # Simulate AI generation progress for different stages
                # Stage 1: Model loading and initialization (5% -> 20%)
                for i in range(5, 21, 3):
                    self.generation_progress = i
                    time.sleep(0.1)  # Brief delay to make progress bar visible
                
                # Stage 2: Text encoding (20% -> 40%)
                for i in range(20, 41, 4):
                    self.generation_progress = i
                    time.sleep(0.1)
                
                # Stage 3: Diffusion process (40% -> 90%)
                for i in range(40, 91, 5):
                    self.generation_progress = i
                    time.sleep(0.2)  # Diffusion process needs more time
                
                # Stage 4: Image generation (90% -> 95%)
                for i in range(90, 96, 1):
                    self.generation_progress = i
                    time.sleep(0.1)
                
                # Actually generate image
                image = generate_image_local(prompt, width, height, steps=20)
                
                # Stage 5: Post-processing (95% -> 100%)
                self.generation_progress = 95
                time.sleep(0.1)
                self.generation_progress = 100
                time.sleep(0.2)  # Keep 100% status for a moment
                
                if image:
                    # Always need to scale to target size (because we used larger generation size)
                    print(f"缩放图片: {width}x{height} -> {target_size}")
                    # Use high-quality scaling algorithm
                    scaled_image = pygame.transform.smoothscale(image, target_size)
                    
                    # Update preview area (scale to preview size)
                    if image_type in self.preview_areas:
                        # Get preview size
                        preview_size = self.preview_areas[image_type].get('preview_size', (target_size[0] * 3, target_size[1] * 3))
                        preview_image = pygame.transform.smoothscale(scaled_image, preview_size)
                        self.preview_areas[image_type]['image'] = preview_image
                        print(f"已更新AI预览区域: {image_type}, 预览尺寸: {preview_size}")
                    
                    # Update configuration cache (save target size image)
                    self.config_cache[image_type] = scaled_image
                    # 设置图片来源标识为AI生成
                    self.image_sources[image_type] = 'ai_generated'
                    print(f"已更新AI配置缓存: {image_type}, 目标尺寸: {target_size}")
                    print(f"图片来源标记为: {self.image_sources[image_type]}")
                    
                    self.show_status(f"{image_type} AI生成成功!", self.GREEN)
                    
                    # 自动去除背景（仅对飞机图片）
                    if image_type in ['player_plane', 'enemy_plane']:
                        self.show_status(f"正在自动去除 {image_type} 背景...", self.BLUE)
                        self.auto_remove_background(image_type, scaled_image)
                else:
                    self.show_status(f"{image_type} AI生成失败", self.RED)
                
            except Exception as e:
                print(f"AI generation failed: {e}")
                self.show_status(f"AI生成失败: {e}", self.RED)
            finally:
                self.generating = False
                self.generation_progress = 0
        
        threading.Thread(target=generation_thread, daemon=True).start()
    
    def show_status(self, message, color):
        """Display status information"""
        self.status_message = message
        self.status_color = color
        self.show_status_flag = True
        self.status_timer = time.time()
    
    def clear_cache(self):
        """Clear cache"""
        self.config_cache = {
            'player_plane': None,
            'enemy_plane': None,
            'background': None
        }
        # 清除图片来源标识
        self.image_sources = {
            'player_plane': None,
            'enemy_plane': None,
            'background': None
        }
        for preview in self.preview_areas.values():
            preview['image'] = None
        self.force_redraw = True
    
    def get_config(self):
        """Get configuration"""
        return {
            'images': self.config_cache,
            'sources': self.image_sources
        }
    
    def update(self):
        """Update status"""
        current_time = time.time()
        
        # Check status information display time
        if self.show_status_flag and current_time - self.status_timer > 3:
            self.show_status_flag = False
        
        # Process pending upload file
        if self.pending_upload:
            image_type, file_path = self.pending_upload
            self.pending_upload = None
            self.process_uploaded_file(image_type, file_path)
        
        # Update AI generation progress - now controlled by generation thread, no auto-increment needed here
        # Progress bar update logic moved to AI generation thread to ensure synchronization with actual generation process
    
    def process_uploaded_file(self, image_type, file_path):
        """Process uploaded file"""
        try:
            print(f"正在处理上传的文件: {image_type} - {file_path}")
            
            if not os.path.exists(file_path):
                self.show_status(f"文件不存在: {file_path}", self.RED)
                return
            
            # Check file type
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
            file_ext = os.path.splitext(file_path.lower())[1]
            if file_ext not in valid_extensions:
                self.show_status(f"不支持的文件格式: {file_ext}", self.RED)
                return
            
            # Load image
            try:
                image = pygame.image.load(file_path)
                print(f"图片加载成功，原始尺寸: {image.get_size()}")
            except pygame.error as e:
                self.show_status(f"无法加载图片: {str(e)}", self.RED)
                return
            
            # Get target size
            target_size = self.TRADITIONAL_SIZES.get(image_type, (512, 512))
            target_width, target_height = target_size
            
            # Scale image to target size - use high-quality scaling
            scaled_image = pygame.transform.smoothscale(image, target_size)
            print(f"图片已缩放到目标尺寸: {target_size}")
            
            # Update preview area (scale to preview size)
            if image_type in self.preview_areas:
                # Get preview size
                preview_size = self.preview_areas[image_type].get('preview_size', (target_size[0] * 3, target_size[1] * 3))
                preview_image = pygame.transform.smoothscale(scaled_image, preview_size)
                self.preview_areas[image_type]['image'] = preview_image
                print(f"Updated preview area: {image_type}, preview size: {preview_size}")
            
            # Update configuration cache (save target size image)
            self.config_cache[image_type] = preview_image
            # 设置图片来源标识为上传
            self.image_sources[image_type] = 'uploaded'
            print(f"已更新配置缓存: {image_type}, 目标尺寸: {target_size}")
            print(f"图片来源标记为: {self.image_sources[image_type]}")
            
            # Show success message
            self.show_status(f"{image_type} 上传成功!", self.GREEN)
            self.force_redraw = True
            
            # 自动去除背景（仅对飞机图片）
            if image_type in ['player_plane', 'enemy_plane']:
                self.show_status(f"正在自动去除 {image_type} 背景...", self.BLUE)
                self.auto_remove_background(image_type, scaled_image)
            
        except Exception as e:
            print(f"Failed to process uploaded file: {e}")
            import traceback
            traceback.print_exc()
            self.show_status(f"文件处理失败: {str(e)}", self.RED)
    
    def draw(self):
        """Draw page"""
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.draw_modern_background()
        
        # Draw title with shadow effect
        title = self.render_text("自定义配置", 48, self.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 50))
        
        # 添加标题阴影效果
        shadow = self.render_text("自定义配置", 48, self.TRANSPARENT_BLACK)
        shadow_rect = shadow.get_rect(center=(self.width // 2 + 3, 53))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        
        # 添加标题下的装饰线
        line_y = 80
        line_width = 200
        line_x = (self.width - line_width) // 2
        pygame.draw.line(self.screen, self.BLUE, (line_x, line_y), (line_x + line_width, line_y), 3)
        
        # Draw input boxes
        self.draw_input_boxes()
        
        # Draw preview areas
        self.draw_preview_areas()
        
        # Draw buttons
        self.draw_buttons()
        
        # Draw status information
        if self.show_status_flag:
            self.draw_status_info()
        
        # Draw AI generation progress
        if self.generating:
            self.draw_generation_progress()
        
        # Draw AI processor status
        self.draw_ai_processor_status()
        
        # Reset force redraw flag
        self.force_redraw = False
    
    def draw_input_boxes(self):
        """Draw input boxes"""
        for i, input_box in enumerate(self.input_boxes):
            # Draw column title - horizontally centered with input box
            title_text = self.render_text(input_box['title'], 32, self.WHITE)
            title_rect = title_text.get_rect(
                centerx=input_box['rect'].centerx,  # Horizontal center
                y=input_box['rect'].y - 35
            )
            self.screen.blit(title_text, title_rect)
            
            # Input box background - modern glass effect
            if input_box['active']:
                # Active state: glass effect with blue accent
                s = pygame.Surface((input_box['rect'].width, input_box['rect'].height))
                s.set_alpha(40)
                s.fill(self.WHITE)
                self.screen.blit(s, input_box['rect'])
                
                # 渐变边框效果
                pygame.draw.rect(self.screen, self.BLUE, input_box['rect'], 3)
                # 内边框高光
                pygame.draw.rect(self.screen, self.LIGHT_BLUE, input_box['rect'].inflate(-6, -6), 1)
            else:
                # Inactive state: subtle glass effect
                s = pygame.Surface((input_box['rect'].width, input_box['rect'].height))
                s.set_alpha(20)
                s.fill(self.LIGHT_GRAY)
                self.screen.blit(s, input_box['rect'])
                pygame.draw.rect(self.screen, self.DARK_GRAY, input_box['rect'], 2)
            
            # Input box text
            if input_box['active']:
                display_text = input_box['text']
                text_color = self.BLACK
            else:
                display_text = input_box['text'] or input_box['placeholder']
                text_color = self.DARK_GRAY if not input_box['text'] else self.BLACK
            
            # Use wrapped text drawing
            self.draw_wrapped_text(input_box['rect'], display_text, text_color)
            
            # Draw clear button - modern style
            clear_button = self.buttons.get(f"clear_{input_box['type']}")
            if clear_button:
                # 现代风格的清除按钮
                button_rect = clear_button['rect']
                
                # 渐变背景
                gradient_surface = pygame.Surface((button_rect.width, button_rect.height))
                for y in range(button_rect.height):
                    ratio = y / button_rect.height
                    r = int(255 * (1 - ratio * 0.3))
                    g = int(69 * (1 - ratio * 0.3))
                    b = int(58 * (1 - ratio * 0.3))
                    pygame.draw.line(gradient_surface, (r, g, b), (0, y), (button_rect.width, y))
                
                self.screen.blit(gradient_surface, button_rect)
                
                # 边框和高光
                pygame.draw.rect(self.screen, self.RED, button_rect, 2)
                pygame.draw.rect(self.screen, (255, 120, 120), button_rect.inflate(-4, -4), 1)
                
                # 按钮文字 - 调整字体大小
                clear_text = self.render_text(clear_button['text'], 18, self.WHITE)
                clear_rect = clear_text.get_rect(center=button_rect.center)
                self.screen.blit(clear_text, clear_rect)
    
    def draw_wrapped_text(self, rect, text, color):
        """Draw wrapped text - supports manual and automatic line breaks, maximum 4 lines"""
        if not text:
            return
        
        line_height = self.text_font.get_height()
        available_width = rect.width - 20
        
        # First split text by line breaks
        manual_lines = text.split('\n')
        lines = []
        
        for manual_line in manual_lines:
            if not manual_line:
                # Empty line
                lines.append("")
                continue
                
            # Check if manually wrapped lines need further splitting
            line_surface = self.text_font.render(manual_line, True, color)
            if line_surface.get_width() <= available_width:
                # Line width is appropriate, add directly
                lines.append(manual_line)
            else:
                # Line too wide, need automatic splitting
                current_line = ""
                for char in manual_line:
                    test_line = current_line + char
                    test_surface = self.text_font.render(test_line, True, color)
                    
                    if test_surface.get_width() <= available_width:
                        current_line = test_line
                    else:
                        # Current line is full, save and start new line
                        if current_line:
                            lines.append(current_line)
                        current_line = char
                
                # Add last part
                if current_line:
                    lines.append(current_line)
        
        # Strictly limit maximum lines to 4
        max_lines = 4
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            # If 4th line is too long, truncate and add ...
            last_line = lines[-1]
            while last_line and self.text_font.render(last_line + "...", True, color).get_width() > available_width:
                last_line = last_line[:-1]
            lines[-1] = last_line + "..."
        
        # Draw each line
        start_y = rect.y + 10
        
        for i, line in enumerate(lines):
            # Check if it will exceed input box bottom
            if start_y + i * line_height > rect.bottom - 10:
                break
            
            # Render text
            text_surface = self.text_font.render(line, True, color)
            
            # Draw text
            text_rect = text_surface.get_rect(
                x=rect.x + 10,
                y=start_y + i * line_height
            )
            self.screen.blit(text_surface, text_rect)
    
    def draw_preview_areas(self):
        """Draw preview areas"""
        for image_type, preview in self.preview_areas.items():
            rect = preview['rect']
            size = preview['size']
            preview_size = preview.get('preview_size', (size[0] * 3, size[1] * 3))
            
            # Preview box background - modern glass effect
            s = pygame.Surface((rect.width, rect.height))
            s.set_alpha(30)  # 更透明
            s.fill(self.WHITE)
            self.screen.blit(s, rect)
            
            # 现代化边框
            pygame.draw.rect(self.screen, self.LIGHT_GRAY, rect, 2)
            # 内边框高光
            pygame.draw.rect(self.screen, self.WHITE, rect.inflate(-4, -4), 1)
            
            # Preview image
            if preview['image']:
                # Use saved preview size
                scaled_image = pygame.transform.smoothscale(preview['image'], preview_size)
                
                # Center display
                image_rect = scaled_image.get_rect(center=rect.center)
                self.screen.blit(scaled_image, image_rect)
            else:
                # Display "No Image" - no background color
                no_image_text = self.render_text("无图片", 28, self.DARK_GRAY)
                no_image_rect = no_image_text.get_rect(center=rect.center)
                self.screen.blit(no_image_text, no_image_rect)
            
            # Display size information
            size_text = f"目标: {size[0]}x{size[1]}"
            size_surface = self.render_text(size_text, 20, self.WHITE)
            size_rect = size_surface.get_rect(
                x=rect.x,
                y=rect.bottom + 15
            )
            self.screen.blit(size_surface, size_rect)
            
            # Display preview size
            preview_text = f"预览: {preview_size[0]}x{preview_size[1]}"
            preview_surface = self.render_text(preview_text, 20, self.WHITE)
            preview_rect = preview_surface.get_rect(
                x=rect.x,
                y=size_rect.bottom + 5
            )
            self.screen.blit(preview_surface, preview_rect)
    
    def draw_buttons(self):
        """Draw buttons with modern styling"""
        for button_name, button in self.buttons.items():
            # Set modern colors based on button type
            if button['type'] == 'back':
                # Back button - modern gray
                bg_color = self.GRAY
                border_color = self.DARK_GRAY
                hover_color = self.LIGHT_GRAY
            elif button['type'] == 'complete':
                # Complete button - modern green
                bg_color = self.GREEN
                border_color = self.DARK_GRAY
                hover_color = self.LIGHT_GREEN
            elif 'upload' in button['type']:
                # Upload button - modern blue
                bg_color = self.BLUE
                border_color = self.DARK_BLUE
                hover_color = self.LIGHT_BLUE
            elif 'ai_gen' in button['type']:
                # AI Gen button - modern purple
                bg_color = self.PURPLE
                border_color = self.DARK_GRAY
                hover_color = (200, 120, 255)
            elif 'clear' in button['type']:
                # Clear button already handled in input_boxes
                continue
            else:
                # Default button
                bg_color = self.BLUE
                border_color = self.DARK_BLUE
                hover_color = self.LIGHT_BLUE
            
            # 检查鼠标悬停状态
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button['rect'].collidepoint(mouse_pos)
            
            # 使用悬停颜色或默认颜色
            current_bg_color = hover_color if is_hovered else bg_color
            
            # 绘制现代化按钮背景
            button_rect = button['rect']
            
            # 渐变背景
            gradient_surface = pygame.Surface((button_rect.width, button_rect.height))
            for y in range(button_rect.height):
                ratio = y / button_rect.height
                r = int(current_bg_color[0] * (1 - ratio * 0.2))
                g = int(current_bg_color[1] * (1 - ratio * 0.2))
                b = int(current_bg_color[2] * (1 - ratio * 0.2))
                pygame.draw.line(gradient_surface, (r, g, b), (0, y), (button_rect.width, y))
            
            self.screen.blit(gradient_surface, button_rect)
            
            # 现代化边框
            pygame.draw.rect(self.screen, border_color, button_rect, 2)
            
            # 内边框高光效果
            pygame.draw.rect(self.screen, self.WHITE, button_rect.inflate(-4, -4), 1)
            
            # 按钮文字 - 更小的字体大小
            font_size = 18 if len(button['text']) > 6 else 22
            button_text = self.render_text(button['text'], font_size, self.WHITE)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
    
    def draw_status_info(self):
        """绘制状态信息 - 现代化样式"""
        if self.status_message:
            # 状态框背景 - 现代化设计
            status_rect = pygame.Rect(50, 50, self.width - 100, 60)
            
            # 半透明背景
            status_surface = pygame.Surface((status_rect.width, status_rect.height))
            status_surface.set_alpha(200)
            status_surface.fill(self.status_color)
            self.screen.blit(status_surface, status_rect)
            
            # 现代化边框
            pygame.draw.rect(self.screen, self.WHITE, status_rect, 2)
            pygame.draw.rect(self.screen, self.DARK_GRAY, status_rect.inflate(-4, -4), 1)
            
            # 状态文字 - 调整字体大小
            status_text = self.render_text(self.status_message, 28, self.WHITE)
            status_text_rect = status_text.get_rect(center=status_rect.center)
            self.screen.blit(status_text, status_text_rect)
            
            # 添加状态图标（简单的装饰点）
            icon_size = 8
            icon_x = status_rect.x + 20
            icon_y = status_rect.centery
            pygame.draw.circle(self.screen, self.WHITE, (icon_x, icon_y), icon_size)
            pygame.draw.circle(self.screen, self.status_color, (icon_x, icon_y), icon_size - 2)
    
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
            
            # 进度条背景 - 现代化设计
            progress_bg_rect = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
            
            # 半透明背景
            bg_surface = pygame.Surface((progress_width, progress_height))
            bg_surface.set_alpha(100)
            bg_surface.fill(self.DARK_GRAY)
            self.screen.blit(bg_surface, progress_bg_rect)
            
            # 现代化边框
            pygame.draw.rect(self.screen, self.LIGHT_GRAY, progress_bg_rect, 2)
            
            # 进度条填充
            if self.generation_progress > 0:
                fill_width = int(progress_width * self.generation_progress / 100)
                if fill_width > 0:
                    progress_fill_rect = pygame.Rect(progress_x, progress_y, fill_width, progress_height)
                    
                    # 创建渐变填充效果
                    fill_surface = pygame.Surface((fill_width, progress_height))
                    for y in range(progress_height):
                        ratio = y / progress_height
                        r = int(76 * (1 - ratio * 0.3))  # 绿色渐变
                        g = int(217 * (1 - ratio * 0.3))
                        b = int(100 * (1 - ratio * 0.3))
                        pygame.draw.line(fill_surface, (r, g, b), (0, y), (fill_width, y))
                    
                    self.screen.blit(fill_surface, progress_fill_rect)
                    
                    # 添加内边框高光
                    pygame.draw.rect(self.screen, self.LIGHT_GREEN, progress_fill_rect.inflate(-2, -2), 1)
            
            # 进度文字 - 居中显示，包含阶段信息
            stage_text = self.get_generation_stage_text()
            progress_text = f"AI生成中... {self.generation_progress}% - {stage_text}"
            progress_surface = self.render_text(progress_text, 32, self.WHITE)
            progress_text_rect = progress_surface.get_rect(center=(self.width // 2, progress_y + progress_height + 30))
            self.screen.blit(progress_surface, progress_text_rect)
    
    def draw_ai_processor_status(self):
        """Draw AI processor status information"""
        if not hasattr(self, 'ai_processor'):
            return
        
        # Get AI processor status
        status = self.ai_processor.get_processing_status()
        
        # Only show status if processing or if there are items in queue
        if status['is_processing'] or status['queue_length'] > 0:
            # Create status display area at bottom of screen
            status_y = self.height - 80
            status_height = 60
            
            # Status background - modern design
            status_rect = pygame.Rect(50, status_y, self.width - 100, status_height)
            
            # 半透明背景
            status_surface = pygame.Surface((status_rect.width, status_rect.height))
            status_surface.set_alpha(180)
            status_surface.fill(self.DARK_GRAY)
            self.screen.blit(status_surface, status_rect)
            
            # 现代化边框
            pygame.draw.rect(self.screen, self.LIGHT_GRAY, status_rect, 2)
            pygame.draw.rect(self.screen, self.WHITE, status_rect.inflate(-4, -4), 1)
            
            # Status text
            if status['is_processing']:
                status_text = f"AI处理中: {status['message']} ({status['progress']}%)"
                text_color = self.BLUE
            else:
                status_text = f"队列中: {status['queue_length']} 个任务等待处理"
                text_color = self.GRAY
            
            status_surface = self.render_text(status_text, 32, text_color)
            status_rect_text = status_surface.get_rect(center=status_rect.center)
            self.screen.blit(status_surface, status_rect_text)
            
            # Progress bar for current task
            if status['is_processing'] and status['progress'] > 0:
                progress_width = status_rect.width - 20
                progress_height = 8
                progress_x = status_rect.x + 10
                progress_y = status_rect.bottom - 15
                
                # Progress background - modern design
                progress_bg_rect = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
                
                # 半透明背景
                bg_surface = pygame.Surface((progress_width, progress_height))
                bg_surface.set_alpha(100)
                bg_surface.fill(self.DARK_GRAY)
                self.screen.blit(bg_surface, progress_bg_rect)
                
                # 现代化边框
                pygame.draw.rect(self.screen, self.LIGHT_GRAY, progress_bg_rect, 1)
                
                # Progress fill
                fill_width = int(progress_width * status['progress'] / 100)
                if fill_width > 0:
                    progress_fill_rect = pygame.Rect(progress_x, progress_y, fill_width, progress_height)
                    
                    # 创建渐变填充效果
                    fill_surface = pygame.Surface((fill_width, progress_height))
                    for y in range(progress_height):
                        ratio = y / progress_height
                        r = int(76 * (1 - ratio * 0.3))  # 绿色渐变
                        g = int(217 * (1 - ratio * 0.3))
                        b = int(100 * (1 - ratio * 0.3))
                        pygame.draw.line(fill_surface, (r, g, b), (0, y), (fill_width, y))
                    
                    self.screen.blit(fill_surface, progress_fill_rect)
                    
                    # 添加内边框高光
                    pygame.draw.rect(self.screen, self.LIGHT_GREEN, progress_fill_rect.inflate(-1, -1), 1)
    
    def get_generation_stage_text(self):
        """获取AI生成的阶段文字"""
        if self.generation_progress <= 5:
            return "准备中..."
        elif self.generation_progress <= 20:
            return "加载模型中..."
        elif self.generation_progress <= 40:
            return "文本编码中..."
        elif self.generation_progress <= 90:
            return "扩散处理中..."
        elif self.generation_progress <= 95:
            return "图片生成中..."
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
