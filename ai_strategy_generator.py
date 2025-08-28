#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI策略生成器
使用机器学习和进化算法生成智能游戏策略
"""

import random
import math
import numpy as np
from typing import Dict, List, Tuple, Any, Callable
import json
import time

class AIGameStrategyGenerator:
    """AI游戏策略生成器 - 使用机器学习和进化算法"""
    
    def __init__(self):
        self.seed = random.randint(1, 10000)
        random.seed(self.seed)
        np.random.seed(self.seed)
        
        # 策略参数范围
        self.strategy_params = {
            'aggression': (0.0, 1.0),
            'defense': (0.0, 1.0),
            'speed': (0.5, 2.0),
            'accuracy': (0.3, 1.0),
            'risk_tolerance': (0.0, 1.0),
            'adaptability': (0.1, 1.0),
            'teamwork': (0.0, 1.0),
            'resource_management': (0.0, 1.0)
        }
        
        # 当前策略
        self.current_strategy = {}
        
        # 策略历史记录
        self.strategy_history = []
        
        # 性能评估函数
        self.performance_metrics = {
            'survival_time': 0.0,
            'enemies_killed': 0,
            'damage_taken': 0.0,
            'power_ups_collected': 0,
            'accuracy_rate': 0.0,
            'efficiency_score': 0.0
        }
        
    def generate_initial_strategy(self) -> Dict[str, Any]:
        """生成初始游戏策略"""
        print(f"🧠 AI正在生成初始游戏策略 (种子: {self.seed})...")
        
        strategy = {}
        for param, (min_val, max_val) in self.strategy_params.items():
            strategy[param] = random.uniform(min_val, max_val)
        
        # 添加策略特征
        strategy.update({
            'strategy_id': f"strategy_{self.seed}_{int(time.time())}",
            'generation': 1,
            'fitness_score': 0.0,
            'creation_time': time.time(),
            'tactics': self._generate_tactics(strategy),
            'behavior_patterns': self._generate_behavior_patterns(strategy),
            'resource_allocation': self._generate_resource_allocation(strategy)
        })
        
        self.current_strategy = strategy
        self.strategy_history.append(strategy.copy())
        
        print("✅ 初始AI策略生成完成！")
        return strategy
    
    def _generate_tactics(self, strategy: Dict[str, float]) -> Dict[str, Any]:
        """根据策略参数生成具体战术"""
        aggression = strategy['aggression']
        defense = strategy['defense']
        speed = strategy['speed']
        accuracy = strategy['accuracy']
        
        # 攻击战术
        attack_tactics = []
        if aggression > 0.7:
            attack_tactics.extend(['rush', 'overwhelm', 'focused_fire'])
        elif aggression > 0.4:
            attack_tactics.extend(['balanced_attack', 'opportunistic_strike'])
        else:
            attack_tactics.extend(['defensive_attack', 'counter_attack'])
        
        # 防御战术
        defense_tactics = []
        if defense > 0.7:
            defense_tactics.extend(['evasive_maneuvers', 'shield_management', 'cover_usage'])
        elif defense > 0.4:
            defense_tactics.extend(['balanced_defense', 'situational_defense'])
        else:
            defense_tactics.extend(['minimal_defense', 'aggressive_defense'])
        
        # 移动战术
        movement_tactics = []
        if speed > 1.5:
            movement_tactics.extend(['hit_and_run', 'rapid_positioning', 'escape_routes'])
        elif speed > 1.0:
            movement_tactics.extend(['balanced_movement', 'tactical_positioning'])
        else:
            movement_tactics.extend(['conservative_movement', 'defensive_positioning'])
        
        return {
            'attack': attack_tactics,
            'defense': defense_tactics,
            'movement': movement_tactics,
            'priority': self._calculate_tactic_priority(strategy)
        }
    
    def _generate_behavior_patterns(self, strategy: Dict[str, float]) -> Dict[str, Any]:
        """生成行为模式"""
        adaptability = strategy['adaptability']
        teamwork = strategy['teamwork']
        risk_tolerance = strategy['risk_tolerance']
        
        patterns = {
            'learning_rate': adaptability,
            'adaptation_threshold': 1.0 - adaptability,
            'team_coordination': teamwork > 0.5,
            'risk_assessment': risk_tolerance,
            'decision_making': 'adaptive' if adaptability > 0.7 else 'static',
            'communication': 'team' if teamwork > 0.7 else 'individual'
        }
        
        # 根据策略参数调整行为模式
        if strategy['aggression'] > 0.8:
            patterns['combat_style'] = 'berserker'
        elif strategy['defense'] > 0.8:
            patterns['combat_style'] = 'turtle'
        else:
            patterns['combat_style'] = 'balanced'
        
        return patterns
    
    def _generate_resource_allocation(self, strategy: Dict[str, float]) -> Dict[str, float]:
        """生成资源分配策略"""
        total_points = 100
        allocations = {}
        
        # 根据策略参数分配资源点
        if strategy['aggression'] > 0.7:
            allocations['weapons'] = 40
            allocations['speed'] = 25
            allocations['defense'] = 15
            allocations['utility'] = 20
        elif strategy['defense'] > 0.7:
            allocations['defense'] = 40
            allocations['utility'] = 30
            allocations['weapons'] = 20
            allocations['speed'] = 10
        else:  # 平衡策略
            allocations['weapons'] = 30
            allocations['defense'] = 25
            allocations['speed'] = 25
            allocations['utility'] = 20
        
        return allocations
    
    def _calculate_tactic_priority(self, strategy: Dict[str, float]) -> Dict[str, float]:
        """计算战术优先级"""
        priorities = {}
        
        # 攻击优先级
        if strategy['aggression'] > 0.6:
            priorities['attack'] = 0.8
            priorities['defense'] = 0.2
        else:
            priorities['attack'] = 0.3
            priorities['defense'] = 0.7
        
        # 移动优先级
        if strategy['speed'] > 1.5:
            priorities['movement'] = 0.6
        else:
            priorities['movement'] = 0.3
        
        # 资源管理优先级
        priorities['resource_management'] = strategy['resource_management']
        
        return priorities
    
    def evolve_strategy(self, performance_data: Dict[str, float]) -> Dict[str, Any]:
        """基于性能数据进化策略"""
        if not self.current_strategy:
            return self.generate_initial_strategy()
        
        print("🔄 AI策略正在进化...")
        
        # 计算适应度分数
        fitness_score = self._calculate_fitness(performance_data)
        
        # 更新当前策略的性能
        self.current_strategy['fitness_score'] = fitness_score
        self.current_strategy['last_performance'] = performance_data
        
        # 创建新策略（进化）
        new_strategy = self.current_strategy.copy()
        new_strategy['generation'] += 1
        new_strategy['strategy_id'] = f"strategy_{self.seed}_{int(time.time())}"
        new_strategy['creation_time'] = time.time()
        
        # 根据性能调整策略参数
        self._adjust_strategy_parameters(new_strategy, performance_data)
        
        # 重新生成战术和行为模式
        new_strategy['tactics'] = self._generate_tactics(new_strategy)
        new_strategy['behavior_patterns'] = self._generate_behavior_patterns(new_strategy)
        new_strategy['resource_allocation'] = self._generate_resource_allocation(new_strategy)
        
        # 添加变异
        self._add_mutation(new_strategy)
        
        # 更新策略
        self.current_strategy = new_strategy
        self.strategy_history.append(new_strategy.copy())
        
        print(f"✅ AI策略进化完成！第{new_strategy['generation']}代")
        return new_strategy
    
    def _calculate_fitness(self, performance_data: Dict[str, float]) -> float:
        """计算策略适应度分数"""
        # 权重配置
        weights = {
            'survival_time': 0.3,
            'enemies_killed': 0.25,
            'damage_taken': -0.2,  # 负权重，伤害越少越好
            'power_ups_collected': 0.15,
            'accuracy_rate': 0.1
        }
        
        fitness = 0.0
        for metric, weight in weights.items():
            if metric in performance_data:
                # 标准化性能数据到0-1范围
                normalized_value = min(1.0, performance_data[metric] / 100.0)
                fitness += weight * normalized_value
        
        return max(0.0, min(1.0, fitness))
    
    def _adjust_strategy_parameters(self, strategy: Dict[str, float], performance_data: Dict[str, float]):
        """根据性能数据调整策略参数"""
        # 如果生存时间短，增加防御
        if performance_data.get('survival_time', 0) < 30:
            strategy['defense'] = min(1.0, strategy['defense'] + 0.1)
            strategy['aggression'] = max(0.0, strategy['aggression'] - 0.05)
        
        # 如果击杀数少，增加攻击性
        if performance_data.get('enemies_killed', 0) < 10:
            strategy['aggression'] = min(1.0, strategy['aggression'] + 0.1)
            strategy['accuracy'] = min(1.0, strategy['accuracy'] + 0.05)
        
        # 如果伤害过高，增加防御和速度
        if performance_data.get('damage_taken', 0) > 50:
            strategy['defense'] = min(1.0, strategy['defense'] + 0.15)
            strategy['speed'] = min(2.0, strategy['speed'] + 0.1)
        
        # 如果准确率低，增加准确率
        if performance_data.get('accuracy_rate', 0) < 0.5:
            strategy['accuracy'] = min(1.0, strategy['accuracy'] + 0.1)
            strategy['aggression'] = max(0.0, strategy['aggression'] - 0.05)
    
    def _add_mutation(self, strategy: Dict[str, float]):
        """添加随机变异"""
        mutation_rate = 0.1
        
        for param, (min_val, max_val) in self.strategy_params.items():
            if random.random() < mutation_rate:
                # 添加随机变异
                current_value = strategy[param]
                mutation = random.uniform(-0.1, 0.1)
                new_value = current_value + mutation
                
                # 确保值在有效范围内
                strategy[param] = max(min_val, min(max_val, new_value))
    
    def get_ai_decision(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """根据当前游戏状态生成AI决策"""
        if not self.current_strategy:
            return {}
        
        strategy = self.current_strategy
        decision = {
            'action': self._select_action(game_state, strategy),
            'target': self._select_target(game_state, strategy),
            'movement': self._calculate_movement(game_state, strategy),
            'resource_usage': self._decide_resource_usage(game_state, strategy)
        }
        
        return decision
    
    def _select_action(self, game_state: Dict[str, Any], strategy: Dict[str, float]) -> str:
        """选择行动类型"""
        # 分析游戏状态
        player_health = game_state.get('player_health', 100)
        nearby_enemies = game_state.get('nearby_enemies', 0)
        power_ups_available = game_state.get('power_ups_available', 0)
        
        # 根据策略和状态选择行动
        if player_health < 30 and strategy['defense'] > 0.6:
            return 'defend'
        elif nearby_enemies > 3 and strategy['aggression'] > 0.7:
            return 'attack'
        elif power_ups_available > 0 and strategy['resource_management'] > 0.6:
            return 'collect_power_up'
        elif strategy['aggression'] > 0.5:
            return 'attack'
        else:
            return 'defend'
    
    def _select_target(self, game_state: Dict[str, Any], strategy: Dict[str, float]) -> Dict[str, Any]:
        """选择目标"""
        enemies = game_state.get('enemies', [])
        if not enemies:
            return {}
        
        # 根据策略选择目标
        if strategy['aggression'] > 0.7:
            # 攻击性策略：选择最近或最弱的敌人
            target = min(enemies, key=lambda e: e.get('distance', float('inf')))
        elif strategy['defense'] > 0.7:
            # 防御性策略：选择威胁最大的敌人
            target = max(enemies, key=lambda e: e.get('threat_level', 0))
        else:
            # 平衡策略：随机选择
            target = random.choice(enemies)
        
        return target
    
    def _calculate_movement(self, game_state: Dict[str, Any], strategy: Dict[str, float]) -> Dict[str, float]:
        """计算移动方向和速度"""
        player_pos = game_state.get('player_position', {'x': 400, 'y': 500})
        enemies = game_state.get('enemies', [])
        
        # 计算移动向量
        dx, dy = 0, 0
        
        if strategy['defense'] > 0.6:
            # 防御性移动：远离敌人
            for enemy in enemies:
                enemy_pos = enemy.get('position', {'x': 0, 'y': 0})
                dx += (player_pos['x'] - enemy_pos['x']) * 0.1
                dy += (player_pos['y'] - enemy_pos['y']) * 0.1
        elif strategy['aggression'] > 0.6:
            # 攻击性移动：接近敌人
            if enemies:
                target = min(enemies, key=lambda e: e.get('distance', float('inf')))
                target_pos = target.get('position', {'x': 400, 'y': 100})
                dx = (target_pos['x'] - player_pos['x']) * 0.05
                dy = (target_pos['y'] - player_pos['y']) * 0.05
        
        # 应用速度策略
        speed_multiplier = strategy['speed']
        dx *= speed_multiplier
        dy *= speed_multiplier
        
        return {'dx': dx, 'dy': dy, 'speed': speed_multiplier}
    
    def _decide_resource_usage(self, game_state: Dict[str, Any], strategy: Dict[str, float]) -> Dict[str, Any]:
        """决定资源使用策略"""
        player_health = game_state.get('player_health', 100)
        player_ammo = game_state.get('player_ammo', 100)
        power_ups = game_state.get('available_power_ups', [])
        
        decisions = {
            'use_health_pack': player_health < 50 and strategy['defense'] > 0.5,
            'use_ammo_pack': player_ammo < 30 and strategy['aggression'] > 0.5,
            'use_shield': player_health < 70 and strategy['defense'] > 0.6,
            'use_speed_boost': strategy['speed'] > 1.2 and strategy['aggression'] > 0.6,
            'save_power_ups': strategy['resource_management'] > 0.7
        }
        
        return decisions
    
    def get_strategy_summary(self) -> str:
        """获取策略摘要"""
        if not self.current_strategy:
            return "未生成策略"
        
        strategy = self.current_strategy
        summary = f"""
