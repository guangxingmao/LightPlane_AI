import numpy as np
import pygame
import math
import random
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import gymnasium as gym
from gymnasium import spaces
import os

class PlaneFighterEnv(gym.Env):
    """飞机大战强化学习环境"""
    
    def __init__(self, screen_width, screen_height):
        super().__init__()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 动作空间：移动方向 + 射击
        # [x_move, y_move, shoot] 
        # x_move: -1(左), 0(不动), 1(右)
        # y_move: -1(上), 0(不动), 1(下)
        # shoot: 0(不射击), 1(射击)
        self.action_space = spaces.MultiDiscrete([3, 3, 2])
        
        # 观察空间：AI飞机位置、最近敌人位置、敌人数量、生命值等
        # [ai_x, ai_y, nearest_enemy_x, nearest_enemy_y, enemy_count, life, score]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0]),
            high=np.array([screen_width, screen_height, screen_width, screen_height, 10, 3, 1000]),
            dtype=np.float32
        )
        
        # 环境状态
        self.reset()
    
    def reset(self, seed=None):
        """重置环境"""
        super().reset(seed=seed)
        
        # 初始化AI飞机位置（右侧居中）
        self.ai_x = self.screen_width * 0.8
        self.ai_y = self.screen_height * 0.5
        
        # 初始化敌人位置
        self.enemies = []
        for _ in range(3):
            enemy = {
                'x': random.uniform(0, self.screen_width * 0.6),
                'y': random.uniform(50, self.screen_height - 50)
            }
            self.enemies.append(enemy)
        
        # 游戏状态
        self.life = 3
        self.score = 0
        self.steps = 0
        
        return self._get_observation(), {}
    
    def step(self, action):
        """执行动作"""
        self.steps += 1
        
        # 解析动作
        x_move, y_move, shoot = action
        
        # 移动AI飞机
        if x_move == 0:  # 左移
            self.ai_x = max(50, self.ai_x - 5)
        elif x_move == 2:  # 右移
            self.ai_x = min(self.screen_width - 50, self.ai_x + 5)
            
        if y_move == 0:  # 上移
            self.ai_y = max(50, self.ai_y - 5)
        elif y_move == 2:  # 下移
            self.ai_y = min(self.screen_height - 50, self.ai_y + 5)
        
        # 处理射击
        if shoot == 1:
            self._handle_shooting()
        
        # 更新敌人
        self._update_enemies()
        
        # 检查碰撞
        self._check_collisions()
        
        # 计算奖励
        reward = self._calculate_reward()
        
        # 检查游戏是否结束
        done = self.life <= 0 or self.steps >= 1000
        
        # 获取观察
        observation = self._get_observation()
        
        return observation, reward, done, False, {}
    
    def _handle_shooting(self):
        """处理射击逻辑"""
        # 找到最近的敌人
        if self.enemies:
            nearest_enemy = min(self.enemies, 
                              key=lambda e: math.sqrt((e['x'] - self.ai_x)**2 + (e['y'] - self.ai_y)**2))
            
            # 计算射击方向
            dx = nearest_enemy['x'] - self.ai_x
            dy = nearest_enemy['y'] - self.ai_y
            distance = math.sqrt(dx**2 + dy**2)
            
            # 如果敌人在射击范围内，增加分数
            if distance < 300:
                self.score += 1
                # 移除被击中的敌人
                self.enemies.remove(nearest_enemy)
                # 生成新敌人
                if len(self.enemies) < 3:
                    new_enemy = {
                        'x': random.uniform(0, self.screen_width * 0.6),
                        'y': random.uniform(50, self.screen_height - 50)
                    }
                    self.enemies.append(new_enemy)
    
    def _update_enemies(self):
        """更新敌人位置"""
        for enemy in self.enemies:
            # 敌人向AI飞机移动
            dx = self.ai_x - enemy['x']
            dy = self.ai_y - enemy['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # 标准化移动向量
                dx = dx / distance * 2
                dy = dy / distance * 2
                
                enemy['x'] += dx
                enemy['y'] += dy
    
    def _check_collisions(self):
        """检查碰撞"""
        for enemy in self.enemies[:]:  # 使用切片避免在迭代时修改列表
            distance = math.sqrt((enemy['x'] - self.ai_x)**2 + (enemy['y'] - self.ai_y)**2)
            if distance < 30:  # 碰撞距离
                self.life -= 1
                self.enemies.remove(enemy)
                # 生成新敌人
                new_enemy = {
                    'x': random.uniform(0, self.screen_width * 0.6),
                    'y': random.uniform(50, self.screen_height - 50)
                }
                self.enemies.append(new_enemy)
    
    def _calculate_reward(self):
        """计算奖励"""
        reward = 0
        
        # 生存奖励
        reward += 0.1
        
        # 击杀敌人奖励
        reward += self.score * 10
        
        # 生命值奖励
        reward += self.life * 5
        
        # 距离惩罚（鼓励保持安全距离）
        if self.enemies:
            min_distance = min(math.sqrt((e['x'] - self.ai_x)**2 + (e['y'] - self.ai_y)**2) 
                             for e in self.enemies)
            if min_distance < 50:
                reward -= 5  # 太近的惩罚
            elif min_distance > 200:
                reward += 2  # 保持适当距离的奖励
        
        # 死亡惩罚
        if self.life <= 0:
            reward -= 100
        
        return reward
    
    def _get_observation(self):
        """获取观察状态"""
        if not self.enemies:
            # 没有敌人时，使用默认值
            nearest_enemy_x = 0
            nearest_enemy_y = 0
            enemy_count = 0
        else:
            # 找到最近的敌人
            nearest_enemy = min(self.enemies, 
                              key=lambda e: math.sqrt((e['x'] - self.ai_x)**2 + (e['y'] - self.ai_y)**2))
            nearest_enemy_x = nearest_enemy['x']
            nearest_enemy_y = nearest_enemy['y']
            enemy_count = len(self.enemies)
        
        return np.array([
            self.ai_x,
            self.ai_y,
            nearest_enemy_x,
            nearest_enemy_y,
            enemy_count,
            self.life,
            self.score
        ], dtype=np.float32)

class RLController:
    """强化学习AI控制器"""
    
    def __init__(self, hero2, enemy_group, screen_width, screen_height):
        self.hero2 = hero2
        self.enemy_group = enemy_group
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 创建强化学习环境
        self.env = PlaneFighterEnv(screen_width, screen_height)
        
        # 模型文件路径
        self.model_path = "ai_plane_model.zip"
        
        # 尝试加载预训练模型，如果没有则创建新模型
        if os.path.exists(self.model_path):
            print("加载预训练AI模型...")
            self.model = PPO.load(self.model_path)
        else:
            print("创建新的AI模型...")
            self.model = PPO("MlpPolicy", self.env, verbose=1, learning_rate=0.0003)
        
        # 训练参数
        self.training_mode = False
        self.training_steps = 0
        self.max_training_steps = 10000
        
        # 决策参数
        self.decision_timer = 0
        self.decision_interval = 5  # 每5帧做一次决策
        
        # 性能统计
        self.total_reward = 0
        self.episode_count = 0
    
    def update(self):
        """更新AI决策"""
        self.decision_timer += 1
        
        if self.decision_timer >= self.decision_interval:
            self._make_decision()
            self.decision_timer = 0
    
    def _make_decision(self):
        """使用强化学习模型做决策"""
        try:
            # 获取当前环境状态
            observation = self._get_current_observation()
            
            # 使用模型预测动作
            action, _ = self.model.predict(observation, deterministic=True)
            
            # 执行动作
            self._execute_action(action)
            
            # 如果启用训练模式，进行训练
            if self.training_mode:
                self._train_step(observation, action)
                
        except Exception as e:
            print(f"AI决策错误: {e}")
            # 如果出错，使用备用策略
            self._fallback_behavior()
    
    def _get_current_observation(self):
        """获取当前游戏状态的观察"""
        # 获取AI飞机位置
        ai_x = self.hero2.rect.centerx
        ai_y = self.hero2.rect.centery
        
        # 获取最近的敌人信息
        nearest_enemy_x = 0
        nearest_enemy_y = 0
        enemy_count = len(self.enemy_group)
        
        if enemy_count > 0:
            # 找到最近的敌人
            min_distance = float('inf')
            for enemy in self.enemy_group:
                distance = math.sqrt((enemy.rect.centerx - ai_x)**2 + (enemy.rect.centery - ai_y)**2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_enemy_x = enemy.rect.centerx
                    nearest_enemy_y = enemy.rect.centery
        
        # 获取游戏状态（这里需要从游戏页面获取，暂时使用默认值）
        life = 3  # 应该从游戏页面获取
        score = 0  # 应该从游戏页面获取
        
        return np.array([
            ai_x, ai_y, nearest_enemy_x, nearest_enemy_y, 
            enemy_count, life, score
        ], dtype=np.float32)
    
    def _execute_action(self, action):
        """执行AI动作"""
        x_move, y_move, shoot = action
        
        # 移动AI飞机
        if x_move == 0:  # 左移
            self.hero2.rect.centerx = max(50, self.hero2.rect.centerx - 5)
        elif x_move == 2:  # 右移
            self.hero2.rect.centerx = min(self.screen_width - 50, self.hero2.rect.centerx + 5)
            
        if y_move == 0:  # 上移
            self.hero2.rect.centery = max(50, self.hero2.rect.centery - 5)
        elif y_move == 2:  # 下移
            self.hero2.rect.centery = min(self.screen_height - 50, self.hero2.rect.centery + 5)
        
        # 射击
        if shoot == 1 and self.hero2.time_count > 0:
            self.hero2.fire()
    
    def _fallback_behavior(self):
        """备用行为策略"""
        # 简单的巡逻行为
        patrol_center_x = self.screen_width * 0.8
        patrol_center_y = self.screen_height * 0.5
        
        # 向巡逻中心移动
        dx = patrol_center_x - self.hero2.rect.centerx
        dy = patrol_center_y - self.hero2.rect.centery
        
        if abs(dx) > 10:
            self.hero2.rect.centerx += 3 if dx > 0 else -3
        if abs(dy) > 10:
            self.hero2.rect.centery += 3 if dy > 0 else -3
    
    def _train_step(self, observation, action):
        """训练步骤"""
        # 这里可以实现在线学习，但为了稳定性，我们暂时只做记录
        self.training_steps += 1
        
        if self.training_steps >= self.max_training_steps:
            print("AI训练完成，保存模型...")
            self.model.save(self.model_path)
            self.training_mode = False
    
    def start_training(self):
        """开始训练模式"""
        print("开始AI训练...")
        self.training_mode = True
        self.training_steps = 0
    
    def stop_training(self):
        """停止训练模式"""
        print("停止AI训练...")
        self.training_mode = False
        # 保存模型
        self.model.save(self.model_path)
    
    def get_performance_stats(self):
        """获取性能统计"""
        return {
            'training_mode': self.training_mode,
            'training_steps': self.training_steps,
            'episode_count': self.episode_count,
            'total_reward': self.total_reward
        }
