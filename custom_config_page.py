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
        print("Initializing custom configuration page...")
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (100, 150, 255)
        self.GREEN = (100, 255, 100)
        self.RED = (255, 100, 100)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (100, 100, 100)
        
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
            print("Configuration cache reset")
        else:
            print("Preserving existing configuration cache")
        
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
        
        # Create UI elements
        self.create_ui_elements()
        
        # Restore preview images (if cache preserved)
        if preserve_cache and hasattr(self, 'config_cache'):
            self.restore_preview_images()
        
        # Load background
        self.background = self.load_background()
        
        print("Custom configuration page initialization completed")
    
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
        """Load background image"""
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
        titles = ['Player Plane', 'Enemy Plane', 'Background']
        
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
                'text': 'Clear',
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
                'text': 'Upload',
                'type': f'upload_{image_type}'
            }
            self.buttons[f'upload_{image_type}'] = upload_button
            
            # AI Gen button - to the right of upload button
            ai_gen_button = {
                'rect': pygame.Rect(buttons_start_x + 110, y, 90, 35),
                'text': 'AI Gen',
                'type': f'ai_gen_{image_type}'
            }
            self.buttons[f'ai_gen_{image_type}'] = ai_gen_button
        
        # Top buttons - vertically centered with title
        button_y = 25  # Title at Y=50, button height 50, so start from Y=25
        
        # Back button - improved style, placed in top-left corner, smaller size
        back_button = {
            'rect': pygame.Rect(60, button_y, 120, 40),  # Changed from 140x50 to 120x40
            'text': 'Back',
            'type': 'back'
        }
        self.buttons['back'] = back_button
        
        # Complete button - improved style, placed in top-right corner, smaller size
        complete_button = {
            'rect': pygame.Rect(self.width - 180, button_y, 120, 40),  # Changed from 140x50 to 120x40, position adjusted accordingly
            'text': 'Complete',
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
            print("Clicked Back button, clearing cache and returning to main menu")
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
            print(f"Clicked Upload button: {image_type}")
            self.start_upload(image_type)
        
        elif button_type.startswith('ai_gen_'):
            image_type = button_type.replace('ai_gen_', '')
            print(f"Clicked AI Gen button: {image_type}")
            self.start_ai_generation(image_type)
        
        elif button_type.startswith('clear_'):
            image_type = button_type.replace('clear_', '')
            print(f"Clicked Clear button: {image_type}")
            self.clear_input_text(image_type)
    
    def clear_input_text(self, image_type):
        """Clear input box text"""
        for input_box in self.input_boxes:
            if input_box['type'] == image_type:
                input_box['text'] = ''
                self.force_redraw = True
                break
    
    def start_upload(self, image_type):
        """Start upload"""
        print(f"Starting upload of {image_type} image...")
        
        def upload_thread():
            try:
                # Show upload status
                self.show_status(f"Selecting {image_type} image...", self.BLUE)
                
                # Call file selector
                file_path = select_file(image_type)
                
                if file_path and os.path.exists(file_path):
                    print(f"Selected file: {file_path}")
                    self.pending_upload = (image_type, file_path)
                else:
                    if file_path:
                        print(f"File does not exist: {file_path}")
                        self.show_status(f"File does not exist: {file_path}", self.RED)
                    else:
                        print("User cancelled file selection")
                        self.show_status("File selection cancelled", self.BLUE)
                        
            except Exception as e:
                print(f"Upload failed: {e}")
                self.show_status(f"Upload failed: {str(e)}", self.RED)
        
        # Start upload thread
        threading.Thread(target=upload_thread, daemon=True).start()
    
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
                
                print(f"Target size: {original_width}x{original_height}")
                print(f"Generation size (improved quality): {width}x{height}")
                
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
                    print(f"Scaling image: {width}x{height} -> {target_size}")
                    # Use high-quality scaling algorithm
                    scaled_image = pygame.transform.smoothscale(image, target_size)
                    
                    # Update preview area (scale to preview size)
                    if image_type in self.preview_areas:
                        # Get preview size
                        preview_size = self.preview_areas[image_type].get('preview_size', (target_size[0] * 3, target_size[1] * 3))
                        preview_image = pygame.transform.smoothscale(scaled_image, preview_size)
                        self.preview_areas[image_type]['image'] = preview_image
                        print(f"Updated AI preview area: {image_type}, preview size: {preview_size}")
                    
                    # Update configuration cache (save target size image)
                    self.config_cache[image_type] = scaled_image
                    print(f"Updated AI configuration cache: {image_type}, target size: {target_size}")
                    
                    self.show_status(f"{image_type} AI generation successful!", self.GREEN)
                else:
                    self.show_status(f"{image_type} AI generation failed", self.RED)
                
            except Exception as e:
                print(f"AI generation failed: {e}")
                self.show_status(f"AI generation failed: {e}", self.RED)
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
        for preview in self.preview_areas.values():
            preview['image'] = None
        self.force_redraw = True
    
    def get_config(self):
        """Get configuration"""
        return self.config_cache
    
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
            print(f"Processing uploaded file: {image_type} - {file_path}")
            
            if not os.path.exists(file_path):
                self.show_status(f"File does not exist: {file_path}", self.RED)
                return
            
            # Check file type
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
            file_ext = os.path.splitext(file_path.lower())[1]
            if file_ext not in valid_extensions:
                self.show_status(f"Unsupported file format: {file_ext}", self.RED)
                return
            
            # Load image
            try:
                image = pygame.image.load(file_path)
                print(f"Successfully loaded image, original size: {image.get_size()}")
            except pygame.error as e:
                self.show_status(f"Cannot load image: {str(e)}", self.RED)
                return
            
            # Get target size
            target_size = self.TRADITIONAL_SIZES.get(image_type, (512, 512))
            target_width, target_height = target_size
            
            # Scale image to target size - use high-quality scaling
            scaled_image = pygame.transform.smoothscale(image, target_size)
            print(f"Image scaled to target size: {target_size}")
            
            # Update preview area (scale to preview size)
            if image_type in self.preview_areas:
                # Get preview size
                preview_size = self.preview_areas[image_type].get('preview_size', (target_size[0] * 3, target_size[1] * 3))
                preview_image = pygame.transform.smoothscale(scaled_image, preview_size)
                self.preview_areas[image_type]['image'] = preview_image
                print(f"Updated preview area: {image_type}, preview size: {preview_size}")
            
            # Update configuration cache (save target size image)
            self.config_cache[image_type] = preview_image
            print(f"Updated configuration cache: {image_type}, target size: {target_size}")
            
            # Show success message
            self.show_status(f"{image_type} upload successful!", self.GREEN)
            self.force_redraw = True
            
        except Exception as e:
            print(f"Failed to process uploaded file: {e}")
            import traceback
            traceback.print_exc()
            self.show_status(f"Failed to process file: {str(e)}", self.RED)
    
    def draw(self):
        """Draw page"""
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BLACK)
        
        # Draw title
        title = self.title_font.render("Custom Configuration", True, self.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)
        
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
        
        # Reset force redraw flag
        self.force_redraw = False
    
    def draw_input_boxes(self):
        """Draw input boxes"""
        for i, input_box in enumerate(self.input_boxes):
            # Draw column title - horizontally centered with input box
            title_text = self.text_font.render(input_box['title'], True, self.WHITE)
            title_rect = title_text.get_rect(
                centerx=input_box['rect'].centerx,  # Horizontal center
                y=input_box['rect'].y - 35
            )
            self.screen.blit(title_text, title_rect)
            
            # Input box background - transparent effect
            if input_box['active']:
                # Active state: semi-transparent white background, blue border
                transparent_white = (255, 255, 255, 128)  # Semi-transparent white
                s = pygame.Surface((input_box['rect'].width, input_box['rect'].height))
                s.set_alpha(128)
                s.fill((255, 255, 255))
                self.screen.blit(s, input_box['rect'])
                pygame.draw.rect(self.screen, self.BLUE, input_box['rect'], 3)
            else:
                # Inactive state: semi-transparent light gray background, dark gray border
                s = pygame.Surface((input_box['rect'].width, input_box['rect'].height))
                s.set_alpha(80)  # More transparent
                s.fill((200, 200, 200))
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
            
            # Draw clear button - improved style
            clear_button = self.buttons.get(f"clear_{input_box['type']}")
            if clear_button:
                # Gradient effect
                pygame.draw.rect(self.screen, (220, 80, 80), clear_button['rect'])
                pygame.draw.rect(self.screen, self.BLACK, clear_button['rect'], 2)
                
                clear_text = self.small_font.render(clear_button['text'], True, self.WHITE)
                clear_rect = clear_text.get_rect(center=clear_button['rect'].center)
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
            
            # Preview box background - transparent effect
            s = pygame.Surface((rect.width, rect.height))
            s.set_alpha(100)  # Semi-transparent
            s.fill((150, 150, 150))
            self.screen.blit(s, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2)
            
            # Preview image
            if preview['image']:
                # Use saved preview size
                scaled_image = pygame.transform.smoothscale(preview['image'], preview_size)
                
                # Center display
                image_rect = scaled_image.get_rect(center=rect.center)
                self.screen.blit(scaled_image, image_rect)
            else:
                # Display "No Image" - no background color
                no_image_text = self.text_font.render("No Image", True, self.DARK_GRAY)
                no_image_rect = no_image_text.get_rect(center=rect.center)
                self.screen.blit(no_image_text, no_image_rect)
            
            # Display size information
            size_text = f"Target: {size[0]}x{size[1]}"
            size_surface = self.small_font.render(size_text, True, self.WHITE)
            size_rect = size_surface.get_rect(
                x=rect.x,
                y=rect.bottom + 15
            )
            self.screen.blit(size_surface, size_rect)
            
            # Display preview size
            preview_text = f"Preview: {preview_size[0]}x{preview_size[1]}"
            preview_surface = self.small_font.render(preview_text, True, self.WHITE)
            preview_rect = preview_surface.get_rect(
                x=rect.x,
                y=size_rect.bottom + 5
            )
            self.screen.blit(preview_surface, preview_rect)
    
    def draw_buttons(self):
        """Draw buttons"""
        for button_name, button in self.buttons.items():
            # Set different colors based on button type
            if button['type'] == 'back':
                # Back button - gray
                bg_color = (120, 120, 120)
                border_color = self.BLACK
            elif button['type'] == 'complete':
                # Complete button - green
                bg_color = (80, 180, 80)
                border_color = self.BLACK
            elif 'upload' in button['type']:
                # Upload button - blue
                bg_color = (80, 120, 200)
                border_color = self.BLACK
            elif 'ai_gen' in button['type']:
                # AI Gen button - purple
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
            progress_text = f"AI generating... {self.generation_progress}% - {stage_text}"
            progress_surface = self.text_font.render(progress_text, True, self.WHITE)
            progress_text_rect = progress_surface.get_rect(center=(self.width // 2, progress_y + progress_height + 30))
            self.screen.blit(progress_surface, progress_text_rect)
    
    def get_generation_stage_text(self):
        """获取AI生成的阶段文字"""
        if self.generation_progress <= 5:
            return "Preparing..."
        elif self.generation_progress <= 20:
            return "Loading model..."
        elif self.generation_progress <= 40:
            return "Textencoding..."
        elif self.generation_progress <= 90:
            return "Diffusion in progress..."
        elif self.generation_progress <= 95:
            return "Image generation..."
        else:
            return "Post-processing..."
    
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