🧠 AI策略摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 策略ID: {strategy['strategy_id']}
🔄 代数: {strategy['generation']}
🏆 适应度: {strategy['fitness_score']:.3f}

📊 核心参数:
   • 攻击性: {strategy['aggression']:.2f}
   • 防御性: {strategy['defense']:.2f}
   • 速度: {strategy['speed']:.2f}
   • 准确率: {strategy['accuracy']:.2f}
   • 风险承受: {strategy['risk_tolerance']:.2f}
   • 适应性: {strategy['adaptability']:.2f}

🎯 战术配置:
   • 攻击战术: {', '.join(strategy['tactics']['attack'])}
   • 防御战术: {', '.join(strategy['tactics']['defense'])}
   • 移动战术: {', '.join(strategy['tactics']['movement'])}

🎭 行为模式:
   • 战斗风格: {strategy['behavior_patterns']['combat_style']}
   • 决策方式: {strategy['behavior_patterns']['decision_making']}
   • 团队协作: {'是' if strategy['behavior_patterns']['team_coordination'] else '否'}

💰 资源分配:
   • 武器: {strategy['resource_allocation']['weapons']}%
   • 防御: {strategy['resource_allocation']['defense']}%
   • 速度: {strategy['resource_allocation']['speed']}%
   • 工具: {strategy['resource_allocation']['utility']}%

