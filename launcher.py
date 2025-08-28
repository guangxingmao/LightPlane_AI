import pygame
import sys
import os

# 导入字体管理器
from font_manager import render_chinese_text, get_chinese_font

# 尝试导入游戏相关模块
try:
    from plane_sprites import *
    from game_function import check_KEY, check_mouse
    from Tools import Music, Button as GameButton
    GAME_MODULES_LOADED = True
except ImportError as e:
    print(f"游戏模块加载失败: {e}")
    GAME_MODULES_LOADED = False

# 尝试导入双人游戏页面
try:
    from dual_game_page import DualGamePage
    DUAL_GAME_LOADED = True
except ImportError as e:
    print(f"双人游戏页面加载失败: {e}")
    DUAL_GAME_LOADED = False

# 尝试导入传统模式游戏页面
try:
    from traditional_game_page import TraditionalGamePage
    TRADITIONAL_GAME_LOADED = True
except ImportError as e:
    print(f"传统模式游戏页面加载失败: {e}")
    TRADITIONAL_GAME_LOADED = False

# 尝试导入彩蛋模式游戏页面
try:
    from easter_egg_page import EasterEggPage
    EASTER_EGG_LOADED = True
except ImportError as e:
    print(f"彩蛋模式游戏页面加载失败: {e}")
    EASTER_EGG_LOADED = False

# 尝试导入AI模式游戏页面
try:
    from ai_game_page import AIGamePage
    AI_GAME_LOADED = True
except ImportError as e:
    print(f"AI模式游戏页面加载失败: {e}")
    AI_GAME_LOADED = False

