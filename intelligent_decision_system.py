#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能决策系统 - 分析游戏状态并做出智能决策
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import os

@dataclass
class GameContext:
    """游戏上下文信息"""
    player_health: float
    player_score: int
    enemies_killed: int
    survival_time: float
    enemy_density: float
    power_up_availability: float
    player_performance: float
    current_difficulty: float
    frame_count: int
    last_action_time: float

@dataclass
class DecisionResult:
    """决策结果"""
    action_type: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str
    expected_outcome: str

class ContextAnalyzer(nn.Module):
    """上下文分析器 - 分析游戏状态并提取关键信息"""
    
    def __init__(self, input_size=50, hidden_size=128, context_size=32):
        super(ContextAnalyzer, self).__init__()
        self.analyzer = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, context_size),
            nn.Tanh()
        )
        
        # 注意力机制
        self.attention = nn.MultiheadAttention(context_size, num_heads=4, batch_first=True)
        
    def forward(self, x):
        features = self.analyzer(x)
        # 应用注意力机制
        attended_features, _ = self.attention(features.unsqueeze(0), 
                                           features.unsqueeze(0), 
                                           features.unsqueeze(0))
        return attended_features.squeeze(0)

class DecisionNetwork(nn.Module):
    """决策网络 - 根据上下文生成决策"""
    
    def __init__(self, context_size=32, hidden_size=64, decision_size=20):
        super(DecisionNetwork, self).__init__()
        self.decision_maker = nn.Sequential(
            nn.Linear(context_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, decision_size),
            nn.Softmax(dim=-1)
        )
        
    def forward(self, context):
        return self.decision_maker(context)

