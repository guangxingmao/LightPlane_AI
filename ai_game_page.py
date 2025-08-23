import pygame
import sys
import os
import random
import math

# 导入游戏相关模块
from plane_sprites import *
from game_function import check_KEY, check_mouse
from Tools import Music, Button as GameButton

# 注意：目前使用优化的简单AI控制器，强化学习控制器暂时未使用

class OptimizedAIController:
    """优化的AI控制器 - 减少卡顿，提高流畅度"""
    
    def __init__(self, hero, enemy_group, screen_width, screen_height, is_player1=True):
        self.hero = hero
        self.enemy_group = enemy_group
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_player1 = is_player1
        
        # 优化参数
        self.decision_timer = 0
        self.decision_interval = 20  # 每20帧做一次决策，减少卡顿
        self.movement_pattern = 'patrol'
        self.last_move_time = 0
        self.move_duration = 40  # 每次移动持续40帧
        
        # 移动目标
        self.target_x = 0
        self.target_y = 0
        self.moving = False
        
        # 根据是玩家1还是玩家2设置不同的行为模式
        if is_player1:
            self.patrol_center_x = self.screen_width * 0.25
            self.patrol_center_y = self.screen_height * 0.5
        else:
            # AI飞机现在在左下角，巡逻中心也调整到左侧
            self.patrol_center_x = self.screen_width * 0.25
            self.patrol_center_y = self.screen_height * 0.75
        
        # 初始化目标位置
        self.target_x = self.patrol_center_x
        self.target_y = self.patrol_center_y
        
    def update(self, game_started=True, game_paused=False):
        """更新AI决策和移动"""
        # 如果游戏未开始或已暂停，不执行AI逻辑
        if not game_started or game_paused:
            return
            
        self.decision_timer += 1
        
        # 减少决策频率，但保持移动流畅
        if self.decision_timer >= self.decision_interval:
            self.make_decision()
            self.decision_timer = 0
            self.last_move_time = 0
        
        # 持续执行移动，让移动更流畅
        if self.moving and self.last_move_time < self.move_duration:
            self.execute_movement()
            self.last_move_time += 1
        elif self.last_move_time >= self.move_duration:
            self.moving = False
    
    def make_decision(self):
        """AI决策逻辑"""
        # 寻找最近的敌人
        nearest_enemy = self.find_nearest_enemy()
        
        if nearest_enemy:
            # 计算与敌人的距离
            distance = self.calculate_distance(self.hero.rect.center, nearest_enemy.rect.center)
            
            # 根据距离决定行为
            if distance < 80:  # 敌人太近时躲避
                self.movement_pattern = 'evade'
                self.set_evade_target(nearest_enemy)
            elif distance < 150:  # 中等距离时追击
                self.movement_pattern = 'chase'
                self.set_chase_target(nearest_enemy)
            else:  # 远距离时巡逻
                self.movement_pattern = 'patrol'
                self.set_patrol_target()
            
            # 自动射击
            self.auto_shoot(nearest_enemy)
        else:
            # 没有敌人时巡逻
            self.set_patrol_target()
    
    def set_chase_target(self, enemy):
        """设置追击目标"""
        # 计算追击位置（稍微偏移，避免直接碰撞）
        dx = enemy.rect.centerx - self.hero.rect.centerx
        dy = enemy.rect.centery - self.hero.rect.centery
        
        # 标准化向量
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            # 追击位置在敌人前方一点
            offset = 30
            self.target_x = enemy.rect.centerx - (dx / length) * offset
            self.target_y = enemy.rect.centery - (dy / length) * offset
            
            # 边界检查
            if self.is_player1:
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            else:
                # AI飞机现在在左下角，限制在左侧区域
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            
            self.target_y = max(50, min(self.screen_height - 50, self.target_y))
            self.moving = True
    
    def set_evade_target(self, enemy):
        """设置躲避目标"""
        # 计算远离方向
        dx = self.hero.rect.centerx - enemy.rect.centerx
        dy = self.hero.rect.centery - enemy.rect.centery
        
        # 标准化向量
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            # 躲避位置在远离敌人的方向
            evade_distance = 100
            self.target_x = self.hero.rect.centerx + (dx / length) * evade_distance
            self.target_y = self.hero.rect.centery + (dy / length) * evade_distance
            
            # 边界检查
            if self.is_player1:
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            else:
                # AI飞机现在在左下角，限制在左侧区域
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            
            self.target_y = max(50, min(self.screen_height - 50, self.target_y))
            self.moving = True
    
    def set_patrol_target(self):
        """设置巡逻目标"""
        patrol_radius = 80
        
        # 在巡逻区域内随机选择目标点
        if random.random() < 0.3:  # 30%概率改变巡逻目标
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, patrol_radius)
            
            self.target_x = self.patrol_center_x + math.cos(angle) * distance
            self.target_y = self.patrol_center_y + math.sin(angle) * distance
            
            # 边界检查
            if self.is_player1:
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            else:
                # AI飞机现在在左下角，限制在左侧区域
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            
            self.target_y = max(50, min(self.screen_height - 50, self.target_y))
            self.moving = True
    
    def execute_movement(self):
        """执行移动"""
        if not self.moving:
            return
        
        # 计算到目标的距离
        dx = self.target_x - self.hero.rect.centerx
        dy = self.target_y - self.hero.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        # 如果已经接近目标，停止移动
        if distance < 5:
            self.moving = False
            return
        
        # 平滑移动
        move_speed = 2  # 降低移动速度，减少卡顿
        if distance > 0:
            dx = (dx / distance) * move_speed
            dy = (dy / distance) * move_speed
        
        # 更新位置
        new_x = self.hero.rect.centerx + dx
        new_y = self.hero.rect.centery + dy
        
        # 边界检查
        if self.is_player1:
            new_x = max(50, min(self.screen_width * 0.4, new_x))
        else:
            # AI飞机现在在左下角，限制在左侧区域
            new_x = max(50, min(self.screen_width * 0.4, new_x))
        
        new_y = max(50, min(self.screen_height - 50, new_y))
        
        self.hero.rect.centerx = new_x
        self.hero.rect.centery = new_y
    
    def find_nearest_enemy(self):
        """找到最近的敌人"""
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in self.enemy_group:
            distance = self.calculate_distance(self.hero.rect.center, enemy.rect.center)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        
        return nearest_enemy
    
    def calculate_distance(self, pos1, pos2):
        """计算两点间距离"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def auto_shoot(self, enemy):
        """自动射击 - 现在由事件系统处理，这里保留方法但不执行射击"""
        # 射击现在由AI_FIRE_EVENT事件自动处理
        pass

class AIGamePage:
    """AI模式游戏页面类 - 玩家1 + AI控制的玩家2"""
    
    def __init__(self, screen):
        # 创建游戏屏幕
        self.screen = screen
        
        # 获取屏幕尺寸
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # 设置窗口的标题
        pygame.display.set_caption('LightPlane Fighter - Player + AI Mode 🤖')
        # 创建游戏时钟
        self.clock = pygame.time.Clock()
        
        # 设置AI飞机自动射击事件
        self.AI_FIRE_EVENT = pygame.USEREVENT + 10
        pygame.time.set_timer(self.AI_FIRE_EVENT, 400)  # 每400毫秒发射一次
        
        # 生命数量
        self.life1 = 3
        self.life2 = 3
        # 分数
        self.score1 = 0
        self.score2 = 0
        # AI性能统计
        self.ai_kills = 0
        self.ai_deaths = 0
        
        # 设置背景音乐
        self.BGM = Music('./music/bgm.mp3')
        # 创建按钮对象
        self.button = GameButton()

        # 调用私有方法创建精灵组
        self.__creat_sprites()
        
        # 创建玩家2的AI控制器 - 尝试使用训练好的模型
        try:
            from trained_ai_controller import create_ai_controller
            print("尝试使用训练好的AI模型...")
            self.ai_controller2 = create_ai_controller(
                self.hero2, self.enemy_group, 
                self.screen_width, self.screen_height, 
                controller_type="hybrid"  # 混合模式：优先训练模型，备用简单AI
            )
        except Exception as e:
            print(f"训练模型加载失败: {e}")
            print("使用优化的简单AI控制器")
            self.ai_controller2 = OptimizedAIController(self.hero2, self.enemy_group, self.screen_width, self.screen_height, False)

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

            # 3. 更新AI（只更新玩家2的AI）
            # 检查游戏是否开始和是否暂停
            game_started = self.button.count_mouse % 2 != 0  # 游戏开始标志（点击后为奇数）
            game_paused = self.button.pause_game % 2 != 0    # 游戏暂停标志
            self.ai_controller2.update(game_started, game_paused)

            # 4. 碰撞检测
            game_over = self.__check_collide()
            if game_over:
                return "game_over"

            # 5. 更新精灵组
            self.__update_sprites()

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

        # 更新AI（只更新玩家2的AI）
        # 检查游戏是否开始和是否暂停
        game_started = self.button.count_mouse % 2 != 0  # 游戏开始标志（点击后为奇数）
        game_paused = self.button.pause_game % 2 != 0    # 游戏暂停标志
        self.ai_controller2.update(game_started, game_paused)

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
        """事件监听 - 处理玩家1控制和退出暂停"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
                
            # 处理玩家1的键盘控制
            # 创建虚拟的hero3对象，避免None错误
            dummy_hero3 = type('DummyHero', (), {
                'fire': lambda *args: None, 
                'moving_right': False, 
                'moving_left': False, 
                'moving_up': False, 
                'moving_down': False,
                'time_count': 1
            })()
            # 创建虚拟的hero2对象，防止玩家控制AI飞机
            dummy_hero2 = type('DummyHero', (), {
                'fire': lambda *args: None, 
                'moving_right': False, 
                'moving_left': False, 
                'moving_up': False, 
                'moving_down': False,
                'time_count': 1
            })()
            
            # 只让玩家1响应键盘控制，AI飞机不受玩家控制
            check_KEY(self.hero1, dummy_hero2, dummy_hero3, self.enemy,
                      event, self.enemy_group, self.BGM, self.button)
            
            # 处理AI飞机自动射击事件
            if event.type == self.AI_FIRE_EVENT:
                if self.life2 > 0 and hasattr(self.hero2, 'time_count') and self.hero2.time_count > 0:
                    self.hero2.fire()
            
            # 处理鼠标事件（暂停按钮和玩家1移动）
            check_mouse(event, self.button)
            
            # 游戏开始时候，玩家1跟随鼠标移动
            if self.button.pause_game % 2 == 0 and self.button.count_mouse % 2 == 0:
                if event.type == pygame.MOUSEMOTION and self.life1 > 0:
                    (x,y) = pygame.mouse.get_pos()
                    self.hero1.rect.centerx = x
                    self.hero1.rect.centery = y
        
        return False

    def __check_collide(self):
        '''碰撞检测'''
        # 子弹碰撞敌人
        if pygame.sprite.groupcollide(self.hero1.bullets, self.enemy_group, True, True):
            self.score1 += 1
        if pygame.sprite.groupcollide(self.hero2.bullets, self.enemy_group, True, True):
            self.score2 += 1
            self.ai_kills += 1

        # 敌人碰撞英雄1 (玩家)
        enemys1 = pygame.sprite.spritecollide(
            self.hero1, self.enemy_group, True)
        if len(enemys1) > 0 and self.life1 > 0:
            self.life1 -= 1
            if self.life1 == 0:
                # 英雄死亡后，移除屏幕
                self.hero1.rect.bottom = 0
                self.hero1.rect.x = self.screen_width
                self.hero1.kill()

        # 敌人碰撞英雄2 (AI)
        enemys2 = pygame.sprite.spritecollide(
            self.hero2, self.enemy_group, True)
        if len(enemys2) > 0 and self.life2 > 0:
            self.life2 -= 1
            self.ai_deaths += 1
            if self.life2 == 0:
                self.hero2.rect.bottom = 0
                self.hero2.rect.x = self.screen_width
                self.hero2.kill()

        # 当两个玩家都死亡，游戏结束
        if self.life1 == 0 and self.life2 == 0:
            return True
        
        return False

    def __update_sprites(self):
        '''更新精灵组'''

        if self.button.pause_game % 2 != 0:
            for group in [self.back_group, self.hero_group1, self.hero_group2, self.hero1.bullets, self.hero2.bullets, self.enemy_group, self.enemy.bullets,]: 
                group.draw(self.screen)
                self.button.update()
                # 重新设置按钮位置到左下角
                self.button.rect.x = 20
                self.button.rect.bottom = self.screen_height - 20
                self.screen.blit(self.button.image,(self.button.rect.x,self.button.rect.y))

        elif self.button.pause_game % 2 == 0:
            for group in [self.back_group, self.hero_group1, self.hero_group2, self.hero1.bullets, self.hero2.bullets, self.enemy_group, self.enemy.bullets,]:
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
        pos3 = (self.screen_width // 2, 0)
        pos4 = (self.screen_width // 2, 20)
        pos5 = (self.screen_width // 2, 40)
        pos6 = (self.screen_width // 2, 60)
        
        color = (0, 0, 0)
        text1 = f'PLAYER1 LIFE: {self.life1}'
        text2 = f'PLAYER1 SCORE: {self.score1}'
        text3 = f'AI2 LIFE: {self.life2}'
        text4 = f'AI2 SCORE: {self.score2}'
        text5 = f'AI2 KILLS: {self.ai_kills}'
        text6 = f'AI2 DEATHS: {self.ai_deaths}'
        
        try:
            cur_font = pygame.font.SysFont(None, 20)
        except:
            cur_font = pygame.font.Font(None, 20)
            
        text_fmt1 = cur_font.render(text1, 1, color)
        text_fmt2 = cur_font.render(text2, 1, color)
        text_fmt3 = cur_font.render(text3, 1, color)
        text_fmt4 = cur_font.render(text4, 1, color)
        text_fmt5 = cur_font.render(text5, 1, color)
        text_fmt6 = cur_font.render(text6, 1, color)
        
        self.screen.blit(text_fmt1, pos1)
        self.screen.blit(text_fmt2, pos2)
        self.screen.blit(text_fmt3, pos3)
        self.screen.blit(text_fmt4, pos4)
        self.screen.blit(text_fmt5, pos5)
        self.screen.blit(text_fmt6, pos6)

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

        # 英雄组 - 玩家1在左上，AI玩家2在左下
        self.hero1 = Hero('./images/life.png')
        # 设置英雄1在左上角
        self.hero1.rect.x = 50
        self.hero1.rect.y = 50
        self.hero_group1 = pygame.sprite.Group(self.hero1)
        
        self.hero2 = Hero('./images/life.png', wing=2)
        # 设置英雄2在左下角
        self.hero2.rect.x = 50
        self.hero2.rect.y = self.screen_height - 100
        # 确保AI飞机有射击能力
        self.hero2.time_count = 1
        self.hero_group2 = pygame.sprite.Group(self.hero2)
    
    def reset_game(self):
        """重置游戏状态"""
        # 重置生命和分数
        self.life1 = 3
        self.life2 = 3
        self.score1 = 0
        self.score2 = 0
        self.ai_kills = 0
        self.ai_deaths = 0
        # 重新创建精灵组
        self.__creat_sprites()
        # 确保AI飞机有射击能力
        self.hero2.time_count = 1
        # 重新创建AI控制器（只创建玩家2的AI）
        try:
            from trained_ai_controller import create_ai_controller
            self.ai_controller2 = create_ai_controller(
                self.hero2, self.enemy_group, 
                self.screen_width, self.screen_height, 
                controller_type="hybrid"
            )
        except Exception as e:
            print(f"重置时训练模型加载失败: {e}")
            self.ai_controller2 = OptimizedAIController(self.hero2, self.enemy_group, self.screen_width, self.screen_height, False)
