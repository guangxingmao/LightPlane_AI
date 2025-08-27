import pygame
import sys
import os
import random
import math

# 导入游戏相关模块
from plane_sprites import *
from game_function import check_KEY, check_mouse
from Tools import Music, Button as GameButton
from font_manager import render_chinese_text, get_chinese_font

class EasterEggPage:
    """彩蛋模式游戏页面类 - 特殊效果和有趣玩法"""
    
    def __init__(self, screen):
        # 创建游戏屏幕
        self.screen = screen
        
        # 获取屏幕尺寸
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # 设置窗口的标题
        pygame.display.set_caption('LightPlane Fighter')
        # 创建游戏时钟
        self.clock = pygame.time.Clock()
        # 生命数量
        self.life = 5
        # 分数
        self.score = 0
        # 彩蛋等级
        self.easter_egg_level = 1
        # 特殊效果计时器
        self.special_effect_timer = 0
        # 彩虹模式
        self.rainbow_mode = False
        # 彩虹颜色索引
        self.rainbow_color_index = 0
        # 彩虹颜色列表
        self.rainbow_colors = [
            (255, 0, 0),    # 红
            (255, 127, 0),  # 橙
            (255, 255, 0),  # 黄
            (0, 255, 0),    # 绿
            (0, 0, 255),    # 蓝
            (75, 0, 130),   # 靛
            (148, 0, 211)   # 紫
        ]
        
        # 设置背景音乐
        self.BGM = Music('./music/bgm.mp3')
        # 创建按钮对象
        self.button = GameButton()

        # 调用私有方法创建精灵组
        self.__creat_sprites()
        
        # 创建粒子系统
        self.particles = []
        
        # 创建彩蛋特效
        self.easter_egg_effects = []

    def start_game(self):
        '''开始游戏'''
        while True:
            pygame.init()

            # 判断是否有音乐在播放，如果没有，就播放
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

            # 5. 更新粒子系统
            self.__update_particles()

            # 6. 显示生命和分数
            self.show_life()

            # 7. 更新屏幕显示
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

        # 更新粒子系统
        self.__update_particles()

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # 空格键触发彩蛋特效
                self.__trigger_easter_egg()
                
            print(event)
            # 创建虚拟的hero2和hero3对象，避免None错误
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
                if event.type == pygame.MOUSEMOTION and self.life > 0:
                    (x,y) = pygame.mouse.get_pos()
                    self.hero1.rect.centerx = x
                    self.hero1.rect.centery = y
                    
                    # 创建跟随粒子效果
                    self.__create_follow_particles(x, y)
        
        return False

    def __trigger_easter_egg(self):
        """触发彩蛋特效"""
        self.easter_egg_level += 1
        self.special_effect_timer = 300  # 5秒特效
        
        # 根据等级触发不同特效
        if self.easter_egg_level % 3 == 0:
            self.rainbow_mode = True
            self.special_effect_timer = 180  # 3秒彩虹模式
        
        # 创建爆炸粒子效果
        for _ in range(20):
            particle = {
                'x': self.hero1.rect.centerx,
                'y': self.hero1.rect.centery,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-5, 5),
                'life': 60,
                'color': random.choice(self.rainbow_colors),
                'size': random.randint(2, 6)
            }
            self.particles.append(particle)

    def __create_follow_particles(self, x, y):
        """创建跟随粒子效果"""
        if random.random() < 0.3:  # 30%概率创建粒子
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'life': 30,
                'color': (255, 255, 255),
                'size': random.randint(1, 3)
            }
            self.particles.append(particle)

    def __update_particles(self):
        """更新粒子系统"""
        # 更新现有粒子
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            # 绘制粒子
            if particle['life'] > 0:
                color = particle['color']
                if self.rainbow_mode and self.special_effect_timer > 0:
                    color = self.rainbow_colors[self.rainbow_color_index % len(self.rainbow_colors)]
                
                pygame.draw.circle(self.screen, color, 
                                 (int(particle['x']), int(particle['y'])), 
                                 particle['size'])
            else:
                self.particles.remove(particle)
        
        # 更新彩虹颜色索引
        if self.rainbow_mode and self.special_effect_timer > 0:
            if self.special_effect_timer % 10 == 0:  # 每10帧切换颜色
                self.rainbow_color_index += 1
        
        # 更新特效计时器
        if self.special_effect_timer > 0:
            self.special_effect_timer -= 1
            if self.special_effect_timer == 0:
                self.rainbow_mode = False

    def __check_collide(self):
        '''碰撞检测'''
        # 子弹碰撞敌人
        hit_enemies = pygame.sprite.groupcollide(self.hero1.bullets, self.enemy_group, True, True)
        if hit_enemies:
            self.score += 1
            # 敌人死亡时，将其子弹转移到全局子弹组，让子弹继续存在
            # hit_enemies的键是子弹，值是敌人列表
            for player_bullet, enemies in hit_enemies.items():
                for enemy in enemies:
                    # 将敌机的所有子弹复制到全局子弹组，并设置子弹的独立属性
                    for enemy_bullet in enemy.bullets:
                        # 创建新的子弹实例，避免引用问题
                        new_bullet = Bullet_Enemy()
                        new_bullet.rect = enemy_bullet.rect.copy()
                        new_bullet.speed = enemy_bullet.speed
                        self.global_enemy_bullets.add(new_bullet)
                    # 清空敌机的子弹组
                    enemy.bullets.empty()
            # 创建击中粒子效果
            for player_bullet, enemies in hit_enemies.items():
                for enemy in enemies:
                    for _ in range(10):
                        particle = {
                            'x': enemy.rect.centerx,
                            'y': enemy.rect.centery,
                            'vx': random.uniform(-3, 3),
                            'vy': random.uniform(-3, 3),
                            'life': 40,
                            'color': (255, 255, 0),  # 黄色爆炸
                            'size': random.randint(2, 4)
                        }
                        self.particles.append(particle)

        # 敌人碰撞英雄
        enemys1 = pygame.sprite.spritecollide(
            self.hero1, self.enemy_group, True)
        if len(enemys1) > 0 and self.life > 0:
            self.life -= 1
            if self.life == 0:
                # 英雄死亡后，移除屏幕
                self.hero1.rect.bottom = 0
                self.hero1.rect.x = self.screen_width
                self.hero1.kill()
        
        # 敌人子弹碰撞英雄1 - 使用全局子弹组
        bullets1 = pygame.sprite.spritecollide(
            self.hero1, self.global_enemy_bullets, True)
        if len(bullets1) > 0 and self.life > 0:
            self.life -= 1
            if self.life == 0:
                # 英雄死亡后，移除屏幕
                self.hero1.rect.bottom = 0
                self.hero1.rect.x = self.screen_width
                self.hero1.kill()

        # 当玩家死亡，游戏结束
        if self.life == 0:
            return True
        
        return False

    def __update_sprites(self):
        '''更新精灵组'''

        if self.button.pause_game % 2 != 0:
            # 绘制所有精灵组
            for group in [self.back_group, self.hero_group1, self.hero1.bullets, self.enemy_group, self.global_enemy_bullets]: 
                group.draw(self.screen)
            
            self.button.update()
            # 重新设置按钮位置到左下角
            self.button.rect.x = 20
            self.button.rect.bottom = self.screen_height - 20
            self.screen.blit(self.button.image,(self.button.rect.x,self.button.rect.y))

        elif self.button.pause_game % 2 == 0:
            # 绘制和更新所有精灵组
            for group in [self.back_group, self.hero_group1, self.hero1.bullets, self.enemy_group]:
                group.draw(self.screen)
                group.update()
            # 绘制和更新全局敌人子弹组
            self.global_enemy_bullets.draw(self.screen)
            self.global_enemy_bullets.update()
            
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
        pos3 = (0, 40)
        pos4 = (0, 60)
        
        # 根据特效状态选择颜色
        if self.rainbow_mode and self.special_effect_timer > 0:
            color = self.rainbow_colors[self.rainbow_color_index % len(self.rainbow_colors)]
        else:
            color = (0, 0, 0)
        
        # 使用中文文本
        text1 = f'生命: {self.life}'
        text2 = f'分数: {self.score}'
        text3 = f'彩蛋等级: {self.easter_egg_level}'
        text4 = f'特效: {"彩虹模式!" if self.rainbow_mode and self.special_effect_timer > 0 else "按空格键触发彩蛋"}'
        
        # 使用字体管理器渲染中文文本
        text_fmt1 = render_chinese_text(text1, 20, color)
        text_fmt2 = render_chinese_text(text2, 20, color)
        text_fmt3 = render_chinese_text(text3, 20, color)
        text_fmt4 = render_chinese_text(text4, 20, color)
        
        self.screen.blit(text_fmt1, pos1)
        self.screen.blit(text_fmt2, pos2)
        self.screen.blit(text_fmt3, pos3)
        self.screen.blit(text_fmt4, pos4)

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
        # 添加敌人到敌机组
        self.enemy_group.add(self.enemy)
        
        # 全局敌人子弹组 - 管理所有敌人的子弹，即使敌人死亡子弹也继续存在
        self.global_enemy_bullets = pygame.sprite.Group()

        # 英雄组 - 只有玩家1
        self.hero1 = Hero('./images/life.png')
        # 设置英雄1在左侧居中
        self.hero1.rect.x = 50
        self.hero1.rect.centery = self.screen_height // 2
        self.hero_group1 = pygame.sprite.Group(self.hero1)
    
    def reset_game(self):
        """重置游戏状态"""
        # 重置生命和分数
        self.life = 5
        self.score = 0
        self.easter_egg_level = 1
        self.special_effect_timer = 0
        self.rainbow_mode = False
        self.rainbow_color_index = 0
        # 清空粒子
        self.particles.clear()
        # 重新创建精灵组
        self.__creat_sprites()
