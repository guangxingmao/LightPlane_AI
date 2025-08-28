#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI游戏环境 - 用于训练AI决策系统
将游戏状态转换为AI可理解的观察空间
"""

import numpy as np
import pygame
import math
from typing import Dict, List, Tuple, Any, Optional
try:
    from gymnasium import Env
    from gymnasium.spaces import Box, Discrete, MultiDiscrete
except ImportError:
    from gym import Env
    from gym.spaces import Box, Discrete, MultiDiscrete

class AIGameEnvironment(Env):
    """AI游戏环境 - 用于强化学习训练"""
    
    def __init__(self, screen_width=800, screen_height=600):
        super().__init__()
        
        # 游戏参数
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 动作空间：9个动作 (8个移动方向 + 1个射击)
        self.action_space = Discrete(9)
        
        # 观察空间：游戏状态的向量表示
        # [玩家位置(2), 玩家状态(3), 敌人信息(10), 子弹信息(6), 道具信息(4), 游戏状态(3)]
        self.observation_space = Box(
            low=-1.0, 
            high=1.0, 
            shape=(28,), 
            dtype=np.float32
        )
        
        # 游戏状态
        self.player = None
        self.enemies = []
        self.bullets = []
        self.power_ups = []
        self.score = 0
        self.life = 3
        self.game_over = False
        
        # 奖励系统
        self.reward_weights = {
            'survival': 0.1,      # 生存奖励
            'kill_enemy': 10.0,   # 击杀敌人奖励
            'collect_power_up': 5.0,  # 收集道具奖励
            'damage_taken': -5.0,  # 受伤惩罚
            'miss_shot': -0.1,     # 射击失误惩罚
            'efficiency': 0.5      # 效率奖励
        }
        
        # 性能统计
        self.stats = {
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'damage_taken': 0,
            'shots_fired': 0,
            'shots_hit': 0,
            'survival_time': 0
        }
        
        # 时间控制
        self.step_count = 0
        self.max_steps = 10000  # 最大步数
        
    def reset(self, seed=None):
        """重置环境"""
        super().reset(seed=seed)
        
        # 重置游戏状态
        self.score = 0
        self.life = 3
        self.game_over = False
        self.step_count = 0
        
        # 重置性能统计
        for key in self.stats:
            self.stats[key] = 0
        
        # 重置游戏对象
        self._reset_game_objects()
        
        # 返回初始观察
        return self._get_observation(), {}
    
    def step(self, action):
        """执行一步动作"""
        self.step_count += 1
        
        # 执行动作
        reward = self._execute_action(action)
        
        # 更新游戏状态
        self._update_game_state()
        
        # 检查游戏是否结束
        done = self._is_done()
        
        # 获取观察
        observation = self._get_observation()
        
        # 额外信息
        info = {
            'score': self.score,
            'life': self.life,
            'enemies_killed': self.stats['enemies_killed'],
            'power_ups_collected': self.stats['power_ups_collected'],
            'damage_taken': self.stats['damage_taken'],
            'accuracy': self.stats['shots_hit'] / max(1, self.stats['shots_fired'])
        }
        
        return observation, reward, done, False, info
    
    def _execute_action(self, action: int) -> float:
        """执行动作并计算奖励"""
        reward = 0.0
        
        if action < 8:  # 移动动作
            reward += self._execute_movement(action)
        elif action == 8:  # 射击动作
            reward += self._execute_shooting()
        
        return reward
    
    def _execute_movement(self, direction: int) -> float:
        """执行移动动作"""
        if not self.player:
            return 0.0
        
        # 8个方向的移动向量
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
        
        dx, dy = directions[direction]
        move_speed = 3
        
        # 计算新位置
        new_x = self.player['x'] + dx * move_speed
        new_y = self.player['y'] + dy * move_speed
        
        # 边界检查
        new_x = max(25, min(self.screen_width - 25, new_x))
        new_y = max(25, min(self.screen_height - 25, new_y))
        
        # 更新位置
        self.player['x'] = new_x
        self.player['y'] = new_y
        
        # 移动奖励（鼓励探索）
        return 0.01
    
    def _execute_shooting(self) -> float:
        """执行射击动作"""
        if not self.player:
            return 0.0
        
        self.stats['shots_fired'] += 1
        
        # 检查是否有敌人在射击范围内
        hit_enemy = False
        for enemy in self.enemies:
            distance = math.sqrt(
                (enemy['x'] - self.player['x'])**2 + 
                (enemy['y'] - self.player['y'])**2
            )
            if distance < 100:  # 射击范围
                # 计算命中概率（基于距离和敌人大小）
                hit_chance = max(0.1, 1.0 - distance / 100)
                if np.random.random() < hit_chance:
                    hit_enemy = True
                    self.stats['shots_hit'] += 1
                    break
        
        if hit_enemy:
            return 2.0  # 命中奖励
        else:
            return -0.1  # 射击失误惩罚
    
    def _update_game_state(self):
        """更新游戏状态"""
        # 更新生存时间
        self.stats['survival_time'] += 1
        
        # 更新敌人位置
        self._update_enemies()
        
        # 更新子弹位置
        self._update_bullets()
        
        # 更新道具位置
        self._update_power_ups()
        
        # 碰撞检测
        self._check_collisions()
        
        # 生成新的敌人和道具
        self._spawn_entities()
    
    def _update_enemies(self):
        """更新敌人状态"""
        for enemy in self.enemies:
            # 简单的敌人AI：向玩家移动
            if self.player:
                dx = self.player['x'] - enemy['x']
                dy = self.player['y'] - enemy['y']
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0:
                    # 标准化移动向量
                    dx = (dx / distance) * enemy['speed']
                    dy = (dy / distance) * enemy['speed']
                    
                    enemy['x'] += dx
                    enemy['y'] += dy
    
    def _update_bullets(self):
        """更新子弹状态"""
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            # 移除超出屏幕的子弹
            if (bullet['x'] < 0 or bullet['x'] > self.screen_width or
                bullet['y'] < 0 or bullet['y'] > self.screen_height):
                self.bullets.remove(bullet)
    
    def _update_power_ups(self):
        """更新道具状态"""
        for power_up in self.power_ups[:]:
            power_up['y'] += power_up['speed']
            
            # 移除超出屏幕的道具
            if power_up['y'] > self.screen_height:
                self.power_ups.remove(power_up)
    
    def _check_collisions(self):
        """检查碰撞"""
        if not self.player:
            return
        
        # 检查与敌人的碰撞
        for enemy in self.enemies[:]:
            distance = math.sqrt(
                (enemy['x'] - self.player['x'])**2 + 
                (enemy['y'] - self.player['y'])**2
            )
            if distance < 25:  # 碰撞半径
                self.life -= 1
                self.stats['damage_taken'] += 1
                self.enemies.remove(enemy)
                
                if self.life <= 0:
                    self.game_over = True
        
        # 检查与道具的碰撞
        for power_up in self.power_ups[:]:
            distance = math.sqrt(
                (power_up['x'] - self.player['x'])**2 + 
                (power_up['y'] - self.player['y'])**2
            )
            if distance < 20:  # 收集半径
                self.stats['power_ups_collected'] += 1
                self.power_ups.remove(power_up)
    
    def _spawn_entities(self):
        """生成新的敌人和道具"""
        # 生成敌人
        if len(self.enemies) < 5 and np.random.random() < 0.02:
            enemy = {
                'x': np.random.randint(50, self.screen_width - 50),
                'y': -50,
                'speed': np.random.uniform(1, 3),
                'health': 1
            }
            self.enemies.append(enemy)
        
        # 生成道具
        if len(self.power_ups) < 3 and np.random.random() < 0.01:
            power_up = {
                'x': np.random.randint(50, self.screen_width - 50),
                'y': -30,
                'speed': 2,
                'type': np.random.choice(['health', 'shield', 'speed', 'firepower'])
            }
            self.power_ups.append(power_up)
    
    def _get_observation(self) -> np.ndarray:
        """获取当前游戏状态的观察向量"""
        obs = np.zeros(28, dtype=np.float32)
        
        # 玩家信息 [0-4]
        if self.player:
            obs[0] = (self.player['x'] / self.screen_width) * 2 - 1  # 归一化到[-1, 1]
            obs[1] = (self.player['y'] / self.screen_height) * 2 - 1
            obs[2] = self.life / 3.0  # 生命值比例
            obs[3] = self.score / 1000.0  # 分数比例
            obs[4] = 1.0 if self.game_over else 0.0  # 游戏结束标志
        
        # 敌人信息 [5-14] (最多2个敌人，每个5个特征)
        for i, enemy in enumerate(self.enemies[:2]):
            offset = 5 + i * 5
            obs[offset] = (enemy['x'] / self.screen_width) * 2 - 1
            obs[offset + 1] = (enemy['y'] / self.screen_height) * 2 - 1
            obs[offset + 2] = enemy['speed'] / 3.0  # 速度归一化
            obs[offset + 3] = enemy['health'] / 3.0  # 生命值归一化
            obs[offset + 4] = 1.0  # 存在标志
        
        # 子弹信息 [15-20] (最多2个子弹，每个3个特征)
        for i, bullet in enumerate(self.bullets[:2]):
            offset = 15 + i * 3
            obs[offset] = (bullet['x'] / self.screen_width) * 2 - 1
            obs[offset + 1] = (bullet['y'] / self.screen_height) * 2 - 1
            obs[offset + 2] = 1.0  # 存在标志
        
        # 道具信息 [21-24] (最多1个道具，4个特征)
        if self.power_ups:
            power_up = self.power_ups[0]
            obs[21] = (power_up['x'] / self.screen_width) * 2 - 1
            obs[22] = (power_up['y'] / self.screen_height) * 2 - 1
            obs[23] = 1.0  # 存在标志
            obs[24] = hash(power_up['type']) % 4 / 3.0  # 类型编码
        
        # 游戏状态 [25-27]
        obs[25] = self.step_count / self.max_steps  # 步数比例
        obs[26] = len(self.enemies) / 5.0  # 敌人数量比例
        obs[27] = len(self.power_ups) / 3.0  # 道具数量比例
        
        return obs
    
    def _is_done(self) -> bool:
        """检查游戏是否结束"""
        return (self.game_over or 
                self.life <= 0 or 
                self.step_count >= self.max_steps)
    
    def _reset_game_objects(self):
        """重置游戏对象"""
        # 重置玩家
        self.player = {
            'x': self.screen_width // 2,
            'y': self.screen_height - 100,
            'speed': 3
        }
        
        # 清空敌人、子弹、道具
        self.enemies = []
        self.bullets = []
        self.power_ups = []
    
    def render(self, mode='human'):
        """渲染游戏画面（用于调试）"""
        if mode == 'human':
            # 这里可以添加pygame渲染代码
            pass
    
    def close(self):
        """关闭环境"""
        pass
