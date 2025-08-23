import pygame
import sys
import os

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

class Launcher:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # 创建按钮
        button_width = 200
        button_height = 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.buttons = [
            Button(center_x, 200, button_width, button_height, "传统模式", LIGHT_BLUE, BLUE),
            Button(center_x, 280, button_width, button_height, "双人模式", GREEN, (0, 200, 0)),
            Button(center_x, 360, button_width, button_height, "AI模式", YELLOW, (200, 200, 0)),
            Button(center_x, 440, button_width, button_height, "自定义模式", RED, (200, 0, 0))
        ]
        
        # 背景图片（如果存在）
        self.background = None
        if os.path.exists('./images/background.png'):
            try:
                self.background = pygame.image.load('./images/background.png')
                self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except:
                self.background = None
    
    def draw(self):
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # 渐变背景
            for y in range(SCREEN_HEIGHT):
                color = (
                    int(50 + (y / SCREEN_HEIGHT) * 100),
                    int(100 + (y / SCREEN_HEIGHT) * 100),
                    int(150 + (y / SCREEN_HEIGHT) * 100)
                )
                pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
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
        for button in self.buttons:
            button.draw(self.screen)
        
        # 绘制底部信息
        info_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 16) if os.path.exists("C:/Windows/Fonts/msyh.ttc") else pygame.font.SysFont("arial", 16)
        info_text = info_font.render("按ESC键退出启动器", True, WHITE)
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(info_text, info_rect)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            
            # 处理按钮事件
            for i, button in enumerate(self.buttons):
                if button.handle_event(event):
                    self.handle_button_click(i)
        
        return True
    
    def handle_button_click(self, button_index):
        if button_index == 0:  # 传统模式
            print("启动传统模式...")
            self.launch_traditional_mode()
        elif button_index == 1:  # 双人模式
            print("启动双人模式...")
            self.launch_dual_mode()
        elif button_index == 2:  # AI模式
            print("启动AI模式...")
            self.launch_ai_mode()
        elif button_index == 3:  # 自定义模式
            print("启动自定义模式...")
            self.launch_custom_mode()
    
    def launch_traditional_mode(self):
        """启动传统模式（单人游戏）"""
        try:
            # 这里可以启动传统模式的游戏
            print("传统模式功能待实现")
            # 可以在这里添加启动传统模式的代码
        except Exception as e:
            print(f"启动传统模式失败: {e}")
    
    def launch_dual_mode(self):
        """启动双人模式"""
        try:
            # 启动原有的双人游戏
            os.system("python plane_mian.py")
        except Exception as e:
            print(f"启动双人模式失败: {e}")
    
    def launch_ai_mode(self):
        """启动AI模式"""
        try:
            print("AI模式功能待实现")
            # 可以在这里添加启动AI模式的代码
        except Exception as e:
            print(f"启动AI模式失败: {e}")
    
    def launch_custom_mode(self):
        """启动自定义模式"""
        try:
            print("自定义模式功能待实现")
            # 可以在这里添加启动自定义模式的代码
        except Exception as e:
            print(f"启动自定义模式失败: {e}")
    
    def run(self):
        """运行启动器主循环"""
        running = True
        while running:
            running = self.handle_events()
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    launcher = Launcher()
    launcher.run()

if __name__ == "__main__":
    main()
