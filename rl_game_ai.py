#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于强化学习的游戏AI控制器
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
import random
import os
from typing import Dict, List, Tuple, Any

class DQNNetwork(nn.Module):
    """深度Q网络 - 用于强化学习"""
    
    def __init__(self, state_size=50, action_size=20, hidden_size=128):
        super(DQNNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, action_size)
        
        # 权重初始化
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.xavier_uniform_(module.weight)
            module.bias.data.fill_(0.01)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

class RLGameAI:
    """基于强化学习的游戏AI控制器"""
    
    def __init__(self, state_size=50, action_size=20, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🤖 RL游戏AI使用设备: {self.device}")
        
        # 网络参数
        self.state_size = state_size
        self.action_size = action_size
        self.hidden_size = 128
        
        # 神经网络
        self.q_network = DQNNetwork(state_size, action_size, self.hidden_size).to(self.device)
        self.target_network = DQNNetwork(state_size, action_size, self.hidden_size).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # 优化器
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=0.001)
        
        # 强化学习参数
        self.epsilon = 1.0          # 探索率
        self.epsilon_min = 0.01     # 最小探索率
        self.epsilon_decay = 0.995  # 探索率衰减
        self.gamma = 0.95           # 折扣因子
        self.learning_rate = 0.001  # 学习率
        
        # 经验回放
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        
        # 训练参数
        self.update_target_every = 100  # 每100步更新目标网络
        self.step_count = 0
        
        # 加载预训练模型
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            print(f"✅ 已加载预训练RL模型: {model_path}")
    
    def encode_game_state(self, game_state: Dict[str, Any]) -> torch.Tensor:
        """将游戏状态编码为神经网络输入"""
        features = []
        
        # 玩家状态
        features.extend([
            game_state.get('player_health', 100) / 100.0,
            game_state.get('player_score', 0) / 1000.0,
            game_state.get('enemies_killed', 0) / 50.0,
            game_state.get('survival_time', 0) / 300.0,
            game_state.get('player_position', {}).get('x', 400) / 800.0,
            game_state.get('player_position', {}).get('y', 300) / 600.0,
        ])
        
        # 敌机状态
        enemies = game_state.get('enemies', [])
        features.extend([
            len(enemies) / 20.0,
            sum(e.get('speed', 5) for e in enemies) / max(len(enemies), 1) / 10.0,
            sum(e.get('health', 1) for e in enemies) / max(len(enemies), 1) / 5.0,
        ])
        
        # 道具状态
        power_ups = game_state.get('power_ups', [])
        features.extend([
            len(power_ups) / 10.0,
            sum(1 for p in power_ups if p.get('type') == 'health') / max(len(power_ups), 1),
            sum(1 for p in power_ups if p.get('type') == 'shield') / max(len(power_ups), 1),
        ])
        
        # 游戏环境
        features.extend([
            game_state.get('ai_difficulty', 1.0) / 2.0,
            game_state.get('player_performance', 0.5),
            game_state.get('frame_count', 0) / 1000.0,
        ])
        
        # 填充到固定长度
        while len(features) < self.state_size:
            features.append(0.0)
        
        return torch.FloatTensor(features[:self.state_size]).to(self.device)
    
    def select_action(self, game_state: Dict[str, Any]) -> int:
        """选择动作（epsilon-greedy策略）"""
        if random.random() < self.epsilon:
            # 探索：随机选择动作
            return random.randrange(self.action_size)
        else:
            # 利用：选择Q值最大的动作
            state = self.encode_game_state(game_state)
            with torch.no_grad():
                q_values = self.q_network(state)
            return q_values.argmax().item()
    
    def decode_action(self, action_id: int) -> Dict[str, Any]:
        """将动作ID解码为游戏参数"""
        # 动作空间定义：20个不同的游戏配置
        actions = [
            # 波次攻击模式
            {'type': 'wave', 'wave_count': 3, 'enemies_per_wave': 5, 'wave_delay': 2.0},
            {'type': 'wave', 'wave_count': 5, 'enemies_per_wave': 8, 'wave_delay': 3.0},
            {'type': 'wave', 'wave_count': 7, 'enemies_per_wave': 12, 'wave_delay': 4.0},
            {'type': 'wave', 'wave_count': 8, 'enemies_per_wave': 15, 'wave_delay': 5.0},
            
            # 螺旋攻击模式
            {'type': 'spiral', 'spiral_arms': 2, 'enemies_per_arm': 8, 'spiral_tightness': 0.5},
            {'type': 'spiral', 'spiral_arms': 3, 'enemies_per_arm': 10, 'spiral_tightness': 1.0},
            {'type': 'spiral', 'spiral_arms': 4, 'enemies_per_arm': 15, 'spiral_tightness': 1.5},
            {'type': 'spiral', 'spiral_arms': 6, 'enemies_per_arm': 20, 'spiral_tightness': 2.0},
            
            # 编队攻击模式
            {'type': 'formation', 'formation_type': 'v', 'formation_size': 3, 'formation_spacing': 50},
            {'type': 'formation', 'formation_type': 'square', 'formation_size': 4, 'formation_spacing': 80},
            {'type': 'formation', 'formation_type': 'triangle', 'formation_size': 5, 'formation_spacing': 100},
            {'type': 'formation', 'formation_type': 'diamond', 'formation_size': 6, 'formation_spacing': 120},
            
            # 随机攻击模式
            {'type': 'random', 'enemy_count': 20, 'spawn_interval': 0.5},
            {'type': 'random', 'enemy_count': 30, 'spawn_interval': 1.0},
            {'type': 'random', 'enemy_count': 40, 'spawn_interval': 1.5},
            {'type': 'random', 'enemy_count': 50, 'spawn_interval': 2.0},
            
            # 混沌攻击模式
            {'type': 'chaos', 'enemy_count': 25, 'spawn_interval': 0.8},
            {'type': 'chaos', 'enemy_count': 35, 'spawn_interval': 1.2},
            {'type': 'chaos', 'enemy_count': 45, 'spawn_interval': 1.8},
            {'type': 'chaos', 'enemy_count': 55, 'spawn_interval': 2.5},
        ]
        
        # 添加随机参数变化
        action = actions[action_id].copy()
        if 'enemy_speed' not in action:
            action['enemy_speed'] = random.randint(1, 5)
        if 'enemy_health' not in action:
            action['enemy_health'] = random.randint(1, 5)
        if 'enemy_behavior' not in action:
            action['enemy_behavior'] = random.choice(['straight', 'zigzag', 'circle', 'chase', 'evade'])
        
        return action
    
    def remember(self, state: Dict[str, Any], action: int, reward: float, 
                next_state: Dict[str, Any], done: bool):
        """存储经验到回放缓冲区"""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        """从经验回放中学习"""
        if len(self.memory) < self.batch_size:
            return
        
        # 随机采样经验
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # 转换为张量
        states = torch.stack([self.encode_game_state(s) for s in states])
        next_states = torch.stack([self.encode_game_state(s) for s in next_states])
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        dones = torch.BoolTensor(dones).to(self.device)
        
        # 计算当前Q值
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # 计算目标Q值
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        # 计算损失
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # 反向传播
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # 更新探索率
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # 更新目标网络
        self.step_count += 1
        if self.step_count % self.update_target_every == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        return loss.item()
    
    def act(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """根据当前游戏状态选择并执行动作"""
        # 选择动作
        action_id = self.select_action(game_state)
        
        # 解码动作
        action_params = self.decode_action(action_id)
        
        return action_params
    
    def learn_from_game(self, game_states: List[Dict[str, Any]], 
                        actions: List[int], 
                        game_outcome: Dict[str, Any]):
        """从完整游戏过程中学习"""
        if len(game_states) < 2:
            return
        
        # 计算每个状态的奖励
        total_reward = self._calculate_game_reward(game_outcome)
        reward_per_step = total_reward / len(game_states)
        
        # 为每个状态分配奖励
        for i, (state, action) in enumerate(zip(game_states, actions)):
            # 越接近游戏结束，奖励越高
            step_reward = reward_per_step * (i + 1) / len(game_states)
            
            # 确定下一个状态
            next_state = game_states[i + 1] if i + 1 < len(game_states) else state
            done = (i + 1 == len(game_states))
            
            # 存储经验
            self.remember(state, action, step_reward, next_state, done)
        
        # 进行学习
        loss = self.replay()
        if loss is not None:
            print(f"🤖 RL学习完成 - 损失: {loss:.4f}, 探索率: {self.epsilon:.3f}")
    
    def _calculate_game_reward(self, game_outcome: Dict[str, Any]) -> float:
        """计算游戏总奖励"""
        reward = 0.0
        
        # 生存时间奖励
        survival_time = game_outcome.get('survival_time', 0)
        reward += min(survival_time / 60.0, 1.0) * 20
        
        # 击杀奖励
        enemies_killed = game_outcome.get('enemies_killed', 0)
        reward += min(enemies_killed / 20.0, 1.0) * 15
        
        # 分数奖励
        score = game_outcome.get('score', 0)
        reward += min(score / 1000.0, 1.0) * 10
        
        # 惩罚项
        damage_taken = game_outcome.get('damage_taken', 0)
        reward -= min(damage_taken / 100.0, 1.0) * 5
        
        return reward
    
    def save_model(self, model_path: str):
        """保存模型"""
        torch.save({
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'step_count': self.step_count,
        }, model_path)
        print(f"✅ RL模型已保存到: {model_path}")
    
    def load_model(self, model_path: str):
        """加载模型"""
        checkpoint = torch.load(model_path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint.get('epsilon', self.epsilon)
        self.step_count = checkpoint.get('step_count', self.step_count)
        print(f"✅ RL模型已从 {model_path} 加载")

# 使用示例
if __name__ == "__main__":
    # 创建RL游戏AI
    rl_ai = RLGameAI()
    
    # 模拟游戏过程
    game_states = []
    actions = []
    
    # 模拟几个游戏状态
    for i in range(10):
        game_state = {
            'player_health': 100 - i * 5,
            'player_score': i * 100,
            'enemies_killed': i * 2,
            'survival_time': i * 10,
            'player_position': {'x': 400, 'y': 300},
            'enemies': [{'speed': 3, 'health': 2}] * (5 + i),
            'power_ups': [{'type': 'health'}] * (2 - i // 5),
            'ai_difficulty': 1.0 + i * 0.1,
            'player_performance': 0.8 - i * 0.05,
            'frame_count': i * 60
        }
        game_states.append(game_state)
        
        # 选择动作
        action = rl_ai.select_action(game_state)
        actions.append(action)
        
        print(f"步骤 {i}: 动作 {action} -> {rl_ai.decode_action(action)}")
    
    # 模拟游戏结果
    game_outcome = {
        'survival_time': 100,
        'enemies_killed': 20,
        'score': 1000,
        'damage_taken': 50
    }
    
    # 学习
    rl_ai.learn_from_game(game_states, actions, game_outcome)
    
    # 保存模型
    rl_ai.save_model('./models/rl_game_ai.pth')
