#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于机器学习的游戏AI控制器
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import pickle
import os
from typing import Dict, List, Tuple, Any

class GameStateEncoder(nn.Module):
    """游戏状态编码器 - 将游戏状态转换为神经网络输入"""
    
    def __init__(self, input_size=50, hidden_size=128, encoded_size=32):
        super(GameStateEncoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, encoded_size),
            nn.Tanh()
        )
    
    def forward(self, x):
        return self.encoder(x)

class GamePatternGenerator(nn.Module):
    """游戏模式生成器 - 根据编码的游戏状态生成游戏参数"""
    
    def __init__(self, input_size=50, hidden_size=64, output_size=20):
        super(GamePatternGenerator, self).__init__()
        self.generator = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Sigmoid()  # 输出0-1之间的值
        )
    
    def forward(self, x):
        # 确保输入维度正确
        if x.dim() == 1:
            x = x.unsqueeze(0)  # 添加batch维度
        return self.generator(x)

class MLGameAI:
    """基于机器学习的游戏AI控制器"""
    
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🤖 ML游戏AI使用设备: {self.device}")
        
        # 神经网络模型
        self.state_encoder = GameStateEncoder().to(self.device)
        self.pattern_generator = GamePatternGenerator().to(self.device)
        
        # 优化器
        self.encoder_optimizer = optim.Adam(self.state_encoder.parameters(), lr=0.001)
        self.generator_optimizer = optim.Adam(self.pattern_generator.parameters(), lr=0.001)
        
        # 损失函数
        self.encoder_criterion = nn.MSELoss()
        self.generator_criterion = nn.MSELoss()
        
        # 经验回放缓冲区
        self.experience_buffer = deque(maxlen=10000)
        
        # 加载预训练模型（如果存在）
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            print(f"✅ 已加载预训练模型: {model_path}")
    
    def encode_game_state(self, game_state: Dict[str, Any]) -> torch.Tensor:
        """将游戏状态编码为神经网络输入"""
        # 提取关键特征
        features = []
        
        # 玩家状态
        features.extend([
            game_state.get('player_health', 100) / 100.0,  # 归一化生命值
            game_state.get('player_score', 0) / 1000.0,    # 归一化分数
            game_state.get('enemies_killed', 0) / 50.0,    # 归一化击杀数
            game_state.get('survival_time', 0) / 300.0,    # 归一化生存时间
        ])
        
        # 敌机状态
        features.extend([
            len(game_state.get('enemies', [])) / 20.0,     # 归一化敌机数量
            game_state.get('average_enemy_speed', 5) / 10.0,  # 归一化敌机速度
            game_state.get('enemy_density', 0) / 1.0,      # 敌机密度
        ])
        
        # 道具状态
        features.extend([
            len(game_state.get('power_ups', [])) / 10.0,   # 归一化道具数量
            game_state.get('power_up_collection_rate', 0), # 道具收集率
        ])
        
        # 游戏难度
        features.extend([
            game_state.get('ai_difficulty', 1.0) / 2.0,   # 归一化难度
            game_state.get('player_performance', 0.5),     # 玩家表现
        ])
        
        # 填充到固定长度
        while len(features) < 50:
            features.append(0.0)
        
        return torch.FloatTensor(features[:50]).to(self.device)
    
    def generate_game_pattern(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """根据游戏状态生成游戏模式"""
        # 编码游戏状态
        encoded_state = self.encode_game_state(game_state)
        
        # 生成游戏参数
        with torch.no_grad():
            # 确保输入维度正确
            if encoded_state.dim() == 1:
                encoded_state = encoded_state.unsqueeze(0)
            # 直接使用编码后的状态，不经过状态编码器
            pattern_params = self.pattern_generator(encoded_state)
            # 移除batch维度
            pattern_params = pattern_params.squeeze(0)
        
        # 将神经网络输出转换为游戏参数
        pattern = self._decode_pattern(pattern_params)
        
        return pattern
    
    def _decode_pattern(self, pattern_params: torch.Tensor) -> Dict[str, Any]:
        """将神经网络输出解码为游戏参数"""
        params = pattern_params.cpu().numpy()
        
        # 敌机生成模式
        pattern_type_idx = int(params[0] * 4)  # 0-4对应5种模式
        pattern_types = ['wave', 'spiral', 'formation', 'random', 'chaos']
        pattern_type = pattern_types[pattern_type_idx]
        
        # 根据模式类型生成具体参数
        if pattern_type == 'wave':
            return {
                'type': 'wave',
                'wave_count': int(params[1] * 5) + 3,      # 3-8波
                'enemies_per_wave': int(params[2] * 10) + 5,  # 5-15个
                'wave_delay': params[3] * 3 + 2,           # 2-5秒
                'enemy_speed': int(params[4] * 4) + 1,     # 1-5速度
                'enemy_health': int(params[5] * 4) + 1,    # 1-5生命值
                'enemy_behavior': self._select_behavior(params[6])
            }
        elif pattern_type == 'spiral':
            return {
                'type': 'spiral',
                'spiral_arms': int(params[1] * 4) + 2,     # 2-6臂
                'enemies_per_arm': int(params[2] * 12) + 8,  # 8-20个
                'spiral_tightness': params[3] * 1.5 + 0.5,   # 0.5-2.0
                'enemy_speed': int(params[4] * 4) + 1,
                'enemy_health': int(params[5] * 4) + 1,
                'enemy_behavior': self._select_behavior(params[6])
            }
        elif pattern_type == 'formation':
            return {
                'type': 'formation',
                'formation_type': self._select_formation(params[1]),
                'formation_size': int(params[2] * 4) + 3,   # 3-7个
                'formation_spacing': params[3] * 100 + 50,   # 50-150
                'enemy_speed': int(params[4] * 4) + 1,
                'enemy_health': int(params[5] * 4) + 1,
                'enemy_behavior': self._select_behavior(params[6])
            }
        else:  # random, chaos
            return {
                'type': pattern_type,
                'enemy_count': int(params[1] * 30) + 20,    # 20-50个
                'spawn_interval': params[2] * 1.5 + 0.5,   # 0.5-2.0秒
                'enemy_speed': int(params[3] * 4) + 1,
                'enemy_health': int(params[4] * 4) + 1,
                'enemy_behavior': self._select_behavior(params[5])
            }
    
    def _select_behavior(self, param: float) -> str:
        """根据参数选择敌机行为"""
        behaviors = ['straight', 'zigzag', 'circle', 'chase', 'evade']
        idx = int(param * len(behaviors))
        return behaviors[min(idx, len(behaviors) - 1)]
    
    def _select_formation(self, param: float) -> str:
        """根据参数选择编队类型"""
        formations = ['v', 'square', 'triangle', 'diamond']
        idx = int(param * len(formations))
        return formations[min(idx, len(formations) - 1)]
    
    def learn_from_experience(self, game_state: Dict[str, Any], 
                            generated_pattern: Dict[str, Any], 
                            game_outcome: Dict[str, Any]):
        """从游戏经验中学习"""
        # 计算奖励
        reward = self._calculate_reward(game_outcome)
        
        # 存储经验
        experience = {
            'state': game_state,
            'pattern': generated_pattern,
            'reward': reward,
            'outcome': game_outcome
        }
        self.experience_buffer.append(experience)
        
        # 如果经验足够，进行学习
        if len(self.experience_buffer) >= 100:
            self._train_models()
    
    def _calculate_reward(self, game_outcome: Dict[str, Any]) -> float:
        """计算游戏结果的奖励"""
        reward = 0.0
        
        # 生存时间奖励
        survival_time = game_outcome.get('survival_time', 0)
        reward += min(survival_time / 60.0, 1.0) * 10  # 最多10分
        
        # 击杀奖励
        enemies_killed = game_outcome.get('enemies_killed', 0)
        reward += min(enemies_killed / 20.0, 1.0) * 5   # 最多5分
        
        # 分数奖励
        score = game_outcome.get('score', 0)
        reward += min(score / 1000.0, 1.0) * 3          # 最多3分
        
        # 惩罚项
        damage_taken = game_outcome.get('damage_taken', 0)
        reward -= min(damage_taken / 100.0, 1.0) * 2    # 最多扣2分
        
        return reward
    
    def _train_models(self):
        """训练神经网络模型"""
        if len(self.experience_buffer) < 100:
            return
        
        # 随机采样经验
        batch_size = min(32, len(self.experience_buffer))
        batch = random.sample(self.experience_buffer, batch_size)
        
        # 准备训练数据
        states = []
        rewards = []
        
        for exp in batch:
            states.append(self.encode_game_state(exp['state']))
            rewards.append(exp['reward'])
        
        states = torch.stack(states)
        rewards = torch.FloatTensor(rewards).to(self.device)
        
        # 训练状态编码器
        self.encoder_optimizer.zero_grad()
        encoded_states = self.state_encoder(states)
        encoder_loss = self.encoder_criterion(encoded_states.mean(dim=0), 
                                           rewards.mean().expand(encoded_states.size(1)))
        encoder_loss.backward()
        self.encoder_optimizer.step()
        
        # 训练模式生成器
        self.generator_optimizer.zero_grad()
        generated_patterns = self.pattern_generator(encoded_states)
        generator_loss = self.generator_criterion(generated_patterns.mean(dim=0), 
                                               rewards.mean().expand(generated_patterns.size(1)))
        generator_loss.backward()
        self.generator_optimizer.step()
        
        print(f"🤖 模型训练完成 - 编码器损失: {encoder_loss.item():.4f}, 生成器损失: {generator_loss.item():.4f}")
    
    def save_model(self, model_path: str):
        """保存模型"""
        torch.save({
            'state_encoder': self.state_encoder.state_dict(),
            'pattern_generator': self.pattern_generator.state_dict(),
            'encoder_optimizer': self.encoder_optimizer.state_dict(),
            'generator_optimizer': self.generator_optimizer.state_dict(),
        }, model_path)
        print(f"✅ 模型已保存到: {model_path}")
    
    def load_model(self, model_path: str):
        """加载模型"""
        checkpoint = torch.load(model_path, map_location=self.device)
        self.state_encoder.load_state_dict(checkpoint['state_encoder'])
        self.pattern_generator.load_state_dict(checkpoint['pattern_generator'])
        self.encoder_optimizer.load_state_dict(checkpoint['encoder_optimizer'])
        self.generator_optimizer.load_state_dict(checkpoint['generator_optimizer'])
        print(f"✅ 模型已从 {model_path} 加载")

# 使用示例
if __name__ == "__main__":
    # 创建ML游戏AI
    ml_ai = MLGameAI()
    
    # 模拟游戏状态
    game_state = {
        'player_health': 75,
        'player_score': 450,
        'enemies_killed': 12,
        'survival_time': 45,
        'enemies': [{'speed': 3, 'health': 2}] * 8,
        'power_ups': [{'type': 'health'}] * 2,
        'ai_difficulty': 1.2,
        'player_performance': 0.7
    }
    
    # 生成游戏模式
    pattern = ml_ai.generate_game_pattern(game_state)
    print(f"🎮 生成的游戏模式: {pattern}")
    
    # 模拟游戏结果
    game_outcome = {
        'survival_time': 67,
        'enemies_killed': 18,
        'score': 720,
        'damage_taken': 45
    }
    
    # 学习
    ml_ai.learn_from_experience(game_state, pattern, game_outcome)
    
    # 保存模型
    ml_ai.save_model('./models/ml_game_ai.pth')