class IntelligentDecisionSystem:
    """智能决策系统"""
    
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🧠 智能决策系统使用设备: {self.device}")
        
        # 神经网络模型
        self.context_analyzer = ContextAnalyzer().to(self.device)
        self.decision_network = DecisionNetwork().to(self.device)
        
        # 优化器
        self.analyzer_optimizer = optim.Adam(self.context_analyzer.parameters(), lr=0.001)
        self.decision_optimizer = optim.Adam(self.decision_network.parameters(), lr=0.001)
        
        # 决策历史
        self.decision_history = deque(maxlen=1000)
        self.context_history = deque(maxlen=1000)
        
        # 决策策略
        self.decision_strategies = {
            'aggressive': self._aggressive_strategy,
            'defensive': self._defensive_strategy,
            'balanced': self._balanced_strategy,
            'adaptive': self._adaptive_strategy,
            'chaotic': self._chaotic_strategy
        }
        
        # 当前策略
        self.current_strategy = 'adaptive'
        self.strategy_confidence = 0.8
        
        # 加载预训练模型
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            print(f"✅ 已加载预训练决策模型: {model_path}")
    
    def analyze_game_context(self, game_state: Dict[str, Any]) -> GameContext:
        """分析游戏状态，提取上下文信息"""
        # 计算敌机密度
        enemies = game_state.get('enemies', [])
        screen_area = 800 * 600  # 假设屏幕大小
        enemy_area = sum(e.get('size', 50) ** 2 for e in enemies)
        enemy_density = enemy_area / screen_area
        
        # 计算道具可用性
        power_ups = game_state.get('power_ups', [])
        power_up_availability = len(power_ups) / 10.0  # 归一化
        
        # 计算玩家表现
        player_performance = self._calculate_player_performance(game_state)
        
        context = GameContext(
            player_health=game_state.get('player_health', 100) / 100.0,
            player_score=game_state.get('player_score', 0),
            enemies_killed=game_state.get('enemies_killed', 0),
            survival_time=game_state.get('survival_time', 0),
            enemy_density=enemy_density,
            power_up_availability=power_up_availability,
            player_performance=player_performance,
            current_difficulty=game_state.get('ai_difficulty', 1.0),
            frame_count=game_state.get('frame_count', 0),
            last_action_time=time.time()
        )
        
        return context
    
    def _calculate_player_performance(self, game_state: Dict[str, Any]) -> float:
        """计算玩家表现分数"""
        performance = 0.5  # 基础分数
        
        # 生存时间奖励
        survival_time = game_state.get('survival_time', 0)
        if survival_time > 60:
            performance += 0.2
        elif survival_time > 30:
            performance += 0.1
        
        # 击杀效率奖励
        enemies_killed = game_state.get('enemies_killed', 0)
        if enemies_killed > 20:
            performance += 0.2
        elif enemies_killed > 10:
            performance += 0.1
        
        # 生命值奖励
        player_health = game_state.get('player_health', 100)
        if player_health > 80:
            performance += 0.1
        
        return min(performance, 1.0)
    
    def make_intelligent_decision(self, game_state: Dict[str, Any]) -> DecisionResult:
        """做出智能决策"""
        # 分析游戏上下文
        context = self.analyze_game_context(game_state)
        
        # 选择决策策略
        strategy_name = self._select_strategy(context)
        
        # 执行策略
        strategy_func = self.decision_strategies[strategy_name]
        decision = strategy_func(context)
        
        # 记录决策历史
        self.decision_history.append(decision)
        self.context_history.append(context)
        
        # 更新策略置信度
        self._update_strategy_confidence(context, decision)
        
        return decision
    
    def _select_strategy(self, context: GameContext) -> str:
        """根据上下文选择决策策略"""
        # 基于玩家表现选择策略
        if context.player_performance > 0.8:
            # 玩家表现好，使用更具挑战性的策略
            if context.enemy_density < 0.3:
                return 'aggressive'
            else:
                return 'chaotic'
        elif context.player_performance < 0.3:
            # 玩家表现差，使用防御性策略
            return 'defensive'
        else:
            # 玩家表现一般，使用平衡策略
            return 'balanced'
    
    def _aggressive_strategy(self, context: GameContext) -> DecisionResult:
        """激进策略 - 大量敌机，高难度"""
        return DecisionResult(
            action_type='enemy_spawn',
            parameters={
                'type': 'wave',
                'wave_count': 8,
                'enemies_per_wave': 15,
                'wave_delay': 2.0,
                'enemy_speed': 4,
                'enemy_health': 4,
                'enemy_behavior': 'chase'
            },
            confidence=0.9,
            reasoning='玩家表现优秀，增加挑战性',
            expected_outcome='高难度战斗，测试玩家极限'
        )
    
    def _defensive_strategy(self, context: GameContext) -> DecisionResult:
        """防御策略 - 减少敌机，增加道具"""
        return DecisionResult(
            action_type='enemy_spawn',
            parameters={
                'type': 'formation',
                'formation_type': 'v',
                'formation_size': 3,
                'formation_spacing': 100,
                'enemy_speed': 2,
                'enemy_health': 2,
                'enemy_behavior': 'straight'
            },
            confidence=0.8,
            reasoning='玩家表现不佳，降低难度',
            expected_outcome='轻松战斗，帮助玩家恢复'
        )
    
    def _balanced_strategy(self, context: GameContext) -> DecisionResult:
        """平衡策略 - 中等难度，平衡挑战"""
        return DecisionResult(
            action_type='enemy_spawn',
            parameters={
                'type': 'spiral',
                'spiral_arms': 3,
                'enemies_per_arm': 10,
                'spiral_tightness': 1.0,
                'enemy_speed': 3,
                'enemy_health': 3,
                'enemy_behavior': 'zigzag'
            },
            confidence=0.7,
            reasoning='玩家表现一般，保持平衡',
            expected_outcome='适度挑战，维持游戏平衡'
        )
    
    def _adaptive_strategy(self, context: GameContext) -> DecisionResult:
        """自适应策略 - 根据实时情况调整"""
        # 动态调整参数
        if context.enemy_density > 0.5:
            # 敌机太多，减少生成
            return DecisionResult(
                action_type='enemy_spawn',
                parameters={
                    'type': 'random',
                    'enemy_count': 15,
                    'spawn_interval': 2.0,
                    'enemy_speed': 2,
                    'enemy_health': 2,
                    'enemy_behavior': 'straight'
                },
                confidence=0.8,
                reasoning='敌机密度过高，减少生成',
                expected_outcome='降低敌机密度，平衡游戏'
            )
        else:
            # 敌机不多，增加生成
            return DecisionResult(
                action_type='enemy_spawn',
                parameters={
                    'type': 'wave',
                    'wave_count': 5,
                    'enemies_per_wave': 8,
                    'wave_delay': 3.0,
                    'enemy_speed': 3,
                    'enemy_health': 3,
                    'enemy_behavior': 'circle'
                },
                confidence=0.8,
                reasoning='敌机密度适中，增加挑战',
                expected_outcome='适度增加敌机，维持挑战'
            )
    
    def _chaotic_strategy(self, context: GameContext) -> DecisionResult:
        """混沌策略 - 随机变化，不可预测"""
        strategies = ['wave', 'spiral', 'formation', 'random', 'chaos']
        strategy_type = random.choice(strategies)
        
        if strategy_type == 'wave':
            params = {
                'type': 'wave',
                'wave_count': random.randint(5, 10),
                'enemies_per_wave': random.randint(10, 20),
                'wave_delay': random.uniform(1.5, 4.0),
                'enemy_speed': random.randint(3, 5),
                'enemy_health': random.randint(3, 5),
                'enemy_behavior': random.choice(['chase', 'evade', 'circle'])
            }
        elif strategy_type == 'spiral':
            params = {
                'type': 'spiral',
                'spiral_arms': random.randint(2, 6),
                'enemies_per_arm': random.randint(8, 25),
                'spiral_tightness': random.uniform(0.3, 2.5),
                'enemy_speed': random.randint(2, 5),
                'enemy_health': random.randint(2, 5),
                'enemy_behavior': random.choice(['zigzag', 'circle', 'chase'])
            }
        else:
            params = {
                'type': strategy_type,
                'enemy_count': random.randint(20, 60),
                'spawn_interval': random.uniform(0.5, 3.0),
                'enemy_speed': random.randint(1, 5),
                'enemy_health': random.randint(1, 5),
                'enemy_behavior': random.choice(['straight', 'zigzag', 'circle', 'chase', 'evade'])
            }
        
        return DecisionResult(
            action_type='enemy_spawn',
            parameters=params,
            confidence=0.6,
            reasoning='混沌策略，随机变化',
            expected_outcome='不可预测的游戏体验'
        )
    
    def _update_strategy_confidence(self, context: GameContext, decision: DecisionResult):
        """更新策略置信度"""
        # 基于决策结果的历史表现更新置信度
        if len(self.decision_history) < 10:
            return
        
        # 分析最近10个决策的效果
        recent_decisions = list(self.decision_history)[-10:]
        recent_contexts = list(self.context_history)[-10:]
        
        # 计算策略成功率
        success_count = 0
        for i, (ctx, dec) in enumerate(zip(recent_contexts, recent_decisions)):
            # 简单的成功判断：如果玩家生存时间增加，认为决策成功
            if i > 0 and ctx.survival_time > recent_contexts[i-1].survival_time:
                success_count += 1
        
        success_rate = success_count / 9  # 9个比较
        
        # 更新置信度
        self.strategy_confidence = 0.7 * self.strategy_confidence + 0.3 * success_rate
    
    def learn_from_decision_outcome(self, decision: DecisionResult, 
                                  outcome: Dict[str, Any]):
        """从决策结果中学习"""
        # 计算决策效果
        effectiveness = self._evaluate_decision_effectiveness(decision, outcome)
        
        # 存储学习经验
        experience = {
            'decision': decision,
            'outcome': outcome,
            'effectiveness': effectiveness,
            'timestamp': time.time()
        }
        
        # 这里可以添加更复杂的学习逻辑
        # 比如更新神经网络权重，调整策略参数等
        
        print(f"🧠 决策学习完成 - 效果评分: {effectiveness:.2f}")
    
    def _evaluate_decision_effectiveness(self, decision: DecisionResult, 
                                       outcome: Dict[str, Any]) -> float:
        """评估决策效果"""
        effectiveness = 0.5  # 基础分数
        
        # 基于游戏结果评估
        if outcome.get('player_survived', True):
            effectiveness += 0.2
        
        if outcome.get('enemies_killed', 0) > 10:
            effectiveness += 0.1
        
        if outcome.get('player_damage_taken', 0) < 50:
            effectiveness += 0.1
        
        if outcome.get('game_duration', 0) > 60:
            effectiveness += 0.1
        
        return min(effectiveness, 1.0)
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'current_strategy': self.current_strategy,
            'strategy_confidence': self.strategy_confidence,
            'decision_count': len(self.decision_history),
            'context_count': len(self.context_history),
            'device': str(self.device)
        }
    
    def save_model(self, model_path: str):
        """保存模型"""
        torch.save({
            'context_analyzer': self.context_analyzer.state_dict(),
            'decision_network': self.decision_network.state_dict(),
            'analyzer_optimizer': self.analyzer_optimizer.state_dict(),
            'decision_optimizer': self.decision_optimizer.state_dict(),
        }, model_path)
        print(f"✅ 决策模型已保存到: {model_path}")
    
    def load_model(self, model_path: str):
        """加载模型"""
        checkpoint = torch.load(model_path, map_location=self.device)
        self.context_analyzer.load_state_dict(checkpoint['context_analyzer'])
        self.decision_network.load_state_dict(checkpoint['decision_network'])
        self.analyzer_optimizer.load_state_dict(checkpoint['analyzer_optimizer'])
        self.decision_optimizer.load_state_dict(checkpoint['decision_optimizer'])
        print(f"✅ 决策模型已从 {model_path} 加载")

# 使用示例
if __name__ == "__main__":
    # 创建智能决策系统
    ids = IntelligentDecisionSystem()
    
    # 模拟游戏状态
    game_state = {
        'player_health': 75,
        'player_score': 450,
        'enemies_killed': 12,
        'survival_time': 45,
        'enemies': [{'speed': 3, 'health': 2, 'size': 50}] * 8,
        'power_ups': [{'type': 'health'}] * 2,
        'ai_difficulty': 1.2,
        'frame_count': 2700
    }
    
    # 做出决策
    decision = ids.make_intelligent_decision(game_state)
    print(f"🧠 智能决策: {decision}")
    
    # 模拟游戏结果
    outcome = {
        'player_survived': True,
        'enemies_killed': 18,
        'player_damage_taken': 45,
        'game_duration': 67
    }
    
    # 学习
    ids.learn_from_decision_outcome(decision, outcome)
    
    # 显示系统状态
    status = ids.get_system_status()
    print(f"📊 系统状态: {status}")
    
    # 保存模型
    ids.save_model('./models/intelligent_decision_system.pth')
