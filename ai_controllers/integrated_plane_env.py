#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成飞机大战训练环境
AI战机训练环境与游戏策略AI集成，实现真正的协同训练
"""

import os
# 设置SDL为虚拟模式，避免在训练时弹出窗口
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
import math
import random
from typing import Optional, Tuple, Dict, Any

# 导入游戏模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plane_sprites import *

class IntegratedTrainingHero(pygame.sprite.Sprite):
    """集成训练专用的英雄类，支持动态策略调整"""
    
    def __init__(self, image_path):
        super().__init__()
        
        # 加载图片
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        
        # 创建子弹组
        self.bullets = pygame.sprite.Group()
        
        # 射击计时器（支持动态调整）
        self.time_count = 1
        self.fire_cooldown = 0
        self.fire_rate_multiplier = 1.0  # 射击频率倍数
        
        # 移动参数（支持动态调整）
        self.speed_multiplier = 1.0  # 移动速度倍数
        self.base_speed = 3
        
        # 添加存活状态
        self._alive = True
        
        # 性能统计
        self.enemies_killed = 0
        self.power_ups_collected = 0
        self.damage_taken = 0
        self.survival_time = 0
    
    def update(self, strategy_params=None):
        """更新英雄状态，支持策略参数调整"""
        if strategy_params:
            # 根据策略调整参数
            if 'fire_rate' in strategy_params:
                self.fire_rate_multiplier = strategy_params['fire_rate']
            if 'speed' in strategy_params:
                self.speed_multiplier = strategy_params['speed']
        
        # 更新子弹
        self.bullets.update()
        
        # 清理超出屏幕的子弹
        for bullet in self.bullets:
            if bullet.rect.bottom < 0:
                bullet.kill()
        
        # 更新射击冷却（考虑策略调整）
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        else:
            self.time_count = 1
        
        # 更新生存时间
        self.survival_time += 1
    
    def alive(self):
        """检查英雄是否存活"""
        return self._alive
    
    def fire(self):
        """发射子弹（支持动态射击频率）"""
        if self.time_count > 0 and self.fire_cooldown <= 0:
            bullet = Bullet_Hero()
            bullet.rect.centerx = self.rect.centerx
            bullet.rect.bottom = self.rect.top
            self.bullets.add(bullet)
            
            # 根据策略调整射击冷却
            base_cooldown = 10
            adjusted_cooldown = int(base_cooldown / self.fire_rate_multiplier)
            self.fire_cooldown = max(1, adjusted_cooldown)
            self.time_count = 0
    
    def move(self, dx, dy):
        """移动英雄（支持动态速度）"""
        adjusted_speed = self.base_speed * self.speed_multiplier
        self.rect.x += int(dx * adjusted_speed)
        self.rect.y += int(dy * adjusted_speed)
        
        # 边界检查
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())
    
    def _find_nearest_enemy(self, enemy_group):
        """找到最近的敌人"""
        if not enemy_group:
            return None
        
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemy_group:
            distance = self._calculate_distance(
                self.rect.center, enemy.rect.center
            )
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        
        return nearest_enemy
    
    def _calculate_distance(self, pos1, pos2):
        """计算两点间距离"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

