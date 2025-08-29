#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏策略AI训练环境
专门用于训练AI如何生成和管理游戏策略
包括难度调整、敌机生成、道具掉落、背景切换等
"""

import numpy as np
import pygame
import math
import random
from typing import Dict, List, Tuple, Any, Optional
try:
    from gymnasium import Env
    from gymnasium.spaces import Box, Discrete, MultiDiscrete
except ImportError:
    from gym import Env
    from gym.spaces import Box, Discrete, MultiDiscrete

class GameStrategyEnvironment(Env):
    """游戏策略AI训练环境 - 专门训练游戏策略生成"""
    
    def __init__(self, screen_width=800, screen_height=600):
        super().__init__()
        
        # 游戏参数
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 动作空间：游戏策略调整动作
        # [难度调整, 敌机生成率, 敌机射击率, 道具掉落率, 背景切换, 特殊事件]
        self.action_space = Discrete(6)
        
        # 观察空间：游戏策略状态向量
        # [游戏状态(5), 玩家表现(5), 游戏平衡(5), 策略效果(5), 环境状态(5)]
        self.observation_space = Box(
            low=-1.0, 
            high=1.0, 
            shape=(25,), 
            dtype=np.float32
        )
        
        # 游戏策略参数
        self.game_strategy = {
            'difficulty': 0.5,           # 游戏难度 [0.0, 1.0]
            'enemy_spawn_rate': 0.02,    # 敌机生成率 [0.0, 0.1]
            'enemy_bullet_frequency': 0.01,  # 敌机射击频率 [0.0, 0.05]
            'power_up_drop_rate': 0.005,     # 道具掉落率 [0.0, 0.02]
            'background_intensity': 0.5,     # 背景强度 [0.0, 1.0]
            'special_event_chance': 0.1      # 特殊事件概率 [0.0, 0.3]
        }
        
        # 游戏状态
        self.game_state = {
            'score': 0,
            'lives': 3,
            'enemies_active': 0,
            'power_ups_active': 0,
            'bullets_active': 0,
            'background_type': 0,
            'special_event_active': False,
            'survival_time': 0
        }
        
        # 玩家表现指标
        self.player_performance = {
            'survival_time': 0,
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'damage_taken': 0,
            'accuracy_rate': 0.0,
            'efficiency_score': 0.0
        }
        
        # 游戏平衡指标
        self.balance_metrics = {
            'challenge_level': 0.5,      # 挑战等级 [0.0, 1.0]
            'engagement_score': 0.5,     # 参与度评分 [0.0, 1.0]
            'fun_factor': 0.5,           # 趣味性评分 [0.0, 1.0]
            'difficulty_progression': 0.0,  # 难度递进 [0.0, 1.0]
            'variety_score': 0.5         # 多样性评分 [0.0, 1.0]
        }
        
        # 策略效果历史
        self.strategy_history = []
        self.max_history = 100
        
        # 奖励系统 - 专注于游戏策略优化
        self.reward_weights = {
            'game_balance': 10.0,        # 游戏平衡性
            'player_engagement': 8.0,    # 玩家参与度
            'difficulty_progression': 5.0,   # 难度递进
            'variety_creation': 3.0,     # 多样性创造
            'challenge_maintenance': 3.0,    # 挑战维持
            'fun_optimization': 2.0      # 趣味性优化
        }
        
        # 性能统计
        self.stats = {
            'total_reward': 0.0,
            'strategy_changes': 0,
            'balance_improvements': 0,
            'player_satisfaction': 0.0
        }
        
        # 时间控制
        self.step_count = 0
        self.max_steps = 2000  # 最大步数
        self.strategy_update_interval = 50  # 每50步更新一次策略
        
    def reset(self, seed=None):
        """重置环境"""
        super().reset(seed=seed)
        
        # 重置游戏状态
        self.game_state = {
            'score': 0,
            'lives': 3,
            'enemies_active': 0,
            'power_ups_active': 0,
            'bullets_active': 0,
            'background_type': 0,
            'special_event_active': False,
            'survival_time': 0
        }
        
        # 重置玩家表现
        self.player_performance = {
            'survival_time': 0,
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'damage_taken': 0,
            'accuracy_rate': 0.0,
            'efficiency_score': 0.0
        }
        
        # 重置游戏平衡指标
        self.balance_metrics = {
            'challenge_level': 0.5,
            'engagement_score': 0.5,
            'fun_factor': 0.5,
            'difficulty_progression': 0.0,
            'variety_score': 0.5
        }
        
        # 重置策略历史
        self.strategy_history = []
        
        # 重置统计
        for key in self.stats:
            self.stats[key] = 0.0
        
        # 重置步数
        self.step_count = 0
        
        # 返回初始观察
        return self._get_observation(), {}
    
    def step(self, action):
        """执行一步策略调整动作"""
        self.step_count += 1
        
        # 执行策略调整
        reward = self._execute_strategy_action(action)
        
        # 更新游戏状态
        self._update_game_state()
        
        # 更新游戏平衡指标
        self._update_balance_metrics()
        
        # 计算策略效果奖励
        strategy_reward = self._calculate_strategy_reward()
        total_reward = reward + strategy_reward
        
        # 检查游戏是否结束
        done = self._is_done()
        
        # 获取观察
        observation = self._get_observation()
        
        # 额外信息
        info = {
            'game_strategy': self.game_strategy.copy(),
            'balance_metrics': self.balance_metrics.copy(),
            'player_performance': self.player_performance.copy(),
            'total_reward': self.stats['total_reward']
        }
        
        return observation, total_reward, done, False, info
    
    def _execute_strategy_action(self, action: int) -> float:
        """执行策略调整动作"""
        reward = 0.0
        old_strategy = self.game_strategy.copy()
        
        if action == 0:  # 调整难度
            adjustment = random.uniform(-0.1, 0.1)
            self.game_strategy['difficulty'] = np.clip(
                self.game_strategy['difficulty'] + adjustment, 0.0, 1.0
            )
            reward += 0.1  # 小奖励鼓励调整
            
        elif action == 1:  # 调整敌机生成率
            adjustment = random.uniform(-0.005, 0.005)
            self.game_strategy['enemy_spawn_rate'] = np.clip(
                self.game_strategy['enemy_spawn_rate'] + adjustment, 0.0, 0.1
            )
            reward += 0.1
            
        elif action == 2:  # 调整敌机射击频率
            adjustment = random.uniform(-0.002, 0.002)
            self.game_strategy['enemy_bullet_frequency'] = np.clip(
                self.game_strategy['enemy_bullet_frequency'] + adjustment, 0.0, 0.05
            )
            reward += 0.1
            
        elif action == 3:  # 调整道具掉落率
            adjustment = random.uniform(-0.001, 0.001)
            self.game_strategy['power_up_drop_rate'] = np.clip(
                self.game_strategy['power_up_drop_rate'] + adjustment, 0.0, 0.02
            )
            reward += 0.1
            
        elif action == 4:  # 切换背景
            self.game_strategy['background_intensity'] = random.uniform(0.0, 1.0)
            reward += 0.2  # 背景切换奖励
            
        elif action == 5:  # 触发特殊事件
            if random.random() < self.game_strategy['special_event_chance']:
                self.game_state['special_event_active'] = True
                reward += 0.5  # 特殊事件奖励
            else:
                reward -= 0.1  # 失败惩罚
        
        # 记录策略变化
        self.strategy_history.append({
            'step': self.step_count,
            'action': action,
            'old_strategy': old_strategy,
            'new_strategy': self.game_strategy.copy(),
            'reward': reward
        })
        
        # 限制历史记录长度
        if len(self.strategy_history) > self.max_history:
            self.strategy_history.pop(0)
        
        self.stats['strategy_changes'] += 1
        return reward
    
    def _update_game_state(self):
        """更新游戏状态"""
        # 模拟游戏进行
        self.game_state['score'] += random.randint(1, 10)
        self.game_state['survival_time'] += 1
        
        # 根据策略生成敌人
        if random.random() < self.game_strategy['enemy_spawn_rate']:
            self.game_state['enemies_active'] = min(
                self.game_state['enemies_active'] + 1, 10
            )
        
        # 根据策略生成道具
        if random.random() < self.game_strategy['power_up_drop_rate']:
            self.game_state['power_ups_active'] = min(
                self.game_state['power_ups_active'] + 1, 5
            )
        
        # 根据策略生成子弹
        if random.random() < self.game_strategy['enemy_bullet_frequency']:
            self.game_state['bullets_active'] = min(
                self.game_state['bullets_active'] + 1, 20
            )
        
        # 更新玩家表现
        self.player_performance['survival_time'] = self.step_count
        
        # 模拟击杀敌人
        if random.random() < 0.1:  # 10%概率击杀敌人
            self.player_performance['enemies_killed'] += 1
            self.game_state['enemies_active'] = max(0, self.game_state['enemies_active'] - 1)
        
        # 模拟收集道具
        if random.random() < 0.05:  # 5%概率收集道具
            self.player_performance['power_ups_collected'] += 1
            self.game_state['power_ups_active'] = max(0, self.game_state['power_ups_active'] - 1)
        
        # 模拟受伤
        if random.random() < 0.02:  # 2%概率受伤
            self.player_performance['damage_taken'] += 1
            self.game_state['lives'] = max(0, self.game_state['lives'] - 1)
        
        # 计算命中率
        total_shots = self.player_performance['enemies_killed'] + self.player_performance['damage_taken']
        if total_shots > 0:
            self.player_performance['accuracy_rate'] = self.player_performance['enemies_killed'] / total_shots
        
        # 计算效率分数
        self.player_performance['efficiency_score'] = (
            self.player_performance['enemies_killed'] * 10 +
            self.player_performance['power_ups_collected'] * 5 -
            self.player_performance['damage_taken'] * 2
        ) / max(1, self.step_count)
    
    def _update_balance_metrics(self):
        """更新游戏平衡指标"""
        # 挑战等级 - 基于敌人数量和射击频率
        enemy_density = self.game_state['enemies_active'] / 10.0
        bullet_density = self.game_state['bullets_active'] / 20.0
        self.balance_metrics['challenge_level'] = (
            enemy_density * 0.6 + bullet_density * 0.4
        )
        
        # 参与度评分 - 基于玩家活动
        activity_score = (
            self.player_performance['enemies_killed'] / max(1, self.step_count) * 10 +
            self.player_performance['power_ups_collected'] / max(1, self.step_count) * 5
        )
        self.balance_metrics['engagement_score'] = np.clip(activity_score, 0.0, 1.0)
        
        # 趣味性评分 - 基于策略多样性和特殊事件
        try:
            strategy_variety = len(set(strategy.get('action', 0) for strategy in self.strategy_history[-10:]))
            special_event_bonus = 0.2 if self.game_state['special_event_active'] else 0.0
            self.balance_metrics['fun_factor'] = np.clip(
                strategy_variety / 6.0 + special_event_bonus, 0.0, 1.0
            )
        except Exception as e:
            # 如果无法计算多样性，使用默认值
            self.balance_metrics['fun_factor'] = 0.1
        
        # 难度递进 - 基于步数和挑战等级
        self.balance_metrics['difficulty_progression'] = np.clip(
            self.step_count / self.max_steps, 0.0, 1.0
        )
        
        # 多样性评分 - 基于策略变化频率
        try:
            recent_changes = len([s for s in self.strategy_history[-20:] if s.get('action', 0) != 0])
            self.balance_metrics['variety_score'] = np.clip(recent_changes / 20.0, 0.0, 1.0)
        except Exception as e:
            # 如果无法计算多样性，使用默认值
            self.balance_metrics['variety_score'] = 0.1
    
    def _calculate_strategy_reward(self) -> float:
        """计算策略效果奖励"""
        reward = 0.0
        
        # 游戏平衡性奖励
        balance_score = (
            self.balance_metrics['challenge_level'] * 0.3 +
            self.balance_metrics['engagement_score'] * 0.3 +
            self.balance_metrics['fun_factor'] * 0.2 +
            self.balance_metrics['difficulty_progression'] * 0.1 +
            self.balance_metrics['variety_score'] * 0.1
        )
        reward += balance_score * self.reward_weights['game_balance']
        
        # 玩家参与度奖励
        engagement_reward = self.balance_metrics['engagement_score'] * self.reward_weights['player_engagement']
        reward += engagement_reward
        
        # 难度递进奖励
        progression_reward = self.balance_metrics['difficulty_progression'] * self.reward_weights['difficulty_progression']
        reward += progression_reward
        
        # 多样性创造奖励
        variety_reward = self.balance_metrics['variety_score'] * self.reward_weights['variety_creation']
        reward += variety_reward
        
        # 挑战维持奖励
        challenge_reward = (1.0 - abs(0.7 - self.balance_metrics['challenge_level'])) * self.reward_weights['challenge_maintenance']
        reward += challenge_reward
        
        # 趣味性优化奖励
        fun_reward = self.balance_metrics['fun_factor'] * self.reward_weights['fun_optimization']
        reward += fun_reward
        
        # 更新统计
        self.stats['total_reward'] += reward
        self.stats['balance_improvements'] += 1 if balance_score > 0.5 else 0
        
        return reward
    
    def _get_observation(self) -> np.ndarray:
        """获取当前游戏策略状态的观察向量"""
        obs = np.zeros(25, dtype=np.float32)
        
        # 游戏状态 [0-4]
        obs[0] = self.game_state['score'] / 1000.0  # 分数归一化
        obs[1] = self.game_state['lives'] / 3.0     # 生命值比例
        obs[2] = self.game_state['enemies_active'] / 10.0  # 敌人数量比例
        obs[3] = self.game_state['power_ups_active'] / 5.0  # 道具数量比例
        obs[4] = self.game_state['bullets_active'] / 20.0   # 子弹数量比例
        
        # 玩家表现 [5-9]
        obs[5] = self.player_performance['survival_time'] / self.max_steps  # 生存时间比例
        obs[6] = self.player_performance['enemies_killed'] / 100.0  # 击杀数归一化
        obs[7] = self.player_performance['power_ups_collected'] / 50.0  # 道具收集数归一化
        obs[8] = self.player_performance['accuracy_rate']  # 命中率
        obs[9] = np.clip(self.player_performance['efficiency_score'], -1.0, 1.0)  # 效率分数
        
        # 游戏平衡 [10-14]
        obs[10] = self.balance_metrics['challenge_level']
        obs[11] = self.balance_metrics['engagement_score']
        obs[12] = self.balance_metrics['fun_factor']
        obs[13] = self.balance_metrics['difficulty_progression']
        obs[14] = self.balance_metrics['variety_score']
        
        # 策略效果 [15-19]
        obs[15] = self.game_strategy['difficulty']
        obs[16] = self.game_strategy['enemy_spawn_rate'] * 10  # 放大到[0,1]
        obs[17] = self.game_strategy['enemy_bullet_frequency'] * 20  # 放大到[0,1]
        obs[18] = self.game_strategy['power_up_drop_rate'] * 50  # 放大到[0,1]
        obs[19] = self.game_strategy['background_intensity']
        
        # 环境状态 [20-24]
        obs[20] = self.game_state['background_type'] / 3.0  # 背景类型
        obs[21] = 1.0 if self.game_state['special_event_active'] else 0.0  # 特殊事件
        obs[22] = self.step_count / self.max_steps  # 步数比例
        obs[23] = len(self.strategy_history) / self.max_history  # 策略历史长度
        obs[24] = self.stats['total_reward'] / 100.0  # 总奖励归一化
        
        return obs
    
    def _is_done(self) -> bool:
        """检查游戏是否结束"""
        return (self.step_count >= self.max_steps or 
                self.game_state['lives'] <= 0)
    
    def render(self):
        """渲染环境（训练时不需要）"""
        pass
    
    def close(self):
        """关闭环境"""
        pass
