#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI游戏规则生成器
动态生成游戏玩法、策略和规则，增加游戏随机性
"""

import random
import json
import math
import numpy as np
from typing import Dict, List, Tuple, Any
import colorsys
import time

class AIGameRuleGenerator:
    """AI游戏规则生成器"""
    
    def __init__(self):
        self.seed = random.randint(1, 10000)
        random.seed(self.seed)
        np.random.seed(self.seed)
        
        # 游戏规则模板
        self.rule_templates = {
            'enemy_spawn': {
                'patterns': ['wave', 'random', 'spiral', 'formation', 'chaos'],
                'speeds': [1, 2, 3, 4, 5],
                'healths': [1, 2, 3, 4, 5],
                'behaviors': ['straight', 'zigzag', 'circle', 'chase', 'evade']
            },
            'power_ups': {
                'types': ['health', 'speed', 'firepower', 'shield', 'bomb'],
                'rarities': [0.1, 0.3, 0.5, 0.7, 0.9],
                'effects': ['instant', 'temporary', 'permanent']
            },
            'level_design': {
                'backgrounds': ['space', 'city', 'forest', 'desert', 'ocean'],
                'difficulties': ['easy', 'normal', 'hard', 'extreme'],
                'themes': ['sci-fi', 'military', 'fantasy', 'cyberpunk']
            }
        }
        
        # 当前游戏规则
        self.current_rules = {}
        
    def generate_game_session(self) -> Dict[str, Any]:
        """生成新的游戏会话规则"""
        print(f"[AI] AI正在生成新的游戏规则 (种子: {self.seed})...")
        
        # 生成基础规则
        self.current_rules = {
            'session_id': f"session_{self.seed}",
            'seed': self.seed,
            'generation_timestamp': time.time(),
            'enemy_spawn_rules': self._generate_enemy_spawn_rules(),
            'power_up_rules': self._generate_power_up_rules(),
            'level_design_rules': self._generate_level_design_rules(),
            'ai_behavior_rules': self._generate_ai_behavior_rules(),
            'special_events': self._generate_special_events(),
            'scoring_rules': self._generate_scoring_rules()
        }
        
        print("[AI] AI游戏规则生成完成！")
        return self.current_rules
    
    def _generate_enemy_spawn_rules(self) -> Dict[str, Any]:
        """生成敌机生成规则"""
        pattern = random.choice(self.rule_templates['enemy_spawn']['patterns'])
        
        if pattern == 'wave':
            return {
                'type': 'wave',
                'wave_count': random.randint(3, 8),
                'enemies_per_wave': random.randint(5, 15),
                'wave_delay': random.uniform(2.0, 5.0),
                'enemy_speed': random.choice(self.rule_templates['enemy_spawn']['speeds']),
                'enemy_health': random.choice(self.rule_templates['enemy_spawn']['healths']),
                'enemy_behavior': random.choice(self.rule_templates['enemy_spawn']['behaviors'])
            }
        elif pattern == 'spiral':
            return {
                'type': 'spiral',
                'spiral_arms': random.randint(2, 6),
                'enemies_per_arm': random.randint(8, 20),
                'spiral_tightness': random.uniform(0.5, 2.0),
                'enemy_speed': random.choice(self.rule_templates['enemy_spawn']['speeds']),
                'enemy_health': random.choice(self.rule_templates['enemy_spawn']['healths']),
                'enemy_behavior': random.choice(self.rule_templates['enemy_spawn']['behaviors'])
            }
        elif pattern == 'formation':
            return {
                'type': 'formation',
                'formation_type': random.choice(['v', 'square', 'triangle', 'diamond']),
                'formation_size': random.randint(3, 7),
                'formation_spacing': random.uniform(50, 150),
                'enemy_speed': random.choice(self.rule_templates['enemy_spawn']['speeds']),
                'enemy_health': random.choice(self.rule_templates['enemy_spawn']['healths']),
                'enemy_behavior': random.choice(self.rule_templates['enemy_spawn']['behaviors'])
            }
        else:  # random, chaos
            return {
                'type': pattern,
                'enemy_count': random.randint(20, 50),
                'spawn_interval': random.uniform(0.5, 2.0),
                'enemy_speed': random.choice(self.rule_templates['enemy_spawn']['speeds']),
                'enemy_health': random.choice(self.rule_templates['enemy_spawn']['healths']),
                'enemy_behavior': random.choice(self.rule_templates['enemy_spawn']['behaviors'])
            }
    
    def _generate_power_up_rules(self) -> Dict[str, Any]:
        """生成道具系统规则"""
        power_up_count = random.randint(3, 8)
        power_ups = []
        
        for _ in range(power_up_count):
            power_up_type = random.choice(self.rule_templates['power_ups']['types'])
            rarity = random.choice(self.rule_templates['power_ups']['rarities'])
            effect = random.choice(self.rule_templates['power_ups']['effects'])
            
            power_ups.append({
                'type': power_up_type,
                'rarity': rarity,
                'effect': effect,
                'duration': random.uniform(5.0, 30.0) if effect == 'temporary' else 0,
                'value': random.randint(1, 5)
            })
        
        return {
            'power_ups': power_ups,
            'drop_rate': random.uniform(0.1, 0.3),
            'max_power_ups': random.randint(2, 5)
        }
    
    def _generate_level_design_rules(self) -> Dict[str, Any]:
        """生成关卡设计规则"""
        background = random.choice(self.rule_templates['level_design']['backgrounds'])
        difficulty = random.choice(self.rule_templates['level_design']['difficulties'])
        theme = random.choice(self.rule_templates['level_design']['themes'])
        
        # 根据难度调整参数
        difficulty_multiplier = {'easy': 0.7, 'normal': 1.0, 'hard': 1.5, 'extreme': 2.0}[difficulty]
        
        return {
            'background': background,
            'difficulty': difficulty,
            'theme': theme,
            'difficulty_multiplier': difficulty_multiplier,
            'parallax_layers': random.randint(2, 5),
            'ambient_effects': random.choice([True, False]),
            'weather_effects': random.choice([True, False]) if background in ['forest', 'desert', 'ocean'] else False
        }
    
    def _generate_ai_behavior_rules(self) -> Dict[str, Any]:
        """生成AI行为规则"""
        return {
            'aggression_level': random.uniform(0.3, 0.9),
            'learning_rate': random.uniform(0.01, 0.1),
            'adaptation_speed': random.uniform(0.5, 2.0),
            'teamwork_factor': random.uniform(0.0, 1.0),
            'special_abilities': random.randint(0, 3),
            'behavior_patterns': random.sample(['aggressive', 'defensive', 'tactical', 'chaotic'], 
                                            random.randint(2, 4))
        }
    
    def _generate_special_events(self) -> List[Dict[str, Any]]:
        """生成特殊事件"""
        event_count = random.randint(2, 6)
        events = []
        
        event_types = [
            'boss_battle', 'power_surge', 'time_warp', 'gravity_shift',
            'shield_break', 'speed_boost', 'weapon_upgrade', 'health_drain'
        ]
        
        for _ in range(event_count):
            event_type = random.choice(event_types)
            trigger_condition = random.choice(['time', 'score', 'enemies_killed', 'random'])
            
            events.append({
                'type': event_type,
                'trigger': trigger_condition,
                'trigger_value': random.randint(10, 100),
                'duration': random.uniform(5.0, 20.0),
                'effect_strength': random.uniform(0.5, 2.0)
            })
        
        return events
    
    def _generate_scoring_rules(self) -> Dict[str, Any]:
        """生成计分系统"""
        return {
            'base_score': random.randint(100, 500),
            'combo_multiplier': random.uniform(1.1, 2.0),
            'time_bonus': random.uniform(0.5, 2.0),
            'accuracy_bonus': random.uniform(1.0, 3.0),
            'survival_bonus': random.uniform(1.5, 4.0),
            'special_achievements': random.randint(3, 8)
        }
    
    def get_dynamic_enemy_spawn(self, frame_count: int, current_enemies: int) -> List[Dict[str, Any]]:
        """根据当前规则动态生成敌机"""
        if not self.current_rules:
            return []
        
        spawn_rules = self.current_rules['enemy_spawn_rules']
        new_enemies = []
        
        if spawn_rules['type'] == 'wave':
            # 波次生成
            wave_number = frame_count // int(spawn_rules['wave_delay'] * 60)
            if wave_number < spawn_rules['wave_count']:
                if frame_count % int(spawn_rules['wave_delay'] * 60) == 0:
                    for i in range(spawn_rules['enemies_per_wave']):
                        angle = (i / spawn_rules['enemies_per_wave']) * 2 * math.pi
                        x = 800 + math.cos(angle) * 100
                        y = 100 + math.sin(angle) * 200
                        new_enemies.append({
                            'x': x, 'y': y,
                            'speed': spawn_rules['enemy_speed'],
                            'health': spawn_rules['enemy_health'],
                            'behavior': spawn_rules['enemy_behavior']
                        })
        
        elif spawn_rules['type'] == 'spiral':
            # 螺旋生成
            if frame_count % 30 == 0 and current_enemies < 20:
                arm = len(new_enemies) % spawn_rules['spiral_arms']
                angle = (frame_count / 60) * spawn_rules['spiral_tightness'] + (arm * 2 * math.pi / spawn_rules['spiral_arms'])
                radius = 100 + (frame_count / 60) * 50
                x = 800 + math.cos(angle) * radius
                y = 300 + math.sin(angle) * radius
                new_enemies.append({
                    'x': x, 'y': y,
                    'speed': spawn_rules['enemy_speed'],
                    'health': spawn_rules['enemy_health'],
                    'behavior': spawn_rules['enemy_behavior']
                })
        
        elif spawn_rules['type'] == 'formation':
            # 编队生成
            if frame_count % 120 == 0:
                formation_size = spawn_rules['formation_size']
                spacing = spawn_rules['formation_spacing']
                
                if spawn_rules['formation_type'] == 'v':
                    for i in range(formation_size):
                        x = 800 + (i - formation_size//2) * spacing * 0.5
                        y = 100 + abs(i - formation_size//2) * spacing * 0.3
                        new_enemies.append({
                            'x': x, 'y': y,
                            'speed': spawn_rules['enemy_speed'],
                            'health': spawn_rules['enemy_health'],
                            'behavior': spawn_rules['enemy_behavior']
                        })
        
        return new_enemies
    
    def get_dynamic_power_up(self, frame_count: int, player_score: int) -> Dict[str, Any]:
        """根据当前规则动态生成道具"""
        if not self.current_rules:
            return None
        
        power_up_rules = self.current_rules['power_up_rules']
        
        # 根据分数和帧数决定是否生成道具
        if random.random() < power_up_rules['drop_rate']:
            power_up = random.choice(power_up_rules['power_ups'])
            
            # 根据稀有度调整生成概率
            if random.random() < power_up['rarity']:
                # 修复：让道具在整个屏幕范围内随机生成
                # 避免在边缘区域生成，留出安全边距
                return {
                    'type': power_up['type'],
                    'x': random.randint(50, 750),  # 扩大x范围，避免边缘
                    'y': random.randint(50, 550),  # 扩大y范围，覆盖整个屏幕
                    'effect': power_up['effect'],
                    'duration': power_up['duration'],
                    'value': power_up['value']
                }
        
        return None
    
    def apply_special_event(self, frame_count: int, player_score: int, current_enemies: int) -> Dict[str, Any]:
        """应用特殊事件"""
        if not self.current_rules:
            return {}
        
        events = self.current_rules['special_events']
        active_events = {}
        
        for event in events:
            # 检查触发条件
            triggered = False
            if event['trigger'] == 'time' and frame_count >= event['trigger_value'] * 60:
                triggered = True
            elif event['trigger'] == 'score' and player_score >= event['trigger_value']:
                triggered = True
            elif event['trigger'] == 'enemies_killed' and current_enemies >= event['trigger_value']:
                triggered = True
            elif event['trigger'] == 'random' and random.random() < 0.001:  # 0.1% 概率
                triggered = True
            
            if triggered:
                active_events[event['type']] = {
                    'duration': event['duration'],
                    'effect_strength': event['effect_strength'],
                    'start_frame': frame_count
                }
        
        return active_events
    
    def get_ai_difficulty_adjustment(self, player_performance: float) -> float:
        """根据玩家表现动态调整AI难度"""
        if not self.current_rules:
            return 1.0
        
        ai_rules = self.current_rules['ai_behavior_rules']
        
        # 基础难度
        base_difficulty = ai_rules['aggression_level']
        
        # 根据玩家表现调整
        if player_performance > 0.8:  # 玩家表现很好
            difficulty_boost = ai_rules['adaptation_speed'] * 0.5
        elif player_performance < 0.3:  # 玩家表现较差
            difficulty_boost = -ai_rules['adaptation_speed'] * 0.3
        else:
            difficulty_boost = 0
        
        return max(0.1, min(2.0, base_difficulty + difficulty_boost))
    
    def get_session_summary(self) -> str:
        """获取游戏会话摘要"""
        if not self.current_rules:
            return "未生成游戏规则"
        
        rules = self.current_rules
        summary = f"""