# 初始化pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('战机大战 - 游戏启动器')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
LIGHT_BLUE = (100, 150, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

def safe_render_text(font, text, color):
    """安全地渲染文本，优先使用字体管理器支持中文"""
    try:
        # 优先使用字体管理器渲染中文
        return render_chinese_text(text, None, color)
    except Exception as e:
        print(f"字体管理器渲染失败: {e}")
        # 回退到原来的字体渲染方式
        if font is None:
            # 如果字体为None，尝试使用最基本的字体
            try:
                basic_font = pygame.font.Font(None, 24)
                return basic_font.render(text, True, color)
            except:
                # 如果还是失败，返回一个简单的矩形
                surface = pygame.Surface((len(text) * 10, 20))
                surface.fill(color)
                return surface
        
        try:
            return font.render(text, True, color)
        except Exception as e:
            print(f"文本渲染失败: {e}")
            # 返回一个简单的矩形作为备用
            surface = pygame.Surface((len(text) * 10, 20))
            surface.fill(color)
            return surface

def get_simple_font(size):
    """获取支持中文的字体"""
    try:
        return get_chinese_font(size)
    except:
        try:
            # 回退到系统字体
            return pygame.font.SysFont(None, size)
        except:
            try:
                return pygame.font.Font(None, size)
            except:
                return None

# 字体设置
title_font = pygame.font.SysFont("arial", 48)
button_font = pygame.font.SysFont("arial", 24)

# 页面状态枚举
class PageState:
    MAIN_MENU = "main_menu"
    TRADITIONAL_MODE = "traditional_mode"
    DUAL_MODE = "dual_mode"
    AI_MODE = "ai_mode"
    CUSTOM_MODE = "custom_mode"
    EASTER_EGG_MODE = "easter_egg_mode"

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.hovered = False
        self.last_click_time = 0  # 防抖：记录上次点击时间
        self.click_cooldown = 200  # 防抖：200毫秒冷却时间
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 3)
        
        # 绘制按钮文字 - 使用简单字体
        text_surface = safe_render_text(get_simple_font(24), self.text, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
                self.hovered = True
            else:
                self.current_color = self.color
                self.hovered = False
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                current_time = pygame.time.get_ticks()
                # 防抖：检查是否在冷却时间内
                if current_time - self.last_click_time > self.click_cooldown:
                    self.last_click_time = current_time
                    return True
        return False

class GameManager:
    """游戏管理器，负责管理不同页面的切换"""
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.current_page = PageState.MAIN_MENU
        
        # 缓存字体，避免重复获取
        self.title_font = get_simple_font(48)
        self.button_font = get_simple_font(24)
        self.info_font = get_simple_font(20)
        self.small_font = get_simple_font(16)
        
        # 初始化双人游戏页面
        if DUAL_GAME_LOADED:
            self.dual_game_page = DualGamePage(screen)
        else:
            self.dual_game_page = None
            
        # 初始化传统模式游戏页面
        if TRADITIONAL_GAME_LOADED:
            self.traditional_game_page = TraditionalGamePage(screen)
        else:
            self.traditional_game_page = None
            
        # 初始化彩蛋模式游戏页面
        if EASTER_EGG_LOADED:
            self.easter_egg_page = EasterEggPage(screen)
        else:
            self.easter_egg_page = None
            
        # 初始化AI模式游戏页面 - 延迟加载
        self.ai_game_page = None  # 先设为None，需要时再加载
        self._ai_game_loading = False  # 加载状态标志
        
        # 初始化页面状态标志
        self._traditional_mode_initialized = False
        self._dual_mode_initialized = False
        self._easter_egg_mode_initialized = False
        self._ai_mode_initialized = False
    
    def change_page(self, new_page):
        """切换页面"""
        self.current_page = new_page
        print(f"切换到页面: {new_page}")
    
    def run(self):
        """运行游戏管理器主循环"""
        running = True
        while running:
            # 根据当前页面状态处理事件和绘制
            if self.current_page == PageState.MAIN_MENU:
                running = self.handle_main_menu()
            elif self.current_page == PageState.DUAL_MODE:
                running = self.handle_dual_mode()
            elif self.current_page == PageState.TRADITIONAL_MODE:
                running = self.handle_traditional_mode()
            elif self.current_page == PageState.CUSTOM_MODE:
                running = self.handle_custom_mode()
            elif self.current_page == PageState.AI_MODE:
                running = self.handle_ai_mode()
            elif self.current_page == PageState.EASTER_EGG_MODE:
                running = self.handle_easter_egg_mode()
     
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def handle_main_menu(self):
        """处理主菜单页面"""
        # 创建按钮
        button_width = 200
        button_height = 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        buttons = [
            Button(center_x, 200, button_width, button_height, "传统模式", LIGHT_BLUE, BLUE),
            Button(center_x, 280, button_width, button_height, "双人模式", GREEN, (0, 200, 0)),
            Button(center_x, 360, button_width, button_height, "AI模式", YELLOW, (200, 200, 0)),
            Button(center_x, 440, button_width, button_height, "自定义模式", RED, (200, 0, 0)),
            # Button(center_x, 520, button_width, button_height, "彩蛋模式", (255, 20, 147), (255, 105, 180))
        ]
        
        # 绘制主菜单
        self.draw_main_menu(buttons)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            
            # 处理按钮事件
            for i, button in enumerate(buttons):
                if button.handle_event(event):
                    if i == 0:  # 传统模式
                        self.change_page(PageState.TRADITIONAL_MODE)
                    elif i == 1:  # 双人模式
                        self.change_page(PageState.DUAL_MODE)
                    elif i == 2:  # AI模式
                        self.change_page(PageState.AI_MODE)
                    elif i == 3:  # 自定义模式
                        self.change_page(PageState.CUSTOM_MODE)
                    elif i == 4:  # 彩蛋模式
                        self.change_page(PageState.EASTER_EGG_MODE)
        
        return True
    
    def draw_main_menu(self, buttons):
        """绘制主菜单"""
        # 绘制背景
        self.draw_background()
        
        # 绘制标题
        title_text = safe_render_text(self.title_font, "战机大战 3.0", WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        
        # 添加标题阴影效果
        shadow_text = safe_render_text(self.title_font, "战机大战 3.0", BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 3, 103))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # 绘制副标题
        subtitle_text = safe_render_text(self.info_font, "选择游戏模式开始游戏", WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # 绘制按钮
        for button in buttons:
            button.draw(self.screen)
        
        # 绘制底部信息
        info_text = safe_render_text(self.small_font, "按ESC键返回主菜单", WHITE)
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(info_text, info_rect)
    
    def draw_background(self):
        """绘制背景"""
        # 背景图片（如果存在）
        if os.path.exists('./images/background.png'):
            try:
                background = pygame.image.load('./images/background.png')
                background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.screen.blit(background, (0, 0))
                return
            except:
                pass
        
        # 渐变背景
        for y in range(SCREEN_HEIGHT):
            color = (
                int(50 + (y / SCREEN_HEIGHT) * 100),
                int(100 + (y / SCREEN_HEIGHT) * 100),
                int(150 + (y / SCREEN_HEIGHT) * 100)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
    
    def handle_dual_mode(self):
        """处理双人模式页面"""
        if not self.dual_game_page:
            # 如果双人游戏页面未加载，显示错误信息
            self.draw_background()
            error_text = safe_render_text(self.info_font, "双人游戏模块加载失败", RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(error_text, error_rect)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.change_page(PageState.MAIN_MENU)
                    return True
            return True
        
        # 如果这是第一次进入双人模式或从其他页面返回，重置游戏状态
        if not hasattr(self, '_dual_mode_initialized') or not self._dual_mode_initialized:
            self.dual_game_page.reset_game()
            self._dual_mode_initialized = True
        
        # 运行双人游戏的一帧
        try:
            result = self.dual_game_page.run_one_frame()
            if result == "quit":
                self._dual_mode_initialized = False  # 标记需要重新初始化
                self.change_page(PageState.MAIN_MENU)
                return True
            elif result == "game_over":
                # 游戏结束，标记需要重新初始化
                self._dual_mode_initialized = False
                self.change_page(PageState.MAIN_MENU)
                return True
        except Exception as e:
            print(f"双人游戏运行错误: {e}")
            self._dual_mode_initialized = False
            self.change_page(PageState.MAIN_MENU)
        
        return True
    
    def handle_traditional_mode(self):
        """处理传统模式页面"""
        if not self.traditional_game_page:
            # 如果传统模式游戏页面未加载，显示错误信息
            self.draw_background()
            error_text = safe_render_text(self.info_font, "传统游戏模块加载失败", RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(error_text, error_rect)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.change_page(PageState.MAIN_MENU)
                    return True
            return True
        
        # 如果这是第一次进入传统模式或从其他页面返回，重置游戏状态
        if not hasattr(self, '_traditional_mode_initialized') or not self._traditional_mode_initialized:
            self.traditional_game_page.reset_game()
            self._traditional_mode_initialized = True
        
        # 运行传统模式游戏的一帧
        try:
            result = self.traditional_game_page.run_one_frame()
            if result == "quit":
                self._traditional_mode_initialized = False  # 标记需要重新初始化
                self.change_page(PageState.MAIN_MENU)
                return True
            elif result == "game_over":
                # 游戏结束，标记需要重新初始化
                self._traditional_mode_initialized = False
                self.change_page(PageState.MAIN_MENU)
                return True
        except Exception as e:
            print(f"传统模式游戏运行错误: {e}")
            self._traditional_mode_initialized = False
            self.change_page(PageState.MAIN_MENU)
        
        return True
    
    def handle_easter_egg_mode(self):
        """处理彩蛋模式页面"""
        if not self.easter_egg_page:
            # 如果彩蛋模式游戏页面未加载，显示错误信息
            self.draw_background()
            error_text = safe_render_text(self.info_font, "彩蛋游戏模块加载失败", RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(error_text, error_rect)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.change_page(PageState.MAIN_MENU)
                    return True
            return True
        
        # 如果这是第一次进入彩蛋模式或从其他页面返回，重置游戏状态
        if not hasattr(self, '_easter_egg_mode_initialized') or not self._easter_egg_mode_initialized:
            self.easter_egg_page.reset_game()
            self._easter_egg_mode_initialized = True
        
        # 运行彩蛋模式游戏的一帧
        try:
            result = self.easter_egg_page.run_one_frame()
            if result == "quit":
                self._easter_egg_mode_initialized = False  # 标记需要重新初始化
                self.change_page(PageState.MAIN_MENU)
                return True
            elif result == "game_over":
                # 游戏结束，标记需要重新初始化
                self._easter_egg_mode_initialized = False
                self.change_page(PageState.MAIN_MENU)
                return True
        except Exception as e:
            print(f"彩蛋模式游戏运行错误: {e}")
            self._easter_egg_mode_initialized = False
            self.change_page(PageState.MAIN_MENU)
        
        return True
    
    def handle_ai_mode(self):
        """处理AI模式页面"""
        # 延迟加载AI游戏页面
        if not self.ai_game_page and not self._ai_game_loading:
            if not AI_GAME_LOADED:
                # 如果AI模式游戏页面未加载，显示错误信息
                self.draw_background()
                error_text = safe_render_text(self.info_font, "AI游戏模块加载失败", RED)
                error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
                self.screen.blit(error_text, error_rect)
                
                # 处理事件
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.change_page(PageState.MAIN_MENU)
                        return True
                return True
            
            # 开始加载AI游戏页面
            self._ai_game_loading = True
            self.draw_background()
            loading_text = safe_render_text(self.info_font, "正在加载AI游戏模块...", YELLOW)
            loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(loading_text, loading_rect)
            pygame.display.flip()
            
            try:
                # 在后台线程中加载AI游戏页面
                self.ai_game_page = AIGamePage(self.screen)
                self._ai_game_loading = False
                print("AI游戏页面加载完成")
            except Exception as e:
                print(f"AI游戏页面加载失败: {e}")
                self._ai_game_loading = False
                self.change_page(PageState.MAIN_MENU)
                return True
        
        # 如果还在加载中，显示加载提示
        if self._ai_game_loading:
            self.draw_background()
            
            # 显示加载文本
            loading_text = safe_render_text(self.info_font, "正在加载AI游戏模块...", YELLOW)
            loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(loading_text, loading_rect)
            
            # 显示加载进度条
            progress_width = 400
            progress_height = 20
            progress_x = (SCREEN_WIDTH - progress_width) // 2
            progress_y = 350
            
            # 绘制进度条背景
            pygame.draw.rect(self.screen, GRAY, (progress_x, progress_y, progress_width, progress_height))
            
            # 绘制进度条（动画效果）
            current_time = pygame.time.get_ticks()
            progress = (current_time % 1000) / 1000.0  # 0到1之间的循环进度
            progress_width_filled = int(progress_width * progress)
            pygame.draw.rect(self.screen, GREEN, (progress_x, progress_y, progress_width_filled, progress_height))
            
            # 显示提示文本
            tip_text = safe_render_text(self.small_font, "这可能需要几秒钟...", WHITE)
            tip_rect = tip_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
            self.screen.blit(tip_text, tip_rect)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._ai_game_loading = False
                    self.change_page(PageState.MAIN_MENU)
                    return True
            return True
        
        # 如果这是第一次进入AI模式或从其他页面返回，重置游戏状态
        if not hasattr(self, '_ai_mode_initialized') or not self._ai_mode_initialized:
            # 显示加载提示
            self.draw_background()
            loading_text = safe_render_text(self.info_font, "正在初始化AI模式...", YELLOW)
            loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(loading_text, loading_rect)
            pygame.display.flip()
            
            try:
                # 重新创建AI游戏页面来初始化
                self.ai_game_page = AIGamePage(self.screen)
                self._ai_mode_initialized = True
                print("✅ AI模式重新初始化成功")
            except Exception as e:
                print(f"AI模式初始化失败: {e}")
                # 初始化失败，返回主菜单
                self._ai_mode_initialized = False
                self.change_page(PageState.MAIN_MENU)
                return True
        
        # 如果这是第一次进入AI模式或从其他页面返回，标记为需要初始化
        if not hasattr(self, '_ai_mode_initialized') or not self._ai_mode_initialized:
            self._ai_mode_initialized = True
        
        # 运行AI模式游戏的一帧
        try:
            result = self.ai_game_page.run_one_frame()
            if result == "quit":
                self._ai_mode_initialized = False  # 标记需要重新初始化
                self.change_page(PageState.MAIN_MENU)
                return True
            elif result == "game_over":
                # 游戏结束，标记需要重新初始化
                self._ai_mode_initialized = False
                self.change_page(PageState.MAIN_MENU)
                return True
        except Exception as e:
            print(f"AI模式游戏运行错误: {e}")
            self._ai_mode_initialized = False
            self.change_page(PageState.MAIN_MENU)
        
        return True
    
    def handle_custom_mode(self):
        """处理自定义模式页面"""
        # 每次进入都重新初始化配置页面
        try:
            from custom_config_page import CustomConfigPage
            print("🔄 重新初始化自定义配置页面...")
            self.custom_config_page = CustomConfigPage(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            print("✅ 自定义配置页面加载成功")
        except Exception as e:
            print(f"❌ 自定义配置页面加载失败: {e}")
            import traceback
            traceback.print_exc()
            # 显示错误信息
            self.draw_background()
            error_text = safe_render_text(self.info_font, f"Custom Mode Loading Failed: {e}", RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(error_text, error_rect)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.change_page(PageState.MAIN_MENU)
                    return True
            return True
        
        # 运行自定义配置页面
        try:
            result = self.custom_config_page.run()
            print(f"自定义配置页面返回结果: {result}")  # 调试信息
            
            if result == 'back':
                # 返回主菜单时清除配置页面缓存
                if hasattr(self, 'custom_config_page'):
                    self.custom_config_page.clear_config_cache()
                    print("✅ 配置页面缓存已清除")
                self.change_page(PageState.MAIN_MENU)
                return True
            elif isinstance(result, dict) and result.get('type') == 'custom_game':
                # 跳转到自定义游戏页面
                print(f"跳转到自定义游戏页面，配置: {result['config']}")
                return self.handle_custom_game(result['config'])
            elif result == 'quit':
                return False
            else:
                print(f"未知的返回结果: {result}")
                return True
        except Exception as e:
            print(f"自定义配置页面运行错误: {e}")
            import traceback
            traceback.print_exc()
            self.change_page(PageState.MAIN_MENU)
            return True
        
        return True
    
    def handle_custom_mode_with_cache(self):
        """处理自定义模式页面 - 保留缓存"""
        # 重新初始化配置页面，但保留缓存
        try:
            from custom_config_page import CustomConfigPage
            print("🔄 重新初始化自定义配置页面（保留缓存）...")
            
            # 如果已有配置页面实例，保留其缓存
            if hasattr(self, 'custom_config_page') and self.custom_config_page:
                old_cache = getattr(self.custom_config_page, 'config_cache', {})
                print(f"💾 保存旧缓存: {list(old_cache.keys())}")
                
                # 创建新实例但不自动初始化
                self.custom_config_page = CustomConfigPage.__new__(CustomConfigPage)
                self.custom_config_page.screen = self.screen
                self.custom_config_page.width = SCREEN_WIDTH
                self.custom_config_page.height = SCREEN_HEIGHT
                
                # 先设置缓存再初始化
                self.custom_config_page.config_cache = old_cache
                self.custom_config_page.initialize_config(preserve_cache=True)
                print("💾 配置缓存已保留")
            else:
                self.custom_config_page = CustomConfigPage(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
                print("🆕 新建配置页面")
                
            print("✅ 自定义配置页面加载成功")
        except Exception as e:
            print(f"❌ 自定义配置页面加载失败: {e}")
            import traceback
            traceback.print_exc()
            # 显示错误信息
            self.draw_background()
            error_text = safe_render_text(self.info_font, f"Custom Mode Loading Failed: {e}", RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(error_text, error_rect)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.change_page(PageState.MAIN_MENU)
                    return True
            return True
        
        # 运行自定义配置页面
        try:
            result = self.custom_config_page.run()
            print(f"自定义配置页面返回结果: {result}")  # 调试信息
            
            if result == 'back':
                # 返回主菜单时清除配置页面缓存
                if hasattr(self, 'custom_config_page'):
                    self.custom_config_page.clear_cache()
                    print("✅ 配置页面缓存已清除")
                self.change_page(PageState.MAIN_MENU)
                return True
            elif isinstance(result, dict) and result.get('type') == 'custom_game':
                # 跳转到自定义游戏页面
                print(f"跳转到自定义游戏页面，配置: {result['config']}")
                return self.handle_custom_game(result['config'])
            elif result == 'quit':
                return False
            else:
                print(f"未知的返回结果: {result}")
                return True
        except Exception as e:
            print(f"自定义配置页面运行错误: {e}")
            import traceback
            traceback.print_exc()
            self.change_page(PageState.MAIN_MENU)
            return True
        
        return True
        
    def handle_custom_game(self, custom_config):
        """处理自定义游戏页面"""
        # 每次进入都重新初始化游戏页面
        try:
            from custom_game_page import CustomGamePage
            print("🔄 重新初始化自定义游戏页面...")
            print(f"📋 配置信息: {custom_config}")
            self.custom_game_page = CustomGamePage(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT, custom_config)
            print("✅ 自定义游戏页面加载成功")
        except Exception as e:
            print(f"❌ 自定义游戏页面加载失败: {e}")
            import traceback
            traceback.print_exc()
            # 显示错误信息
            self.draw_background()
            error_text = safe_render_text(self.info_font, f"Custom Game Loading Failed: {e}", RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(error_text, error_rect)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.change_page(PageState.MAIN_MENU)
                    return True
            return True
        
        # 运行自定义游戏页面
        try:
            result = self.custom_game_page.run()
            if result == 'back':
                # 返回自定义配置页面时清除游戏页面缓存，但保留配置页面缓存
                if hasattr(self, 'custom_game_page'):
                    self.custom_game_page.clear_game_cache()
                    print("✅ 游戏页面缓存已清除")
                return self.handle_custom_mode_with_cache()
            elif result == 'quit':
                return False
        except Exception as e:
            print(f"自定义游戏页面运行错误: {e}")
            self.change_page(PageState.MAIN_MENU)
            return True
        
        return True

def main():
    game_manager = GameManager(screen)
    game_manager.run()

if __name__ == "__main__":
    main()
