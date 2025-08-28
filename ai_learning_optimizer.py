#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI学习和优化系统 - 真正的学习和优化能力
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import time
import json
import os
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt

@dataclass
class LearningExperience:
    """学习经验"""
    state: Dict[str, Any]
    action: Dict[str, Any]
    reward: float
    next_state: Dict[str, Any]
    outcome: Dict[str, Any]
    timestamp: float
    session_id: str

@dataclass
class OptimizationResult:
    """优化结果"""
    parameter_name: str
    old_value: Any
    new_value: Any
    improvement: float
    confidence: float
    reasoning: str

class MetaLearningNetwork(nn.Module):
    """元学习网络 - 学习如何学习"""
    
    def __init__(self, input_size=100, hidden_size=256, output_size=50):
        super(MetaLearningNetwork, self).__init__()
        self.meta_learner = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, output_size),
            nn.Tanh()
        )
        
        # 学习率预测器
        self.lr_predictor = nn.Sequential(
            nn.Linear(output_size, hidden_size // 4),
            nn.ReLU(),
            nn.Linear(hidden_size // 4, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        meta_features = self.meta_learner(x)
        learning_rate = self.lr_predictor(meta_features)
        return meta_features, learning_rate

class AdaptiveOptimizer:
    """自适应优化器 - 根据学习效果调整优化策略"""
    
    def __init__(self):
        self.optimization_history = deque(maxlen=1000)
        self.performance_metrics = {
            'learning_rate': [],
            'convergence_speed': [],
            'final_performance': [],
            'stability': []
        }
        
        # 优化策略
        self.optimization_strategies = {
            'gradient_descent': self._gradient_descent_optimization,
            'genetic_algorithm': self._genetic_optimization,
            'bayesian_optimization': self._bayesian_optimization,
            'reinforcement_learning': self._rl_optimization
        }
        
        self.current_strategy = 'gradient_descent'
        self.strategy_performance = {k: 0.0 for k in self.optimization_strategies.keys()}
    
    def optimize_parameters(self, model, loss_function, data, **kwargs):
        """优化模型参数"""
        strategy = self.optimization_strategies[self.current_strategy]
        result = strategy(model, loss_function, data, **kwargs)
        
        # 记录优化历史
        self.optimization_history.append(result)
        
        # 更新策略性能
        self._update_strategy_performance(result)
        
        # 自适应选择策略
        self._adapt_strategy()
        
        return result
    
    def _gradient_descent_optimization(self, model, loss_function, data, **kwargs):
        """梯度下降优化"""
        optimizer = optim.Adam(model.parameters(), lr=kwargs.get('lr', 0.001))
        
        losses = []
        for epoch in range(kwargs.get('epochs', 100)):
            optimizer.zero_grad()
            loss = loss_function(model, data)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
            
            if epoch % 20 == 0:
                print(f"📉 梯度下降优化 - Epoch {epoch}, Loss: {loss.item():.4f}")
        
        return {
            'strategy': 'gradient_descent',
            'final_loss': losses[-1],
            'convergence_speed': len(losses),
            'stability': np.std(losses[-10:]) if len(losses) >= 10 else np.std(losses)
        }
    
    def _genetic_optimization(self, model, loss_function, data, **kwargs):
        """遗传算法优化"""
        population_size = kwargs.get('population_size', 50)
        generations = kwargs.get('generations', 100)
        
        # 获取模型参数
        params = list(model.parameters())
        param_shapes = [p.shape for p in params]
        
        # 初始化种群
        population = []
        for _ in range(population_size):
            individual = []
            for param in params:
                individual.append(torch.randn_like(param))
            population.append(individual)
        
        best_fitness = float('inf')
        best_individual = None
        
        for generation in range(generations):
            # 评估适应度
            fitness_scores = []
            for individual in population:
                # 临时设置参数
                for i, param in enumerate(params):
                    param.data = individual[i]
                
                try:
                    loss = loss_function(model, data)
                    fitness_scores.append(loss.item())
                except:
                    fitness_scores.append(float('inf'))
            
            # 选择最佳个体
            best_idx = np.argmin(fitness_scores)
            if fitness_scores[best_idx] < best_fitness:
                best_fitness = fitness_scores[best_idx]
                best_individual = population[best_idx]
            
            # 生成新种群
            new_population = []
            for _ in range(population_size):
                parent1 = population[random.randint(0, population_size-1)]
                parent2 = population[random.randint(0, population_size-1)]
                
                # 交叉
                child = []
                for i in range(len(parent1)):
                    if random.random() < 0.5:
                        child.append(parent1[i].clone())
                    else:
                        child.append(parent2[i].clone())
                
                # 变异
                for i in range(len(child)):
                    if random.random() < 0.1:
                        child[i] += torch.randn_like(child[i]) * 0.1
                
                new_population.append(child)
            
            population = new_population
            
            if generation % 20 == 0:
                print(f"🧬 遗传算法优化 - Generation {generation}, Best Fitness: {best_fitness:.4f}")
        
        # 应用最佳参数
        if best_individual:
            for i, param in enumerate(params):
                param.data = best_individual[i]
        
        return {
            'strategy': 'genetic_algorithm',
            'final_loss': best_fitness,
            'convergence_speed': generations,
            'stability': 0.0  # 遗传算法稳定性难以量化
        }
    
    def _bayesian_optimization(self, model, loss_function, data, **kwargs):
        """贝叶斯优化"""
        # 简化的贝叶斯优化实现
        n_trials = kwargs.get('n_trials', 50)
        
        # 定义参数空间
        param_ranges = {
            'lr': (0.0001, 0.01),
            'batch_size': (16, 128),
            'hidden_size': (64, 512)
        }
        
        best_params = None
        best_loss = float('inf')
        
        for trial in range(n_trials):
            # 随机采样参数
            params = {
                'lr': random.uniform(*param_ranges['lr']),
                'batch_size': random.randint(*param_ranges['batch_size']),
                'hidden_size': random.randint(*param_ranges['hidden_size'])
            }
            
            # 应用参数
            optimizer = optim.Adam(model.parameters(), lr=params['lr'])
            
            # 训练几步
            for _ in range(10):
                optimizer.zero_grad()
                loss = loss_function(model, data)
                loss.backward()
                optimizer.step()
            
            # 评估
            final_loss = loss_function(model, data).item()
            
            if final_loss < best_loss:
                best_loss = final_loss
                best_params = params
            
            if trial % 10 == 0:
                print(f"🔮 贝叶斯优化 - Trial {trial}, Best Loss: {best_loss:.4f}")
        
        return {
            'strategy': 'bayesian_optimization',
            'final_loss': best_loss,
            'convergence_speed': n_trials,
            'stability': 0.0,
            'best_params': best_params
        }
    
    def _rl_optimization(self, model, loss_function, data, **kwargs):
        """强化学习优化"""
        # 简化的强化学习优化
        n_episodes = kwargs.get('n_episodes', 100)
        
        # 定义动作空间（参数调整）
        actions = [
            {'lr': 0.001, 'momentum': 0.9},
            {'lr': 0.01, 'momentum': 0.8},
            {'lr': 0.0001, 'momentum': 0.95},
            {'lr': 0.005, 'momentum': 0.85}
        ]
        
        best_action = None
        best_reward = float('-inf')
        
        for episode in range(n_episodes):
            # 选择动作
            action = random.choice(actions)
            
            # 应用动作
            optimizer = optim.SGD(model.parameters(), lr=action['lr'], momentum=action['momentum'])
            
            # 训练
            episode_losses = []
            for _ in range(20):
                optimizer.zero_grad()
                loss = loss_function(model, data)
                loss.backward()
                optimizer.step()
                episode_losses.append(loss.item())
            
            # 计算奖励
            reward = -np.mean(episode_losses[-5:])  # 负损失作为奖励
            
            if reward > best_reward:
                best_reward = reward
                best_action = action
            
            if episode % 20 == 0:
                print(f"🎯 RL优化 - Episode {episode}, Best Reward: {best_reward:.4f}")
        
        return {
            'strategy': 'reinforcement_learning',
            'final_loss': -best_reward,
            'convergence_speed': n_episodes,
            'stability': 0.0,
            'best_action': best_action
        }
    
    def _update_strategy_performance(self, result):
        """更新策略性能"""
        strategy = result['strategy']
        performance = 1.0 / (1.0 + result['final_loss'])  # 损失越小，性能越好
        
        self.strategy_performance[strategy] = 0.9 * self.strategy_performance[strategy] + 0.1 * performance
    
    def _adapt_strategy(self):
        """自适应选择策略"""
        # 选择性能最好的策略
        best_strategy = max(self.strategy_performance.items(), key=lambda x: x[1])[0]
        
        if best_strategy != self.current_strategy:
            print(f"🔄 策略切换: {self.current_strategy} -> {best_strategy}")
            self.current_strategy = best_strategy

class AILearningOptimizer:
    """AI学习和优化系统"""
    
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🧠 AI学习和优化系统使用设备: {self.device}")
        
        # 元学习网络
        self.meta_learner = MetaLearningNetwork().to(self.device)
        self.meta_optimizer = optim.Adam(self.meta_learner.parameters(), lr=0.001)
        
        # 自适应优化器
        self.adaptive_optimizer = AdaptiveOptimizer()
        
        # 学习经验库
        self.experience_database = deque(maxlen=10000)
        self.session_experiences = {}
        
        # 性能跟踪
        self.performance_history = {
            'loss': [],
            'accuracy': [],
            'learning_rate': [],
            'optimization_time': []
        }
        
        # 学习统计
        self.learning_stats = {
            'total_sessions': 0,
            'total_experiences': 0,
            'average_improvement': 0.0,
            'best_performance': float('inf')
        }
        
        # 加载预训练模型
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            print(f"✅ 已加载预训练学习模型: {model_path}")
    
    def learn_from_experience(self, experience: LearningExperience):
        """从经验中学习"""
        # 存储经验
        self.experience_database.append(experience)
        
        # 按会话分组
        if experience.session_id not in self.session_experiences:
            self.session_experiences[experience.session_id] = []
        self.session_experiences[experience.session_id].append(experience)
        
        # 更新统计
        self.learning_stats['total_experiences'] += 1
        
        # 如果经验足够，进行元学习
        if len(self.experience_database) >= 100:
            self._meta_learn()
    
    def _meta_learn(self):
        """元学习 - 学习如何学习"""
        print("🧠 开始元学习...")
        
        # 准备训练数据
        batch_size = min(32, len(self.experience_database))
        batch = random.sample(self.experience_database, batch_size)
        
        # 编码经验
        experience_features = []
        learning_targets = []
        
        for exp in batch:
            # 提取特征
            features = self._encode_experience(exp)
            experience_features.append(features)
            
            # 学习目标（奖励）
            learning_targets.append(exp.reward)
        
        # 转换为张量
        experience_features = torch.stack(experience_features).to(self.device)
        learning_targets = torch.FloatTensor(learning_targets).to(self.device)
        
        # 元学习训练
        self.meta_optimizer.zero_grad()
        meta_features, predicted_lr = self.meta_learner(experience_features)
        
        # 计算损失
        meta_loss = nn.MSELoss()(meta_features.mean(dim=0), learning_targets.mean().expand(meta_features.size(1)))
        lr_loss = nn.MSELoss()(predicted_lr.squeeze(), torch.ones_like(predicted_lr.squeeze()) * 0.001)
        
        total_loss = meta_loss + 0.1 * lr_loss
        total_loss.backward()
        self.meta_optimizer.step()
        
        print(f"🧠 元学习完成 - 元损失: {meta_loss.item():.4f}, LR损失: {lr_loss.item():.4f}")
    
    def _encode_experience(self, experience: LearningExperience) -> torch.Tensor:
        """编码学习经验"""
        features = []
        
        # 状态特征
        state = experience.state
        features.extend([
            state.get('player_health', 100) / 100.0,
            state.get('player_score', 0) / 1000.0,
            state.get('enemies_killed', 0) / 50.0,
            state.get('survival_time', 0) / 300.0,
        ])
        
        # 动作特征
        action = experience.action
        features.extend([
            hash(str(action.get('type', ''))) % 100 / 100.0,
            action.get('wave_count', 5) / 10.0,
            action.get('enemies_per_wave', 10) / 20.0,
            action.get('enemy_speed', 3) / 5.0,
        ])
        
        # 结果特征
        outcome = experience.outcome
        features.extend([
            outcome.get('player_survived', True),
            outcome.get('enemies_killed', 0) / 20.0,
            outcome.get('player_damage_taken', 0) / 100.0,
            outcome.get('game_duration', 0) / 300.0,
        ])
        
        # 时间特征
        features.extend([
            experience.timestamp % 86400 / 86400.0,  # 一天内的时间
            (time.time() - experience.timestamp) / 3600.0,  # 经验年龄（小时）
        ])
        
        # 填充到固定长度
        while len(features) < 100:
            features.append(0.0)
        
        return torch.FloatTensor(features[:100])
    
    def optimize_game_parameters(self, current_params: Dict[str, Any], 
                               performance_metrics: Dict[str, Any]) -> OptimizationResult:
        """优化游戏参数"""
        print("🔧 开始参数优化...")
        
        # 分析当前性能
        current_performance = self._evaluate_performance(performance_metrics)
        
        # 生成优化建议
        optimization_suggestions = self._generate_optimization_suggestions(
            current_params, performance_metrics
        )
        
        # 选择最佳优化
        best_optimization = max(optimization_suggestions, key=lambda x: x['expected_improvement'])
        
        # 应用优化
        param_name = best_optimization['parameter']
        old_value = current_params.get(param_name)
        new_value = best_optimization['new_value']
        
        # 创建优化结果
        result = OptimizationResult(
            parameter_name=param_name,
            old_value=old_value,
            new_value=new_value,
            improvement=best_optimization['expected_improvement'],
            confidence=best_optimization['confidence'],
            reasoning=best_optimization['reasoning']
        )
        
        print(f"🔧 参数优化完成: {param_name} = {old_value} -> {new_value}")
        print(f"   预期改进: {best_optimization['expected_improvement']:.2f}")
        print(f"   置信度: {best_optimization['confidence']:.2f}")
        
        return result
    
    def _evaluate_performance(self, metrics: Dict[str, Any]) -> float:
        """评估性能"""
        performance = 0.0
        
        # 生存时间
        survival_time = metrics.get('survival_time', 0)
        performance += min(survival_time / 60.0, 1.0) * 0.3
        
        # 击杀效率
        enemies_killed = metrics.get('enemies_killed', 0)
        performance += min(enemies_killed / 20.0, 1.0) * 0.3
        
        # 分数
        score = metrics.get('score', 0)
        performance += min(score / 1000.0, 1.0) * 0.2
        
        # 伤害控制
        damage_taken = metrics.get('damage_taken', 0)
        performance += max(0, 1.0 - damage_taken / 100.0) * 0.2
        
        return performance
    
    def _generate_optimization_suggestions(self, current_params: Dict[str, Any], 
                                        performance_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []
        
        # 基于性能分析生成建议
        performance = self._evaluate_performance(performance_metrics)
        
        if performance < 0.3:
            # 性能差，降低难度
            suggestions.extend([
                {
                    'parameter': 'enemy_speed',
                    'new_value': max(1, current_params.get('enemy_speed', 3) - 1),
                    'expected_improvement': 0.2,
                    'confidence': 0.8,
                    'reasoning': '玩家表现不佳，降低敌机速度'
                },
                {
                    'parameter': 'enemy_health',
                    'new_value': max(1, current_params.get('enemy_health', 3) - 1),
                    'expected_improvement': 0.15,
                    'confidence': 0.7,
                    'reasoning': '减少敌机生命值，降低难度'
                }
            ])
        elif performance > 0.8:
            # 性能好，增加挑战
            suggestions.extend([
                {
                    'parameter': 'enemy_speed',
                    'new_value': min(5, current_params.get('enemy_speed', 3) + 1),
                    'expected_improvement': 0.1,
                    'confidence': 0.6,
                    'reasoning': '玩家表现优秀，增加挑战性'
                },
                {
                    'parameter': 'enemy_count',
                    'new_value': min(50, current_params.get('enemy_count', 30) + 10),
                    'expected_improvement': 0.1,
                    'confidence': 0.6,
                    'reasoning': '增加敌机数量，测试玩家极限'
                }
            ])
        else:
            # 性能一般，微调
            suggestions.extend([
                {
                    'parameter': 'wave_delay',
                    'new_value': current_params.get('wave_delay', 3.0) * 0.9,
                    'expected_improvement': 0.05,
                    'confidence': 0.5,
                    'reasoning': '微调敌机生成间隔，优化节奏'
                }
            ])
        
        return suggestions
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """获取学习洞察"""
        insights = {
            'learning_stats': self.learning_stats,
            'performance_history': self.performance_history,
            'strategy_performance': self.adaptive_optimizer.strategy_performance,
            'current_strategy': self.adaptive_optimizer.current_strategy,
            'experience_diversity': len(set(exp.session_id for exp in self.experience_database)),
            'recent_improvements': self._calculate_recent_improvements()
        }
        
        return insights
    
    def _calculate_recent_improvements(self) -> List[float]:
        """计算最近的改进"""
        if len(self.performance_history['loss']) < 2:
            return []
        
        recent_losses = self.performance_history['loss'][-10:]
        improvements = []
        
        for i in range(1, len(recent_losses)):
            improvement = recent_losses[i-1] - recent_losses[i]
            improvements.append(improvement)
        
        return improvements
    
    def save_model(self, model_path: str):
        """保存模型"""
        torch.save({
            'meta_learner': self.meta_learner.state_dict(),
            'meta_optimizer': self.meta_optimizer.state_dict(),
        }, model_path)
        print(f"✅ 学习模型已保存到: {model_path}")
    
    def load_model(self, model_path: str):
        """加载模型"""
        checkpoint = torch.load(model_path, map_location=self.device)
        self.meta_learner.load_state_dict(checkpoint['meta_learner'])
        self.meta_optimizer.load_state_dict(checkpoint['meta_optimizer'])
        print(f"✅ 学习模型已从 {model_path} 加载")

# 使用示例
if __name__ == "__main__":
    # 创建AI学习和优化系统
    ailo = AILearningOptimizer()
    
    # 模拟学习经验
    experience = LearningExperience(
        state={'player_health': 75, 'player_score': 450, 'enemies_killed': 12, 'survival_time': 45},
        action={'type': 'wave', 'wave_count': 5, 'enemies_per_wave': 8, 'enemy_speed': 3},
        reward=0.7,
        next_state={'player_health': 70, 'player_score': 520, 'enemies_killed': 15, 'survival_time': 52},
        outcome={'player_survived': True, 'enemies_killed': 15, 'player_damage_taken': 45, 'game_duration': 52},
        timestamp=time.time(),
        session_id='session_001'
    )
    
    # 学习
    ailo.learn_from_experience(experience)
    
    # 优化参数
    current_params = {'enemy_speed': 3, 'enemy_health': 3, 'enemy_count': 30, 'wave_delay': 3.0}
    performance_metrics = {'survival_time': 45, 'enemies_killed': 12, 'score': 450, 'damage_taken': 55}
    
    optimization_result = ailo.optimize_game_parameters(current_params, performance_metrics)
    print(f"🔧 优化结果: {optimization_result}")
    
    # 获取学习洞察
    insights = ailo.get_learning_insights()
    print(f"📊 学习洞察: {insights}")
    
    # 保存模型
    ailo.save_model('./models/ai_learning_optimizer.pth')
