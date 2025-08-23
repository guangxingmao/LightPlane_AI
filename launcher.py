import pygame
import sys
import os

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

# 初始化pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('LightPlane Fighter - Game Launcher')

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
    """安全地渲染文本，如果字体失败则使用备用方案"""
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
    """获取简单的系统字体，不进行中文测试"""
    try:
        # 直接使用系统默认字体
        return pygame.font.SysFont(None, size)
    except:
        try:
            return pygame.font.Font(None, size)
        except:
            return None

# 字体设置
try:
    title_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 48)  # 微软雅黑
    button_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 24)
except:
    title_font = pygame.font.SysFont("arial", 48)
    button_font = pygame.font.SysFont("arial", 24)

# 页面状态枚举
class PageState:
    MAIN_MENU = "main_menu"
    TRADITIONAL_MODE = "traditional_mode"
    DUAL_MODE = "dual_mode"
    EASTER_EGG_MODE = "easter_egg_mode"
    AI_MODE = "ai_mode"
    CUSTOM_MODE = "custom_mode"

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.hovered = False
        
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
        
        # 初始化页面状态标志
        self._traditional_mode_initialized = False
        self._dual_mode_initialized = False
        self._easter_egg_mode_initialized = False
    
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
            elif self.current_page == PageState.EASTER_EGG_MODE:
                running = self.handle_easter_egg_mode()
            elif self.current_page == PageState.AI_MODE:
                running = self.handle_ai_mode()
            elif self.current_page == PageState.CUSTOM_MODE:
                running = self.handle_custom_mode()
            
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
            Button(center_x, 200, button_width, button_height, "Traditional Mode", LIGHT_BLUE, BLUE),
            Button(center_x, 280, button_width, button_height, "Dual Player Mode", GREEN, (0, 200, 0)),
            Button(center_x, 360, button_width, button_height, "Easter Egg Mode 🥚", (255, 20, 147), (255, 105, 180)),
            Button(center_x, 440, button_width, button_height, "AI Mode", YELLOW, (200, 200, 0)),
            Button(center_x, 520, button_width, button_height, "Custom Mode", RED, (200, 0, 0))
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
                    elif i == 2:  # 彩蛋模式
                        self.change_page(PageState.EASTER_EGG_MODE)
                    elif i == 3:  # AI模式
                        self.change_page(PageState.AI_MODE)
                    elif i == 4:  # 自定义模式
                        self.change_page(PageState.CUSTOM_MODE)
        
        return True
    
    def draw_main_menu(self, buttons):
        """绘制主菜单"""
        # 绘制背景
        self.draw_background()
        
        # 绘制标题
        title_text = safe_render_text(self.title_font, "LightPlane Fighter 3.0", WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        
        # 添加标题阴影效果
        shadow_text = safe_render_text(self.title_font, "LightPlane Fighter 3.0", BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 3, 103))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # 绘制副标题
        subtitle_text = safe_render_text(self.info_font, "Select Game Mode to Start", WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # 绘制按钮
        for button in buttons:
            button.draw(self.screen)
        
        # 绘制底部信息
        info_text = safe_render_text(self.small_font, "Press ESC to Return to Main Menu", WHITE)
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
            error_text = safe_render_text(self.info_font, "Dual Game Module Loading Failed", RED)
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
            error_text = safe_render_text(self.info_font, "Traditional Game Module Loading Failed", RED)
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
            error_text = safe_render_text(self.info_font, "Easter Egg Game Module Loading Failed", RED)
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
        self.draw_background()
        
        # 绘制标题
        title_text = safe_render_text(self.title_font, "AI Mode", WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 绘制说明
        text = safe_render_text(self.info_font, "AI Mode - Coming Soon...", WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(text, rect)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.change_page(PageState.MAIN_MENU)
                return True
        
        return True
    
    def handle_custom_mode(self):
        """处理自定义模式页面"""
        self.draw_background()
        
        # 绘制标题
        title_text = safe_render_text(self.title_font, "Custom Mode", WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 绘制说明
        text = safe_render_text(self.info_font, "Custom Mode - Coming Soon...", WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(text, rect)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.change_page(PageState.MAIN_MENU)
                return True
        
        return True

def main():
    game_manager = GameManager(screen)
    game_manager.run()

if __name__ == "__main__":
    main()
