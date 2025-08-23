import pygame
import sys
import os

# 导入游戏相关模块
from plane_sprites import *
from game_function import check_KEY, check_mouse
from Tools import Music, Button as GameButton

class TraditionalGamePage:
    """传统模式游戏页面类 - 只有玩家1"""
    
    def __init__(self, screen):
        # 创建游戏屏幕
        self.screen = screen
        
        # 获取屏幕尺寸
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # 设置窗口的标题
        pygame.display.set_caption('LightPlane Fighter - Traditional Mode')
        # 创建游戏时钟
        self.clock = pygame.time.Clock()
        # 生命数量
        self.life1 = 3
        # 分数
        self.score1 = 0
        # 设置背景音乐
        self.BGM = Music('./music/bgm1.mp3')
        #创建按钮对象
        # 可以控制鼠标显示和控制游戏开始暂停
        self.button = GameButton()

        # 调用私有方法创建精灵组
        self.__creat_sprites()
    
    def reset_game(self):
        """重置游戏状态"""
        # 重置生命和分数
        self.life1 = 3
        self.score1 = 0
        # 重新创建精灵组
        self.__creat_sprites()

    def start_game(self):
        '''开始游戏'''
        while True:
            pygame.init()

            # 判断是否有音乐在播放，如果没有，就播放
            # 也就是循环播放背景音乐
            if not pygame.mixer.music.get_busy():
                self.BGM.play_music()
            # 1. 设置刷新帧率
            self.clock.tick(60)
            # 2. 事件监听
            should_quit = self.__check_event()
            if should_quit:
                return "quit"

            # 3. 碰撞检测
            game_over = self.__check_collide()
            if game_over:
                return "game_over"

            # 4. 更新精灵组
            self.__update_sprites()

            # 5. 显示生命和分数
            self.show_life()

            # 5. 更新屏幕显示
            pygame.display.update()
    
    def run_one_frame(self):
        '''运行一帧游戏 - 用于与启动器集成'''
        # 判断是否有音乐在播放，如果没有，就播放
        if not pygame.mixer.music.get_busy():
            self.BGM.play_music()
        
        # 事件监听
        should_quit = self.__check_event()
        if should_quit:
            return "quit"

        # 碰撞检测
        game_over = self.__check_collide()
        if game_over:
            return "game_over"

        # 更新精灵组
        self.__update_sprites()

        # 显示生命和分数
        self.show_life()

        return "running"

    def __check_event(self):
        """事件监听"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
                
            print(event)
            # 创建虚拟的hero2和hero3对象，避免None错误（传统模式不需要僚机）
            dummy_hero2 = type('DummyHero', (), {
                'fire': lambda *args: None, 
                'moving_right': False, 
                'moving_left': False, 
                'moving_up': False, 
                'moving_down': False,
                'time_count': 1
            })()
            dummy_hero3 = type('DummyHero', (), {
                'fire': lambda *args: None, 
                'moving_right': False, 
                'moving_left': False, 
                'moving_up': False, 
                'moving_down': False,
                'time_count': 1
            })()
            check_KEY(self.hero1, dummy_hero2, dummy_hero3, self.enemy,
                      event, self.enemy_group, self.BGM, self.button)
            check_mouse(event, self.button)

            # 游戏开始时候，主战机跟随鼠标移动
            if self.button.pause_game % 2 == 0 and self.button.count_mouse % 2 == 0:
                if event.type == pygame.MOUSEMOTION and self.life1 > 0:
                    (x,y) = pygame.mouse.get_pos()
                    self.hero1.rect.centerx = x
                    self.hero1.rect.centery = y
        
        return False

    def __check_collide(self):
        '''碰撞检测'''
        # 子弹碰撞敌人（只检测主英雄的子弹）
        if pygame.sprite.groupcollide(self.hero1.bullets, self.enemy_group, True, True):
            self.score1 += 1

        # 敌人碰撞英雄
        enemys1 = pygame.sprite.spritecollide(
            self.hero1, self.enemy_group, True)
        if len(enemys1) > 0 and self.life1 > 0:
            self.life1 -= 1
            if self.life1 == 0:
                # 英雄死亡后，移除屏幕
                self.hero1.rect.bottom = 0
                self.hero1.rect.x = self.screen_width
                self.hero1.kill()

        # 当玩家死亡，游戏结束
        if self.life1 == 0:
            return True
        
        return False

    def __update_sprites(self):
        '''更新精灵组'''

        if self.button.pause_game % 2 != 0:
            for group in [self.back_group, self.hero_group1, self.hero1.bullets, self.enemy_group, self.enemy.bullets,]: 
                group.draw(self.screen)
                self.button.update()
                # 重新设置按钮位置到左下角
                self.button.rect.x = 20
                self.button.rect.bottom = self.screen_height - 20
                self.screen.blit(self.button.image,(self.button.rect.x,self.button.rect.y))

        elif self.button.pause_game % 2 == 0:
            for group in [self.back_group, self.hero_group1, self.hero1.bullets, self.enemy_group, self.enemy.bullets,]:
                group.draw(self.screen)
                group.update()
                self.button.update()
                # 重新设置按钮位置到左下角
                self.button.rect.x = 20
                self.button.rect.bottom = self.screen_height - 20
                self.screen.blit(self.button.image,(self.button.rect.x,self.button.rect.y))
        
        # 手动更新背景位置以适应新的屏幕尺寸
        for bg in self.back_group:
            if bg.rect.x <= -self.screen_width:
                bg.rect.x = self.screen_width

    def show_life(self):
        '''显示字体'''
        pygame.font.init()
        pos1 = (0, 0)
        pos2 = (0, 20)
        color = (0, 0, 0)
        text1 = 'LIFE: ' + str(self.life1)
        text2 = 'SCORE: ' + str(self.score1)
        try:
            cur_font = pygame.font.SysFont(None, 20)
        except:
            cur_font = pygame.font.Font(None, 20)
        text_fmt1 = cur_font.render(text1, 1, color)
        text_fmt2 = cur_font.render(text2, 1, color)
        self.screen.blit(text_fmt1, pos1)
        self.screen.blit(text_fmt2, pos2)

    def __creat_sprites(self):
        '''创建精灵组'''
        # 背景组 - 创建适应屏幕尺寸的背景
        bg1 = Background()
        bg2 = Background(True)
        
        # 调整背景图片大小以适应屏幕
        bg1.image = pygame.transform.scale(bg1.image, (self.screen_width, self.screen_height))
        bg2.image = pygame.transform.scale(bg2.image, (self.screen_width, self.screen_height))
        
        # 重新设置背景位置
        bg1.rect = bg1.image.get_rect()
        bg2.rect = bg2.image.get_rect()
        bg2.rect.x = self.screen_width
        
        self.back_group = pygame.sprite.Group(bg1, bg2)
        # 敌机组
        self.enemy = Enemy()
        self.enemy_group = pygame.sprite.Group()

        # 英雄组 - 只有玩家1
        self.hero1 = Hero('./images/life.png')
        # 设置英雄1在左侧居中
        self.hero1.rect.x = 50
        self.hero1.rect.centery = self.screen_height // 2
        self.hero_group1 = pygame.sprite.Group(self.hero1)
