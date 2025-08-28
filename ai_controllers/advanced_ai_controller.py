#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级AI飞机控制器 - 与新的AI系统协同工作
"""

import numpy as np
import pygame
import random
import time
from typing import Dict, List, Any, Tuple
from collections import deque

class AdvancedAIController:
    """高级AI飞机控制器 - 能够学习和适应游戏模式"""
    
    def __init__(self):
        # 学习参数
        self.learning_rate = 0.01
        self.exploration_rate = 0.3
        self.memory_size = 1000
        
        # 经验回放
        self.experience_memory = deque(maxlen=self.memory_size)
        
        # 性能统计
        self.performance_stats = {
            'total_games': 0,
            'total_score': 0,
            'total_survival_time': 0,
            'total_enemies_killed': 0,
            'learning_progress': []
        }
        
        # 当前游戏状态
        self.current_game_state = {}
        self.last_action = None
        self.last_reward = 0
        
        # 学习历史
        self.action_history = []
        self.state_history = []
        self.reward_history = []
        
        # 适应参数
        self.adaptation_speed = 0.1
        self.strategy_confidence = 0.5
        
        print("🤖 高级AI控制器初始化完成")
    
    def get_action(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """根据游戏状态获取动作"""
        # 记录状态
        self.current_game_state = game_state
        self.state_history.append(game_state.copy())
        
        # 分析游戏状态
        action = self._analyze_and_decide(game_state)
        
        # 记录动作
        self.last_action = action
        self.action_history.append(action.copy())
        
        return action
    
    def _analyze_and_decide(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """分析游戏状态并做出决策"""
        # 提取关键信息
        player_health = game_state.get('player_health', 100)
        player_position = game_state.get('player_position', {'x': 400, 'y': 300})
        enemies = game_state.get('enemies', [])
        bullets = game_state.get('bullets', [])
        power_ups = game_state.get('power_ups', [])
        
        # 计算威胁等级
        threat_level = self._calculate_threat_level(enemies, bullets, player_position)
        
        # 计算机会等级
        opportunity_level = self._calculate_opportunity_level(power_ups, enemies, player_position)
        
        # 基于状态选择策略
        if player_health < 30:
            # 低生命值：防御策略
            strategy = 'defensive'
        elif threat_level > 0.7:
            # 高威胁：躲避策略
            strategy = 'evasive'
        elif opportunity_level > 0.6:
            # 高机会：攻击策略
            strategy = 'aggressive'
        else:
            # 平衡策略
            strategy = 'balanced'
        
        # 执行策略
        action = self._execute_strategy(strategy, game_state)
        
        return action
    
    def _calculate_threat_level(self, enemies: List, bullets: List, player_pos: Dict) -> float:
        """计算威胁等级"""
        threat_score = 0.0
        
        # 敌机威胁
        for enemy in enemies:
            distance = self._calculate_distance(player_pos, enemy.get('position', {'x': 0, 'y': 0}))
            speed = enemy.get('speed', 1)
            health = enemy.get('health', 1)
            
            # 距离越近，速度越快，生命值越高，威胁越大
            threat_score += (1.0 / max(distance, 1)) * speed * health * 0.1
        
        # 子弹威胁
        for bullet in bullets:
            if bullet.get('type') == 'enemy':
                distance = self._calculate_distance(player_pos, bullet.get('position', {'x': 0, 'y': 0}))
                speed = bullet.get('speed', 1)
                
                threat_score += (1.0 / max(distance, 1)) * speed * 0.2
        
        return min(threat_score, 1.0)
    
    def _calculate_opportunity_level(self, power_ups: List, enemies: List, player_pos: Dict) -> float:
        """计算机会等级"""
        opportunity_score = 0.0
        
        # 道具机会
        for power_up in power_ups:
            distance = self._calculate_distance(player_pos, power_up.get('position', {'x': 0, 'y': 0}))
            value = power_up.get('value', 1)
            
            opportunity_score += (1.0 / max(distance, 1)) * value * 0.3
        
        # 击杀机会
        for enemy in enemies:
            distance = self._calculate_distance(player_pos, enemy.get('position', {'x': 0, 'y': 0}))
            health = enemy.get('health', 1)
            
            # 距离越近，生命值越低，机会越大
            opportunity_score += (1.0 / max(distance, 1)) * (1.0 / max(health, 1)) * 0.2
        
        return min(opportunity_score, 1.0)
    
    def _execute_strategy(self, strategy: str, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行特定策略"""
        player_position = game_state.get('player_position', {'x': 400, 'y': 300})
        enemies = game_state.get('enemies', [])
        power_ups = game_state.get('power_ups', [])
        
        if strategy == 'defensive':
            # 防御策略：远离威胁，寻找安全区域
            action = self._defensive_strategy(player_position, enemies)
        elif strategy == 'evasive':
            # 躲避策略：快速移动，避开威胁
            action = self._evasive_strategy(player_position, enemies, game_state.get('bullets', []))
        elif strategy == 'aggressive':
            # 攻击策略：主动出击，收集道具
            action = self._aggressive_strategy(player_position, enemies, power_ups)
        else:
            # 平衡策略：混合各种行为
            action = self._balanced_strategy(player_position, enemies, power_ups)
        
        return action
    
    def _defensive_strategy(self, player_pos: Dict, enemies: List) -> Dict[str, Any]:
        """防御策略"""
        # 找到最安全的移动方向
        safe_directions = self._find_safe_directions(player_pos, enemies)
        
        # 选择最安全的方向
        best_direction = max(safe_directions, key=lambda x: x['safety_score'])
        
        return {
            'move_x': best_direction['dx'],
            'move_y': best_direction['dy'],
            'shoot': False,
            'special': False,
            'strategy': 'defensive'
        }
    
    def _evasive_strategy(self, player_pos: Dict, enemies: List, bullets: List) -> Dict[str, Any]:
        """躲避策略"""
        # 计算威胁方向
        threat_directions = self._calculate_threat_directions(player_pos, enemies, bullets)
        
        # 选择威胁最小的方向移动
        safe_direction = min(threat_directions, key=lambda x: x['threat_score'])
        
        return {
            'move_x': safe_direction['dx'],
            'move_y': safe_direction['dy'],
            'shoot': False,
            'special': False,
            'strategy': 'evasive'
        }
    
    def _aggressive_strategy(self, player_pos: Dict, enemies: List, power_ups: List) -> Dict[str, Any]:
        """攻击策略"""
        # 找到最近的敌人或道具
        targets = enemies + power_ups
        if not targets:
            return {'move_x': 0, 'move_y': 0, 'shoot': False, 'special': False, 'strategy': 'aggressive'}
        
        # 选择最近的目标
        nearest_target = min(targets, key=lambda x: self._calculate_distance(player_pos, x.get('position', {'x': 0, 'y': 0})))
        
        # 计算移动方向
        target_pos = nearest_target.get('position', {'x': 0, 'y': 0})
        dx = (target_pos['x'] - player_pos['x']) / max(abs(target_pos['x'] - player_pos['x']), 1)
        dy = (target_pos['y'] - player_pos['y']) / max(abs(target_pos['y'] - player_pos['y']), 1)
        
        return {
            'move_x': dx,
            'move_y': dy,
            'shoot': True,
            'special': True,
            'strategy': 'aggressive'
        }
    
    def _balanced_strategy(self, player_pos: Dict, enemies: List, power_ups: List) -> Dict[str, Any]:
        """平衡策略"""
        # 混合各种策略
        if random.random() < 0.4:
            return self._defensive_strategy(player_pos, enemies)
        elif random.random() < 0.7:
            return self._evasive_strategy(player_pos, enemies, [])
        else:
            return self._aggressive_strategy(player_pos, enemies, power_ups)
    
    def _find_safe_directions(self, player_pos: Dict, enemies: List) -> List[Dict]:
        """找到安全的移动方向"""
        directions = [
            {'dx': 0, 'dy': -1, 'safety_score': 0},   # 上
            {'dx': 0, 'dy': 1, 'safety_score': 0},    # 下
            {'dx': -1, 'dy': 0, 'safety_score': 0},   # 左
            {'dx': 1, 'dy': 0, 'safety_score': 0},    # 右
            {'dx': -1, 'dy': -1, 'safety_score': 0},  # 左上
            {'dx': 1, 'dy': -1, 'safety_score': 0},   # 右上
            {'dx': -1, 'dy': 1, 'safety_score': 0},   # 左下
            {'dx': 1, 'dy': 1, 'safety_score': 0},    # 右下
        ]
        
        # 计算每个方向的安全性
        for direction in directions:
            safety_score = 0
            
            # 检查移动后的位置是否安全
            new_x = player_pos['x'] + direction['dx'] * 50
            new_y = player_pos['y'] + direction['dy'] * 50
            
            # 边界检查
            if 0 <= new_x <= 800 and 0 <= new_y <= 600:
                safety_score += 0.5
                
                # 检查与敌人的距离
                for enemy in enemies:
                    enemy_pos = enemy.get('position', {'x': 0, 'y': 0})
                    distance = self._calculate_distance({'x': new_x, 'y': new_y}, enemy_pos)
                    if distance > 100:
                        safety_score += 0.1
            
            direction['safety_score'] = safety_score
        
        return directions
    
    def _calculate_threat_directions(self, player_pos: Dict, enemies: List, bullets: List) -> List[Dict]:
        """计算威胁方向"""
        directions = [
            {'dx': 0, 'dy': -1, 'threat_score': 0},   # 上
            {'dx': 0, 'dy': 1, 'threat_score': 0},    # 下
            {'dx': -1, 'dy': 0, 'threat_score': 0},   # 左
            {'dx': 1, 'dy': 0, 'threat_score': 0},    # 右
        ]
        
        # 计算每个方向的威胁
        for direction in directions:
            threat_score = 0
            
            # 检查移动后的位置威胁
            new_x = player_pos['x'] + direction['dx'] * 30
            new_y = player_pos['y'] + direction['dy'] * 30
            
            # 计算威胁
            for enemy in enemies:
                enemy_pos = enemy.get('position', {'x': 0, 'y': 0})
                distance = self._calculate_distance({'x': new_x, 'y': new_y}, enemy_pos)
                if distance < 80:
                    threat_score += 0.3
            
            for bullet in bullets:
                if bullet.get('type') == 'enemy':
                    bullet_pos = bullet.get('position', {'x': 0, 'y': 0})
                    distance = self._calculate_distance({'x': new_x, 'y': new_y}, bullet_pos)
                    if distance < 50:
                        threat_score += 0.5
            
            direction['threat_score'] = threat_score
        
        return directions
    
    def _calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """计算两点间距离"""
        return np.sqrt((pos1['x'] - pos2['x'])**2 + (pos1['y'] - pos2['y'])**2)
    
    def learn_from_experience(self, game_outcome: Dict[str, Any]):
        """从游戏经验中学习"""
        # 计算奖励
        reward = self._calculate_reward(game_outcome)
        
        # 记录经验
        if len(self.state_history) > 0 and self.last_action:
            experience = {
                'state': self.state_history[-1],
                'action': self.last_action,
                'reward': reward,
                'outcome': game_outcome
            }
            self.experience_memory.append(experience)
        
        # 更新性能统计
        self._update_performance_stats(game_outcome)
        
        # 学习改进
        self._learn_and_improve()
        
        # 清空当前游戏历史
        self.action_history = []
        self.state_history = []
        self.reward_history = []
    
    def _calculate_reward(self, game_outcome: Dict[str, Any]) -> float:
        """计算游戏奖励"""
        reward = 0.0
        
        # 生存时间奖励
        survival_time = game_outcome.get('survival_time', 0)
        reward += min(survival_time / 60.0, 1.0) * 10
        
        # 击杀奖励
        enemies_killed = game_outcome.get('enemies_killed', 0)
        reward += min(enemies_killed / 20.0, 1.0) * 5
        
        # 分数奖励
        score = game_outcome.get('score', 0)
        reward += min(score / 1000.0, 1.0) * 3
        
        # 惩罚项
        damage_taken = game_outcome.get('damage_taken', 0)
        reward -= min(damage_taken / 100.0, 1.0) * 2
        
        return reward
    
    def _update_performance_stats(self, game_outcome: Dict[str, Any]):
        """更新性能统计"""
        self.performance_stats['total_games'] += 1
        self.performance_stats['total_score'] += game_outcome.get('score', 0)
        self.performance_stats['total_survival_time'] += game_outcome.get('survival_time', 0)
        self.performance_stats['total_enemies_killed'] += game_outcome.get('enemies_killed', 0)
        
        # 计算平均性能
        avg_score = self.performance_stats['total_score'] / self.performance_stats['total_games']
        avg_survival = self.performance_stats['total_survival_time'] / self.performance_stats['total_games']
        avg_kills = self.performance_stats['total_enemies_killed'] / self.performance_stats['total_games']
        
        # 记录学习进度
        self.performance_stats['learning_progress'].append({
            'game': self.performance_stats['total_games'],
            'avg_score': avg_score,
            'avg_survival': avg_survival,
            'avg_kills': avg_kills,
            'timestamp': time.time()
        })
    
    def _learn_and_improve(self):
        """学习和改进"""
        if len(self.experience_memory) < 10:
            return
        
        # 分析最近的经验
        recent_experiences = list(self.experience_memory)[-10:]
        
        # 计算平均奖励
        avg_reward = np.mean([exp['reward'] for exp in recent_experiences])
        
        # 调整策略参数
        if avg_reward > 5.0:
            # 表现好，增加探索
            self.exploration_rate = min(0.5, self.exploration_rate + 0.05)
            self.strategy_confidence = min(0.9, self.strategy_confidence + 0.05)
        elif avg_reward < 2.0:
            # 表现差，减少探索，增加保守
            self.exploration_rate = max(0.1, self.exploration_rate - 0.05)
            self.strategy_confidence = max(0.3, self.strategy_confidence - 0.05)
        
        # 调整学习率
        if len(self.performance_stats['learning_progress']) > 5:
            recent_progress = self.performance_stats['learning_progress'][-5:]
            if recent_progress[-1]['avg_score'] < recent_progress[0]['avg_score']:
                # 性能下降，增加学习率
                self.learning_rate = min(0.05, self.learning_rate + 0.005)
            else:
                # 性能提升，减少学习率
                self.learning_rate = max(0.001, self.learning_rate - 0.001)
        
        print(f"🤖 AI学习完成 - 平均奖励: {avg_reward:.2f}, 探索率: {self.exploration_rate:.2f}, 策略置信度: {self.strategy_confidence:.2f}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        if self.performance_stats['total_games'] == 0:
            return {"error": "还没有游戏数据"}
        
        avg_score = self.performance_stats['total_score'] / self.performance_stats['total_games']
        avg_survival = self.performance_stats['total_survival_time'] / self.performance_stats['total_games']
        avg_kills = self.performance_stats['total_enemies_killed'] / self.performance_stats['total_games']
        
        return {
            'total_games': self.performance_stats['total_games'],
            'average_score': avg_score,
            'average_survival_time': avg_survival,
            'average_enemies_killed': avg_kills,
            'exploration_rate': self.exploration_rate,
            'strategy_confidence': self.strategy_confidence,
            'learning_rate': self.learning_rate,
            'experience_memory_size': len(self.experience_memory),
            'learning_progress': self.performance_stats['learning_progress'][-10:] if self.performance_stats['learning_progress'] else []
        }
    
    def reset_learning(self):
        """重置学习状态"""
        self.experience_memory.clear()
        self.action_history = []
        self.state_history = []
        self.reward_history = []
        self.performance_stats['learning_progress'] = []
        self.exploration_rate = 0.3
        self.strategy_confidence = 0.5
        self.learning_rate = 0.01
        print("🔄 AI学习状态已重置")

# 使用示例
if __name__ == "__main__":
    # 创建AI控制器
    ai_controller = AdvancedAIController()
    
    # 模拟游戏状态
    game_state = {
        'player_health': 75,
        'player_position': {'x': 400, 'y': 300},
        'enemies': [
            {'position': {'x': 200, 'y': 100}, 'speed': 3, 'health': 2},
            {'position': {'x': 600, 'y': 200}, 'speed': 2, 'health': 1}
        ],
        'bullets': [
            {'position': {'x': 350, 'y': 250}, 'type': 'enemy', 'speed': 5}
        ],
        'power_ups': [
            {'position': {'x': 450, 'y': 350}, 'type': 'health', 'value': 2}
        ]
    }
    
    # 获取AI动作
    action = ai_controller.get_action(game_state)
    print(f"🤖 AI动作: {action}")
    
    # 模拟游戏结果
    game_outcome = {
        'survival_time': 67,
        'enemies_killed': 18,
        'score': 720,
        'damage_taken': 45
    }
    
    # 学习
    ai_controller.learn_from_experience(game_outcome)
    
    # 获取性能报告
    report = ai_controller.get_performance_report()
    print(f"📊 性能报告: {report}")
