"""
优化的AI控制器
减少卡顿，提高流畅度，减少抖动
"""

import pygame
import random
import math


class OptimizedAIController:
    """优化的AI控制器 - 减少卡顿，提高流畅度"""
    
    def __init__(self, hero, enemy_group, screen_width, screen_height, is_player1=True):
        self.hero = hero
        self.enemy_group = enemy_group
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_player1 = is_player1
        
        # 优化参数 - 减少抖动
        self.decision_timer = 0
        self.decision_interval = 60  # 每60帧做一次决策，减少抖动
        self.movement_pattern = 'patrol'
        self.last_move_time = 0
        self.move_duration = 120  # 每次移动持续120帧，让移动更稳定
        
        # 移动目标
        self.target_x = 0
        self.target_y = 0
        self.moving = False
        
        # 添加移动平滑参数
        self.last_position = None
        self.position_change_threshold = 15  # 位置变化阈值，避免微小抖动
        self.stable_time = 0  # 稳定时间计数器
        
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
        """AI决策逻辑 - 优化减少抖动"""
        # 寻找最近的敌人
        nearest_enemy = self.find_nearest_enemy()
        
        if nearest_enemy:
            # 计算与敌人的距离
            distance = self.calculate_distance(self.hero.rect.center, nearest_enemy.rect.center)
            
            # 根据距离决定行为，增加稳定性判断
            if distance < 80:  # 敌人太近时躲避
                if self.movement_pattern != 'evade' or self.stable_time > 30:
                    self.movement_pattern = 'evade'
                    self.set_evade_target(nearest_enemy)
                    self.stable_time = 0
            elif distance < 150:  # 中等距离时追击
                if self.movement_pattern != 'chase' or self.stable_time > 40:
                    self.movement_pattern = 'chase'
                    self.set_chase_target(nearest_enemy)
                    self.stable_time = 0
            else:  # 远距离时巡逻
                if self.movement_pattern != 'patrol' or self.stable_time > 50:
                    self.movement_pattern = 'patrol'
                    self.set_patrol_target()
                    self.stable_time = 0
            
            # 自动射击
            self.auto_shoot(nearest_enemy)
        else:
            # 没有敌人时巡逻，增加稳定性
            if self.movement_pattern != 'patrol' or self.stable_time > 60:
                self.set_patrol_target()
                self.stable_time = 0
        
        # 增加稳定时间
        self.stable_time += 1
    
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
        """设置巡逻目标 - 优化减少抖动"""
        patrol_radius = 80
        
        # 降低巡逻目标变化频率，减少抖动
        if random.random() < 0.1:  # 从30%降低到10%概率改变巡逻目标
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, patrol_radius)
            
            new_target_x = self.patrol_center_x + math.cos(angle) * distance
            new_target_y = self.patrol_center_y + math.sin(angle) * distance
            
            # 检查新目标是否与当前位置差异足够大，避免微小移动
            current_pos = (self.hero.rect.centerx, self.hero.rect.centery)
            new_pos = (new_target_x, new_target_y)
            distance_to_new_target = self.calculate_distance(current_pos, new_pos)
            
            if distance_to_new_target > self.position_change_threshold:
                self.target_x = new_target_x
                self.target_y = new_target_y
                
                # 边界检查
                if self.is_player1:
                    self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
                else:
                    # AI飞机现在在左下角，限制在左侧区域
                    self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
                
                self.target_y = max(50, min(self.screen_height - 50, self.target_y))
                self.moving = True
    
    def execute_movement(self):
        """执行移动 - 优化减少抖动"""
        if not self.moving:
            return
        
        # 计算到目标的距离
        dx = self.target_x - self.hero.rect.centerx
        dy = self.target_y - self.hero.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        # 如果已经接近目标，停止移动
        if distance < 8:  # 增加停止距离，减少抖动
            self.moving = False
            return
        
        # 动态调整移动速度，距离越近速度越慢
        base_speed = 2
        if distance < 20:
            move_speed = base_speed * 0.5  # 接近目标时减速
        elif distance < 50:
            move_speed = base_speed * 0.8  # 中等距离时中速
        else:
            move_speed = base_speed  # 远距离时全速
        
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
        
        # 检查位置变化是否足够大，避免微小抖动
        if self.last_position:
            current_pos = (self.hero.rect.centerx, self.hero.rect.centery)
            new_pos = (new_x, new_y)
            position_change = self.calculate_distance(current_pos, new_pos)
            
            if position_change > 1:  # 只有位置变化大于1像素时才更新
                self.hero.rect.centerx = new_x
                self.hero.rect.centery = new_y
                self.last_position = (new_x, new_y)
        else:
            # 第一次移动，直接更新
            self.hero.rect.centerx = new_x
            self.hero.rect.centery = new_y
            self.last_position = (new_x, new_y)
    
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