class IntegratedPlaneFighterEnv(gym.Env):
    """
    集成飞机大战训练环境
    AI战机训练环境与游戏策略AI集成
    
    观察空间: 游戏状态向量 + 策略参数
    动作空间: 离散动作 (8个方向移动 + 射击)
    奖励函数: 基于击杀敌人、存活时间、策略适应等
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(self, screen_width=1280, screen_height=720, render_mode=None):
        super().__init__()
        
        # 环境参数
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.render_mode = render_mode
        self.max_steps = 5000  # 最大步数
        
        # 游戏状态
        self.step_count = 0
        self.score = 0
        self.lives = 3
        self.is_terminated = False
        self.is_truncated = False
        
        # 策略参数（由游戏策略AI控制）
        self.strategy_params = {
            'difficulty': 0.5,           # 游戏难度 [0.0, 1.0]
            'enemy_spawn_rate': 0.02,    # 敌机生成率 [0.0, 0.1]
            'enemy_bullet_frequency': 0.01,  # 敌机射击频率 [0.0, 0.05]
            'power_up_drop_rate': 0.005,     # 道具掉落率 [0.0, 0.02]
            'background_intensity': 0.5,     # 背景强度 [0.0, 1.0]
            'special_event_chance': 0.1      # 特殊事件概率 [0.0, 0.3]
        }
        
        # 动态调整参数
        self.dynamic_adjustment = True
        self.adjustment_interval = 100  # 每100步调整一次策略
        self.last_adjustment = 0
        
        # Pygame初始化
        pygame.init()
        
        if self.render_mode is not None:
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            self.clock = pygame.time.Clock()
        else:
            # 训练时使用虚拟屏幕
            pygame.display.set_mode((1, 1))
            self.screen = pygame.Surface((screen_width, screen_height))
            self.clock = None
            
        # 动作空间：9个离散动作
        # 0-7: 8个方向移动, 8: 射击
        self.action_space = spaces.Discrete(9)
        
        # 观察空间：状态向量 + 策略参数
        # [hero_x, hero_y, hero_vx, hero_vy, 
        #  enemy1_x, enemy1_y, enemy1_vx, enemy1_vy, enemy1_exists,
        #  enemy2_x, enemy2_y, enemy2_vx, enemy2_vy, enemy2_exists,
        #  bullet1_x, bullet1_y, bullet1_exists,
        #  bullet2_x, bullet2_y, bullet2_exists,
        #  score, lives, step_count_normalized,
        #  difficulty, enemy_spawn_rate, enemy_bullet_frequency, power_up_drop_rate]
        obs_dim = 30  # 28 + 2个新的生存技能参数
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(obs_dim,), dtype=np.float32
        )
        
        # 游戏精灵初始化
        self.hero = None
        self.enemy_group = None
        self.bullets = None
        self.enemy_bullets = None
        self.power_ups = None
        
        # 性能统计
        self.performance_metrics = {
            'survival_time': 0,
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'damage_taken': 0,
            'accuracy_rate': 0.0,
            'efficiency_score': 0.0
        }
        
        # 重置环境
        self.reset()
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """重置环境到初始状态"""
        super().reset(seed=seed)
        
        # 重置游戏状态
        self.step_count = 0
        self.score = 0
        self.lives = 3
        self.is_terminated = False
        self.is_truncated = False
        
        # 重置策略参数到默认值
        self.strategy_params = {
            'difficulty': 0.5,
            'enemy_spawn_rate': 0.02,
            'enemy_bullet_frequency': 0.01,
            'power_up_drop_rate': 0.005,
            'background_intensity': 0.5,
            'special_event_chance': 0.1
        }
        
        # 重置性能统计
        self.performance_metrics = {
            'survival_time': 0,
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'damage_taken': 0,
            'accuracy_rate': 0.0,
            'efficiency_score': 0.0
        }
        
        # 初始化移动和探索相关变量
        self.last_position = (self.screen_width // 2, self.screen_height - 50)  # 初始位置
        self.safe_zone_time = 0
        self.explored_positions = set()
        self.consecutive_dodges = 0  # 初始化连续躲避计数
        
        # 创建游戏对象
        self._create_sprites()
        
        # 返回初始观察和信息
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """执行一步动作"""
        if self.is_terminated or self.is_truncated:
            return self._get_observation(), 0.0, self.is_terminated, self.is_truncated, self._get_info()
        
        # 执行动作
        reward = self._execute_action(action)
        
        # 更新游戏状态
        self._update_game()
        
        # 动态调整策略参数
        if self.dynamic_adjustment:
            self._adjust_strategy_params()
        
        # 计算奖励
        reward += self._calculate_reward()
        
        # 更新步数
        self.step_count += 1
        
        # 检查终止条件
        self._check_termination()
        
        # 获取观察和信息
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, reward, self.is_terminated, self.is_truncated, info
    
    def _create_sprites(self):
        """创建游戏精灵"""
        # 创建英雄
        self.hero = IntegratedTrainingHero("../images/hero1.png")
        self.hero.rect.centerx = self.screen_width // 2
        self.hero.rect.bottom = self.screen_height - 50
        
        # 创建敌机组
        self.enemy_group = []
        
        # 创建子弹组
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        # 创建道具组
        self.power_ups = pygame.sprite.Group()
    
    def _execute_action(self, action: int) -> float:
        """执行动作并返回基础奖励"""
        reward = 0.0
        
        if action == 8:  # 射击
            self.hero.fire()
            reward += 0.1  # 射击奖励
        else:  # 移动
            dx, dy = self._action_to_direction(action)
            self.hero.move(dx, dy)
            
            # 移动奖励（鼓励探索）
            if self.last_position:
                distance_moved = math.sqrt(
                    (self.hero.rect.centerx - self.last_position[0])**2 +
                    (self.hero.rect.centery - self.last_position[1])**2
                )
                if distance_moved > 0:
                    reward += 0.05
            
            self.last_position = (self.hero.rect.centerx, self.hero.rect.centery)
        
        return reward
    
    def _action_to_direction(self, action: int) -> Tuple[int, int]:
        """将动作转换为方向向量"""
        directions = [
            (0, -1),   # 0: 上
            (1, -1),   # 1: 右上
            (1, 0),    # 2: 右
            (1, 1),    # 3: 右下
            (0, 1),    # 4: 下
            (-1, 1),   # 5: 左下
            (-1, 0),   # 6: 左
            (-1, -1),  # 7: 左上
        ]
        
        if 0 <= action < 8:
            return directions[action]
        return (0, 0)
    
    def _update_game(self):
        """更新游戏状态"""
        # 更新英雄
        self.hero.update(self.strategy_params)
        
        # 更新敌机
        self._update_enemies()
        
        # 更新子弹
        self._update_bullets()
        
        # 更新道具
        self._update_power_ups()
        
        # 碰撞检测
        self._check_collisions()
        
        # 生成新的敌机
        self._spawn_enemies()
        
        # 生成道具
        self._spawn_power_ups()
        
        # 更新性能统计
        self._update_performance_metrics()
    
    def _update_enemies(self):
        """更新敌机状态"""
        for enemy in self.enemy_group[:]:
            enemy.rect.y += enemy.speed
            
            # 移除超出屏幕的敌机
            if enemy.rect.top > self.screen_height:
                self.enemy_group.remove(enemy)
            
            # 敌机射击（根据策略频率）
            if random.random() < self.strategy_params['enemy_bullet_frequency']:
                self._enemy_shoot(enemy)
    
    def _enemy_shoot(self, enemy):
        """敌机射击"""
        bullet = Bullet_Enemy()
        bullet.rect.centerx = enemy.rect.centerx
        bullet.rect.top = enemy.rect.bottom
        self.enemy_bullets.add(bullet)
    
    def _update_bullets(self):
        """更新子弹状态"""
        # 更新英雄子弹
        for bullet in self.bullets:
            bullet.rect.y -= bullet.speed
            if bullet.rect.bottom < 0:
                bullet.kill()
        
        # 更新敌机子弹
        for bullet in self.enemy_bullets:
            bullet.rect.y += bullet.speed
            if bullet.rect.top > self.screen_height:
                bullet.kill()
    
    def _update_power_ups(self):
        """更新道具状态"""
        for power_up in self.power_ups:
            power_up.rect.y += power_up.speed
            if power_up.rect.top > self.screen_height:
                power_up.kill()
    
    def _check_collisions(self):
        """碰撞检测"""
        # 英雄子弹击中敌机
        for bullet in self.bullets:
            for enemy in self.enemy_group[:]:
                if pygame.sprite.collide_rect(bullet, enemy):
                    bullet.kill()
                    self.enemy_group.remove(enemy)
                    self.score += 100
                    self.performance_metrics['enemies_killed'] += 1
                    break
        
        # 敌机子弹击中英雄
        for bullet in self.enemy_bullets:
            if pygame.sprite.collide_rect(bullet, self.hero):
                bullet.kill()
                self.lives -= 1
                self.performance_metrics['damage_taken'] += 1
                if self.lives <= 0:
                    self.hero._alive = False
        
        # 英雄收集道具
        for power_up in list(self.power_ups):
            if pygame.sprite.collide_rect(self.hero, power_up):
                self.power_ups.remove(power_up)
                self.performance_metrics['power_ups_collected'] += 1
                self.score += 50
        
        # 敌机撞击英雄
        for enemy in self.enemy_group[:]:
            if pygame.sprite.collide_rect(self.hero, enemy):
                self.enemy_group.remove(enemy)
                self.lives -= 1
                self.performance_metrics['damage_taken'] += 1
                if self.lives <= 0:
                    self.hero._alive = False
    
    def _spawn_enemies(self):
        """生成敌机（根据策略参数）"""
        if random.random() < self.strategy_params['enemy_spawn_rate']:
            enemy = Enemy()
            enemy.rect.x = random.randint(0, self.screen_width - enemy.rect.width)
            enemy.rect.y = -enemy.rect.height
            self.enemy_group.append(enemy)
    
    def _spawn_power_ups(self):
        """生成道具（根据策略参数）"""
        if random.random() < self.strategy_params['power_up_drop_rate']:
            power_up = Bullet_Hero()  # 使用英雄子弹作为道具
            power_up.rect.x = random.randint(0, self.screen_width - power_up.rect.width)
            power_up.rect.y = -power_up.rect.height
            self.power_ups.add(power_up)
    
    def _adjust_strategy_params(self):
        """动态调整策略参数（模拟游戏策略AI的行为）"""
        if self.step_count - self.last_adjustment >= self.adjustment_interval:
            self.last_adjustment = self.step_count
            
            # 基于性能调整难度
            if self.performance_metrics['efficiency_score'] > 0.7:
                # 表现好，增加难度
                self.strategy_params['difficulty'] = min(1.0, self.strategy_params['difficulty'] + 0.05)
                self.strategy_params['enemy_spawn_rate'] = min(0.1, self.strategy_params['enemy_spawn_rate'] + 0.001)
                self.strategy_params['enemy_bullet_frequency'] = min(0.05, self.strategy_params['enemy_bullet_frequency'] + 0.0005)
            elif self.performance_metrics['efficiency_score'] < 0.3:
                # 表现差，降低难度
                self.strategy_params['difficulty'] = max(0.0, self.strategy_params['difficulty'] - 0.05)
                self.strategy_params['enemy_spawn_rate'] = max(0.0, self.strategy_params['enemy_spawn_rate'] - 0.001)
                self.strategy_params['enemy_bullet_frequency'] = max(0.0, self.strategy_params['enemy_bullet_frequency'] - 0.0005)
    
    def _update_performance_metrics(self):
        """更新性能指标"""
        self.performance_metrics['survival_time'] = self.step_count
        
        # 计算效率分数
        total_actions = self.step_count
        if total_actions > 0:
            kill_efficiency = self.performance_metrics['enemies_killed'] / total_actions
            collection_efficiency = self.performance_metrics['power_ups_collected'] / total_actions
            damage_penalty = self.performance_metrics['damage_taken'] / total_actions
            
            self.performance_metrics['efficiency_score'] = (
                kill_efficiency * 0.6 + 
                collection_efficiency * 0.3 - 
                damage_penalty * 0.1
            )
            self.performance_metrics['efficiency_score'] = max(0.0, min(1.0, self.performance_metrics['efficiency_score']))
    
    def _calculate_reward(self) -> float:
        """计算奖励 - 强化生存技能"""
        reward = 0.0
        
        # 🛡️ 生存奖励 - 大幅提升
        reward += 1.0  # 从0.1提升到1.0
        
        # 🎯 击杀奖励 - 适度奖励
        reward += self.performance_metrics['enemies_killed'] * 5  # 从10降到5
        
        # 💊 道具收集奖励 - 适度奖励
        reward += self.performance_metrics['power_ups_collected'] * 3  # 从5降到3
        
        # ⚠️ 伤害惩罚 - 大幅惩罚
        reward -= self.performance_metrics['damage_taken'] * 50  # 从20提升到50
        
        # 🧠 效率奖励 - 基于生存时间
        survival_bonus = min(self.step_count / 1000.0, 1.0)  # 生存时间越长奖励越高
        reward += survival_bonus * 10
        
        # 🎮 策略适应奖励
        strategy_adaptation = 1.0 - abs(self.strategy_params['difficulty'] - 0.5) * 2
        reward += strategy_adaptation * 3
        
        # 🚀 连续生存奖励 - 大幅提升
        if self.step_count > 100 and self.lives == 3:
            reward += 20.0  # 从5.0提升到20.0，大幅奖励满血生存
        
        # 🛡️ 长期生存奖励
        if self.step_count > 500:
            reward += 10.0  # 长期生存额外奖励
        
        # 🎯 生命值保护奖励
        if self.lives >= 2:
            reward += (self.lives - 1) * 15.0  # 每多一条命额外奖励
        
        # 🎯 躲避技能奖励 - 大幅提升
        if self._check_bullet_dodging():
            reward += 10.0  # 从2.0提升到10.0，大幅奖励躲避
        
        # 🚀 连续躲避奖励
        if hasattr(self, 'consecutive_dodges'):
            if self.consecutive_dodges > 0:
                reward += self.consecutive_dodges * 5.0  # 连续躲避额外奖励
        else:
            self.consecutive_dodges = 0
        
        # 🎯 预判躲避奖励
        if self._check_predictive_dodging():
            reward += 15.0  # 预判性躲避奖励
        
        # 🛡️ 安全区域奖励
        if self._check_safe_position():
            reward += 3.0  # 在安全位置奖励
        
        # 🎮 灵活移动奖励
        if self._check_flexible_movement():
            reward += 5.0  # 灵活移动奖励
        
        return reward
    
    def _check_termination(self):
        """检查终止条件"""
        # 生命值耗尽
        if self.lives <= 0 or not self.hero._alive:
            self.is_terminated = True
        
        # 达到最大步数
        if self.step_count >= self.max_steps:
            self.is_truncated = True
    
    def _get_observation(self) -> np.ndarray:
        """获取观察向量"""
        obs = np.zeros(30, dtype=np.float32)
        
        # 英雄信息 [0-3]
        if self.hero:
            obs[0] = self.hero.rect.centerx / self.screen_width * 2 - 1  # 归一化到[-1, 1]
            obs[1] = self.hero.rect.centery / self.screen_height * 2 - 1
            obs[2] = 0.0  # 速度x（简化）
            obs[3] = 0.0  # 速度y（简化）
        
        # 敌机信息 [4-11]
        for i, enemy in enumerate(self.enemy_group[:2]):  # 最多2个敌机
            idx = 4 + i * 4
            obs[idx] = enemy.rect.centerx / self.screen_width * 2 - 1
            obs[idx + 1] = enemy.rect.centery / self.screen_height * 2 - 1
            obs[idx + 2] = enemy.speed / 10.0  # 归一化速度
            obs[idx + 3] = 1.0  # 存在标志
        # 填充不存在的敌机
        for i in range(len(self.enemy_group), 2):
            idx = 4 + i * 4
            obs[idx:idx + 4] = 0.0
        
        # 子弹信息 [12-19]
        for i, bullet in enumerate(list(self.enemy_bullets)[:2]):  # 最多2个子弹
            idx = 12 + i * 4
            obs[idx] = bullet.rect.centerx / self.screen_width * 2 - 1
            obs[idx + 1] = bullet.rect.centery / self.screen_height * 2 - 1
            obs[idx + 2] = bullet.speed / 10.0
            obs[idx + 3] = 1.0
        # 填充不存在的子弹
        for i in range(len(list(self.enemy_bullets)), 2):
            idx = 12 + i * 4
            obs[idx:idx + 4] = 0.0
        
        # 游戏状态 [20-21]
        obs[20] = self.score / 10000.0  # 分数归一化
        obs[21] = self.lives / 3.0      # 生命值比例
        
        # 🛡️ 生存状态 [22-25] - 大幅扩展
        obs[22] = self.step_count / 2000.0  # 生存时间比例
        obs[23] = 1.0 if self.lives == 3 else 0.5 if self.lives == 2 else 0.0  # 生命值状态
        obs[24] = min(self.consecutive_dodges / 10.0, 1.0) if hasattr(self, 'consecutive_dodges') else 0.0  # 连续躲避次数
        obs[25] = 1.0 if self._check_safe_position() else 0.0  # 是否在安全位置
        
        # 🎯 策略参数 [26-27] - 调整索引
        obs[26] = self.strategy_params['difficulty']
        obs[27] = self.strategy_params['enemy_spawn_rate'] * 10
        
        # 策略参数 [22-25]
        obs[22] = self.strategy_params['difficulty']
        obs[23] = self.strategy_params['enemy_spawn_rate'] * 10
        obs[24] = self.strategy_params['enemy_bullet_frequency'] * 20
        obs[25] = self.strategy_params['power_up_drop_rate'] * 50
        
        return obs
    
    def _check_bullet_dodging(self) -> bool:
        """检查是否成功躲避子弹"""
        if not self.hero or len(self.enemy_bullets) == 0:
            return False
        
        # 检查是否有子弹接近英雄但未击中
        for bullet in self.enemy_bullets:
            distance = ((bullet.rect.centerx - self.hero.rect.centerx) ** 2 + 
                       (bullet.rect.centery - self.hero.rect.centery) ** 2) ** 0.5
            
            # 如果子弹在危险距离内但未击中，认为是成功躲避
            if distance < 50 and bullet.rect.centery > self.hero.rect.centery - 20:
                # 更新连续躲避计数
                if not hasattr(self, 'consecutive_dodges'):
                    self.consecutive_dodges = 0
                self.consecutive_dodges += 1
                return True
        
        # 如果没有躲避，重置连续计数
        if hasattr(self, 'consecutive_dodges'):
            self.consecutive_dodges = 0
        return False
    
    def _check_predictive_dodging(self) -> bool:
        """检查是否进行预判性躲避 - 增强版"""
        if not self.hero or len(self.enemy_bullets) == 0:
            return False
        
        # 检查是否在子弹到达前就移动到安全位置
        for bullet in self.enemy_bullets:
            # 计算子弹到达英雄位置的时间
            time_to_reach = (bullet.rect.centery - self.hero.rect.centery) / bullet.speed
            
            # 如果子弹即将到达（时间小于阈值）
            if 0 < time_to_reach < 30:  # 30帧内到达
                # 检查英雄是否已经移动到安全位置
                safe_x = self.screen_width // 2  # 屏幕中央相对安全
                safe_y = self.screen_height // 2  # 屏幕中央相对安全
                
                # 检查是否在安全区域内
                if (abs(self.hero.rect.centerx - safe_x) < 150 and 
                    abs(self.hero.rect.centery - safe_y) < 100):
                    return True
        
        return False
    
    def _check_safe_position(self) -> bool:
        """检查是否在安全位置"""
        if not self.hero:
            return False
        
        # 检查是否在屏幕中央区域（相对安全）
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # 安全区域：屏幕中央附近
        safe_zone_x = abs(self.hero.rect.centerx - center_x) < 200
        safe_zone_y = abs(self.hero.rect.centery - center_y) < 150
        
        return safe_zone_x and safe_zone_y
    
    def _check_flexible_movement(self) -> bool:
        """检查是否进行灵活移动 - 增强版"""
        if not self.hero or not hasattr(self, 'last_position'):
            self.last_position = self.hero.rect.center if self.hero else (0, 0)
            return False
        
        # 检查移动距离和方向变化
        current_pos = self.hero.rect.center
        distance = ((current_pos[0] - self.last_position[0]) ** 2 + 
                   (current_pos[1] - self.last_position[1]) ** 2) ** 0.5
        
        # 如果移动距离适中（既不是静止也不是过度移动），认为是灵活移动
        if 10 < distance < 100:
            # 检查是否在躲避子弹的同时进行移动
            if len(self.enemy_bullets) > 0:
                # 计算最近的子弹距离
                min_bullet_distance = float('inf')
                for bullet in self.enemy_bullets:
                    bullet_distance = ((bullet.rect.centerx - current_pos[0]) ** 2 + 
                                     (bullet.rect.centery - current_pos[1]) ** 2) ** 0.5
                    min_bullet_distance = min(min_bullet_distance, bullet_distance)
                
                # 如果在躲避子弹的同时移动，给予额外奖励
                if min_bullet_distance < 100:
                    self.last_position = current_pos
                    return True
            
            self.last_position = current_pos
            return True
        
        self.last_position = current_pos
        return False
    
    def _get_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        return {
            'score': self.score,
            'lives': self.lives,
            'step_count': self.step_count,
            'strategy_params': self.strategy_params.copy(),
            'performance_metrics': self.performance_metrics.copy()
        }
    
    def render(self):
        """渲染环境（训练时通常不需要）"""
        if self.render_mode == "human":
            # 这里可以添加可视化代码
            pass
    
    def close(self):
        """关闭环境"""
        pygame.quit()

if __name__ == "__main__":
    # 测试环境
    env = IntegratedPlaneFighterEnv()
    obs, info = env.reset()
    
    print("✅ 集成飞机大战训练环境创建成功!")
    print(f"观察空间维度: {env.observation_space.shape}")
    print(f"动作空间: {env.action_space}")
    print(f"策略参数: {env.strategy_params}")
    
    # 测试几步
    for i in range(5):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"步骤 {i+1}: 动作={action}, 奖励={reward:.2f}, 分数={info['score']}")
    
    env.close()