📈 性能历史: {len(self.strategy_history)} 个版本
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        return summary.strip()

# 使用示例
if __name__ == "__main__":
    # 创建AI策略生成器
    generator = AIGameStrategyGenerator()
    
    # 生成初始策略
    strategy = generator.generate_initial_strategy()
    
    # 打印策略摘要
    print(generator.get_strategy_summary())
    
    # 模拟游戏运行和策略进化
    print("\n🎮 模拟游戏运行和策略进化...")
    
    for generation in range(1, 4):
        print(f"\n--- 第{generation}代策略 ---")
        
        # 模拟性能数据
        performance_data = {
            'survival_time': random.uniform(20, 80),
            'enemies_killed': random.randint(5, 25),
            'damage_taken': random.uniform(20, 80),
            'power_ups_collected': random.randint(2, 8),
            'accuracy_rate': random.uniform(0.3, 0.9)
        }
        
        print(f"性能数据: {performance_data}")
        
        # 进化策略
        new_strategy = generator.evolve_strategy(performance_data)
        
        # 模拟AI决策
        game_state = {
            'player_health': 75,
            'nearby_enemies': 3,
            'power_ups_available': 1,
            'enemies': [{'position': {'x': 300, 'y': 200}, 'distance': 150, 'threat_level': 0.7}],
            'player_position': {'x': 400, 'y': 500},
            'player_ammo': 50,
            'available_power_ups': ['health', 'ammo']
        }
        
        decision = generator.get_ai_decision(game_state)
        print(f"AI决策: {decision}")
    
    # 最终策略摘要
    print("\n" + "="*50)
    print("最终策略摘要:")
    print(generator.get_strategy_summary())
