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

# 初始化pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('雷霆战机 - 游戏启动器')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
LIGHT_BLUE = (100, 150, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

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
        
        # 绘制按钮文字
        text_surface = button_font.render(self.text, True, BLACK)
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
        self.current_page = PageState.MAIN_MENU
        self.clock = pygame.time.Clock()
        
        # 游戏相关变量
        self.game_objects = {}
        self.init_game_objects()
    
    def init_game_objects(self):
        """初始化游戏对象"""
        if not GAME_MODULES_LOADED:
            return
            
        try:
            # 这里可以初始化游戏相关的对象
            pass
        except Exception as e:
            print(f"初始化游戏对象失败: {e}")
    
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
            Button(center_x, 200, button_width, button_height, "传统模式", LIGHT_BLUE, BLUE),
            Button(center_x, 280, button_width, button_height, "双人模式", GREEN, (0, 200, 0)),
            Button(center_x, 360, button_width, button_height, "AI模式", YELLOW, (200, 200, 0)),
            Button(center_x, 440, button_width, button_height, "自定义模式", RED, (200, 0, 0))
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
        
        return True
    
    def draw_main_menu(self, buttons):
        """绘制主菜单"""
        # 绘制背景
        self.draw_background()
        
        # 绘制标题
        title_text = title_font.render("雷霆战机 3.0", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        
        # 添加标题阴影效果
        shadow_text = title_font.render("雷霆战机 3.0", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 3, 103))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # 绘制副标题
        subtitle_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 20) if os.path.exists("C:/Windows/Fonts/msyh.ttc") else pygame.font.SysFont("arial", 20)
        subtitle_text = subtitle_font.render("选择游戏模式开始游戏", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # 绘制按钮
        for button in buttons:
            button.draw(self.screen)
        
        # 绘制底部信息
        info_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 16) if os.path.exists("C:/Windows/Fonts/msyh.ttc") else pygame.font.SysFont("arial", 16)
        info_text = info_font.render("按ESC键返回主菜单", True, WHITE)
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
        # 绘制双人模式界面
        self.draw_dual_mode()
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.change_page(PageState.MAIN_MENU)
                    return True
        
        return True
    
    def draw_dual_mode(self):
        """绘制双人模式界面"""
        # 绘制背景
        self.draw_background()
        
        # 绘制标题
        title_text = title_font.render("双人模式", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 绘制游戏说明
        info_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 20) if os.path.exists("C:/Windows/Fonts/msyh.ttc") else pygame.font.SysFont("arial", 20)
        
        instructions = [
            "玩家1: 方向键控制移动",
            "玩家2: WASD键控制移动",
            "空格键: 暂停/继续音乐",
            "`键: 显示/隐藏鼠标",
            "Q键: 退出游戏"
        ]
        
        for i, instruction in enumerate(instructions):
            text = info_font.render(instruction, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 40))
            self.screen.blit(text, rect)
        
        # 绘制返回按钮
        back_button = Button(50, SCREEN_HEIGHT - 80, 120, 40, "返回主菜单", GRAY, LIGHT_BLUE)
        back_button.draw(self.screen)
        
        # 绘制开始游戏按钮
        start_button = Button(SCREEN_WIDTH - 170, SCREEN_HEIGHT - 80, 120, 40, "开始游戏", GREEN, (0, 200, 0))
        start_button.draw(self.screen)
        
        # 处理按钮点击
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:  # 左键点击
            if back_button.rect.collidepoint(mouse_pos):
                self.change_page(PageState.MAIN_MENU)
            elif start_button.rect.collidepoint(mouse_pos):
                self.start_dual_game()
    
    def start_dual_game(self):
        """启动双人游戏"""
        try:
            # 这里直接启动双人游戏，而不是通过os.system
            # 可以在这里集成原有的游戏代码
            print("启动双人游戏...")
            # 暂时返回主菜单，后续可以在这里集成游戏
            self.change_page(PageState.MAIN_MENU)
        except Exception as e:
            print(f"启动双人游戏失败: {e}")
    
    def handle_traditional_mode(self):
        """处理传统模式页面"""
        self.draw_background()
        
        # 绘制标题
        title_text = title_font.render("传统模式", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 绘制说明
        info_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 20) if os.path.exists("C:/Windows/Fonts/msyh.ttc") else pygame.font.SysFont("arial", 20)
        text = info_font.render("传统模式功能开发中...", True, WHITE)
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
    
    def handle_ai_mode(self):
        """处理AI模式页面"""
        self.draw_background()
        
        # 绘制标题
        title_text = title_font.render("AI模式", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 绘制说明
        info_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 20) if os.path.exists("C:/Windows/Fonts/msyh.ttc") else pygame.font.SysFont("arial", 20)
        text = info_font.render("AI模式功能开发中...", True, WHITE)
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
        title_text = title_font.render("自定义模式", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 绘制说明
        info_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 20) if os.path.exists("C:/Windows/Fonts/msyh.ttc") else pygame.font.SysFont("arial", 20)
        text = info_font.render("自定义模式功能开发中...", True, WHITE)
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