🎮 AI游戏规则会话摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 会话ID: {rules['session_id']}
🎲 随机种子: {rules['seed']}

👾 敌机生成规则:
   • 类型: {rules['enemy_spawn_rules']['type']}
   • 速度: {rules['enemy_spawn_rules']['enemy_speed']}
   • 生命值: {rules['enemy_spawn_rules']['enemy_health']}
   • 行为: {rules['enemy_spawn_rules']['enemy_behavior']}

⚡ 道具系统:
   • 道具数量: {len(rules['power_up_rules']['power_ups'])}
   • 掉落率: {rules['power_up_rules']['drop_rate']:.2f}
   • 最大道具: {rules['power_up_rules']['max_power_ups']}

🎨 关卡设计:
   • 背景: {rules['level_design_rules']['background']}
   • 难度: {rules['level_design_rules']['difficulty']}
   • 主题: {rules['level_design_rules']['theme']}

🤖 AI行为:
   • 攻击性: {rules['ai_behavior_rules']['aggression_level']:.2f}
   • 学习率: {rules['ai_behavior_rules']['learning_rate']:.3f}
   • 适应速度: {rules['ai_behavior_rules']['adaptation_speed']:.2f}

🎯 特殊事件: {len(rules['special_events'])} 个
🏆 计分系统: 基础分数 {rules['scoring_rules']['base_score']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        return summary.strip()

# 使用示例
if __name__ == "__main__":
    # 创建AI规则生成器
    generator = AIGameRuleGenerator()
    
    # 生成新的游戏会话
    rules = generator.generate_game_session()
    
    # 打印会话摘要
    print(generator.get_session_summary())
    
    # 模拟游戏运行
    print("\n[AI] 模拟游戏运行...")
    for frame in range(0, 300, 30):  # 每30帧检查一次
        # 模拟敌机生成
        enemies = generator.get_dynamic_enemy_spawn(frame, 5)
        if enemies:
            print(f"帧 {frame}: 生成 {len(enemies)} 个敌机")
        
        # 模拟道具生成
        power_up = generator.get_dynamic_power_up(frame, frame * 10)
        if power_up:
            print(f"帧 {frame}: 生成道具 {power_up['type']}")
        
        # 模拟特殊事件
        events = generator.apply_special_event(frame, frame * 10, len(enemies))
        if events:
            print(f"帧 {frame}: 触发事件 {list(events.keys())}")
