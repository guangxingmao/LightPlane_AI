#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI决策控制器
使用训练好的强化学习模型进行智能决策
替代原有的规则AI系统
"""

import numpy as np
import pygame
import math
import os
from typing import Dict, List, Tuple, Any, Optional

try:
    from stable_baselines3 import PPO, DQN, A2C
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False
    print("⚠️ Stable Baselines3 未安装，将使用简单AI作为备用")

class AIDecisionController:
    """AI决策控制器 - 使用训练好的模型进行智能决策"""
    
    def __init__(self, hero, enemy_group, screen_width, screen_height, 
                 model_path="./models/ai_decision_ppo/final", 
                 env_normalize_path="./models/ai_decision_ppo/env_normalize"):
        self.hero = hero
        self.enemy_group = enemy_group
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.model_path = model_path
        self.env_normalize_path = env_normalize_path
        
        # AI模型
        self.model = None
        self.use_ai_model = False
        
        # 环境标准化
        self.obs_normalizer = None
        self.reward_normalizer = None
        
        # 决策参数
        self.decision_timer = 0
        self.decision_interval = 30  # 每30帧做一次决策
        self.last_action = 0
        self.action_stability = 0
        
        # 移动参数
        self.move_speed = 3
        self.target_x = hero.rect.centerx if hero and hasattr(hero, 'rect') else screen_width // 2
        self.target_y = hero.rect.centery if hero and hasattr(hero, 'rect') else screen_height // 2
        self.moving = False
        
        # 尝试加载AI模型
        if SB3_AVAILABLE:
            self._load_ai_model()
        
        # 如果没有AI模型，使用简单AI作为备用
        if not self.use_ai_model:
            print("🤖 使用简单AI控制器作为备用")
            from .optimized_ai_controller import OptimizedAIController
            self.backup_ai = OptimizedAIController(hero, enemy_group, screen_width, screen_height, False)
        else:
            self.backup_ai = None
        
        # 动作映射
        self.action_directions = [
            (0, -1),   # 0: 上
            (1, -1),   # 1: 右上
            (1, 0),    # 2: 右
            (1, 1),    # 3: 右下
            (0, 1),    # 4: 下
            (-1, 1),   # 5: 左下
            (-1, 0),   # 6: 左
            (-1, -1),  # 7: 左上
        ]
        
        print(f"🧠 AI决策控制器初始化完成")
        print(f"   AI模型可用: {self.use_ai_model}")
        if self.use_ai_model:
            print(f"   模型路径: {model_path}")
    
    def _load_ai_model(self):
        """加载AI模型"""
        try:
            # 检查模型文件是否存在
            if not os.path.exists(f"{self.model_path}.zip"):
                print(f"⚠️ AI模型文件不存在: {self.model_path}.zip")
                return
            
            # 加载模型
            if "ppo" in self.model_path.lower():
                self.model = PPO.load(self.model_path)
            elif "dqn" in self.model_path.lower():
                self.model = DQN.load(self.model_path)
            elif "a2c" in self.model_path.lower():
                self.model = A2C.load(self.model_path)
            else:
                # 默认使用PPO
                self.model = PPO.load(self.model_path)
            
            self.use_ai_model = True
            print(f"✅ 成功加载AI模型: {self.model_path}")
            
            # 加载环境标准化参数
            if os.path.exists(f"{self.env_normalize_path}.pkl"):
                from stable_baselines3.common.vec_env import VecNormalize
                self.obs_normalizer = VecNormalize.load(
                    self.env_normalize_path, 
                    self.model.get_env()
                )
                print(f"✅ 环境标准化参数加载成功")
            
        except Exception as e:
            print(f"❌ 加载AI模型失败: {e}")
            self.use_ai_model = False
    
    def update(self, game_started=True, game_paused=False):
        """更新AI决策"""
        if not game_started or game_paused:
            return
        
        if self.use_ai_model and self.model:
            self._update_with_ai_model()
        elif self.backup_ai:
            self.backup_ai.update(game_started, game_paused)
    
    def _update_with_ai_model(self):
        """使用AI模型进行决策"""
        self.decision_timer += 1
        
        # 减少决策频率，但保持移动流畅
        if self.decision_timer >= self.decision_interval:
            try:
                # 获取当前游戏状态观察
                observation = self._get_observation()
                
                # 标准化观察（如果可用）
                if self.obs_normalizer:
                    observation = self.obs_normalizer.normalize_obs(observation)
                
                # 使用模型预测动作
                action, _states = self.model.predict(observation, deterministic=True)
                action = int(action)
                
                # 执行动作
                self._execute_action(action)
                
                # 重置决策计时器
                self.decision_timer = 0
                
            except Exception as e:
                print(f"❌ AI决策出错: {e}")
                # 出错时切换到备用AI
                if self.backup_ai:
                    self.backup_ai.update(True, False)
        
        # 持续执行移动
        if self.moving:
            self._execute_movement()
    
    def _get_observation(self) -> np.ndarray:
        """获取当前游戏状态的观察向量"""
        obs = np.zeros(28, dtype=np.float32)
        
        # 玩家信息 [0-4]
        if self.hero and hasattr(self.hero, 'rect'):
            obs[0] = (self.hero.rect.centerx / self.screen_width) * 2 - 1
            obs[1] = (self.hero.rect.centery / self.screen_height) * 2 - 1
            obs[2] = getattr(self.hero, 'life', 3) / 3.0  # 生命值比例
            obs[3] = 0.0  # 分数比例（暂时设为0）
            obs[4] = 0.0  # 游戏结束标志
        
        # 敌人信息 [5-14] (最多2个敌人，每个5个特征)
        enemies = list(self.enemy_group)[:2]
        for i, enemy in enumerate(enemies):
            if enemy and hasattr(enemy, 'rect'):
                offset = 5 + i * 5
                obs[offset] = (enemy.rect.centerx / self.screen_width) * 2 - 1
                obs[offset + 1] = (enemy.rect.centery / self.screen_height) * 2 - 1
                obs[offset + 2] = getattr(enemy, 'speed', 2) / 3.0  # 速度归一化
                obs[offset + 3] = getattr(enemy, 'health', 1) / 3.0  # 生命值归一化
                obs[offset + 4] = 1.0  # 存在标志
        
        # 子弹信息 [15-20] (暂时设为0，因为游戏中的子弹处理方式不同)
        for i in range(2):
            offset = 15 + i * 3
            obs[offset:offset + 3] = 0.0
        
        # 道具信息 [21-24] (暂时设为0)
        obs[21:25] = 0.0
        
        # 游戏状态 [25-27]
        obs[25] = 0.0  # 步数比例
        obs[26] = len(self.enemy_group) / 5.0  # 敌人数量比例
        obs[27] = 0.0  # 道具数量比例
        
        return obs
    
    def _execute_action(self, action: int):
        """执行AI预测的动作"""
        if action < 8:  # 移动动作
            self._set_movement_target(action)
        elif action == 8:  # 射击动作
            self._execute_shooting()
        
        # 更新动作稳定性
        if action == self.last_action:
            self.action_stability += 1
        else:
            self.action_stability = 0
        
        self.last_action = action
    
    def _set_movement_target(self, direction: int):
        """设置移动目标"""
        if not self.hero or not hasattr(self.hero, 'rect'):
            return
        
        # 获取当前玩家位置
        current_x = self.hero.rect.centerx
        current_y = self.hero.rect.centery
        
        # 计算移动向量
        dx, dy = self.action_directions[direction]
        
        # 计算目标位置
        target_distance = 50  # 移动距离
        self.target_x = current_x + dx * target_distance
        self.target_y = current_y + dy * target_distance
        
        # 边界检查
        self.target_x = max(25, min(self.screen_width - 25, self.target_x))
        self.target_y = max(25, min(self.screen_height - 25, self.target_y))
        
        # 开始移动
        self.moving = True
    
    def _execute_movement(self):
        """执行移动"""
        if not self.moving or not self.hero:
            return
        
        # 计算到目标的距离
        dx = self.target_x - self.hero.rect.centerx
        dy = self.target_y - self.hero.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        # 如果已经接近目标，停止移动
        if distance < 5:
            self.moving = False
            return
        
        # 计算移动速度
        if distance > 0:
            # 标准化移动向量
            dx = (dx / distance) * self.move_speed
            dy = (dy / distance) * self.move_speed
            
            # 更新位置
            new_x = self.hero.rect.centerx + dx
            new_y = self.hero.rect.centery + dy
            
            # 边界检查
            new_x = max(25, min(self.screen_width - 25, new_x))
            new_y = max(25, min(self.screen_height - 25, new_y))
            
            # 更新英雄位置
            self.hero.rect.centerx = int(new_x)
            self.hero.rect.centery = int(new_y)
    
    def _execute_shooting(self):
        """执行射击"""
        if not self.hero:
            return
        
        # 检查是否可以射击
        if hasattr(self.hero, 'time_count') and self.hero.time_count > 0:
            if hasattr(self.hero, 'fire'):
                self.hero.fire()
    
    def apply_strategy(self, strategy: Dict[str, Any]):
        """应用AI策略（兼容性方法）"""
        if not strategy:
            return
        
        # 根据策略调整行为参数
        if 'aggression' in strategy:
            # 攻击性影响射击频率
            if strategy['aggression'] > 0.7:
                self.decision_interval = 20  # 高攻击性，更频繁决策
            elif strategy['aggression'] < 0.3:
                self.decision_interval = 40  # 低攻击性，较少决策
        
        if 'speed' in strategy:
            # 速度影响移动速度
            self.move_speed = max(2, min(5, strategy['speed'] * 3))
        
        if 'defense' in strategy:
            # 防御性影响移动距离
            if strategy['defense'] > 0.7:
                # 高防御性，移动距离较短
                pass  # 可以在_set_movement_target中实现
        
        print(f"🎯 AI策略已应用: 攻击性={strategy.get('aggression', 0):.2f}, "
              f"防御性={strategy.get('defense', 0):.2f}, 速度={strategy.get('speed', 0):.2f}")
    
    def get_ai_info(self) -> Dict[str, Any]:
        """获取AI信息"""
        info = {
            'controller_type': 'AI决策控制器',
            'ai_model_loaded': self.use_ai_model,
            'model_path': self.model_path if self.use_ai_model else 'None',
            'decision_interval': self.decision_interval,
            'move_speed': self.move_speed,
            'action_stability': self.action_stability,
            'last_action': self.last_action,
            'moving': self.moving
        }
        
        if self.use_ai_model:
            info['model_type'] = type(self.model).__name__
            info['obs_normalizer'] = self.obs_normalizer is not None
        
        return info
    
    def reset(self):
        """重置控制器状态"""
        self.decision_timer = 0
        self.moving = False
        self.action_stability = 0
        self.last_action = 0
        
        # 重置目标位置到当前位置
        if self.hero and hasattr(self.hero, 'rect'):
            self.target_x = self.hero.rect.centerx
            self.target_y = self.hero.rect.centery


# 工厂函数，用于创建AI决策控制器
def create_ai_decision_controller(hero, enemy_group, screen_width, screen_height, 
                                 model_path="./models/ai_decision_ppo/final"):
    """创建AI决策控制器"""
    return AIDecisionController(
        hero, enemy_group, screen_width, screen_height, model_path
    )


if __name__ == "__main__":
    print("🧪 测试AI决策控制器...")
    print(f"📦 Stable Baselines3 可用: {SB3_AVAILABLE}")
    
    # 这里可以添加测试代码
    print("✅ AI决策控制器模块加载成功")
