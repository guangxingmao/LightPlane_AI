#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI游戏场景生成器 - 持续学习并生成更多游戏场景
"""

import numpy as np
import random
import time
import json
import os
from typing import Dict, List, Any, Tuple
from collections import deque
from dataclasses import dataclass, asdict

@dataclass
class GameScene:
    """游戏场景定义"""
    scene_id: str
    scene_type: str
    difficulty: float
    enemy_pattern: Dict[str, Any]
    power_up_distribution: Dict[str, Any]
    background_theme: str
    special_events: List[Dict[str, Any]]
    player_requirements: Dict[str, Any]
    expected_outcome: Dict[str, Any]
    creation_timestamp: float
    success_rate: float
    play_count: int

class AISceneGenerator:
    """AI游戏场景生成器"""
    
    def __init__(self):
        """初始化AI场景生成器"""
        print("[场景] AI游戏场景生成器初始化...")
        
        # 场景模板数据库
        self.scene_templates = {
            'tactical_combat': {
                'difficulty': 0.7,
                'enemy_pattern': 'formation',
                'power_up_distribution': 'balanced',
                'special_events': ['shield_break', 'gravity_shift'],
                'player_requirements': {'skill_level': 'intermediate', 'equipment': 'standard'},
                'expected_outcome': {'success_rate': 0.6, 'completion_time': 180}
            },
            'survival_challenge': {
                'difficulty': 0.9,
                'enemy_pattern': 'wave',
                'power_up_distribution': 'scarce',
                'special_events': ['enemy_swarm', 'power_drain'],
                'player_requirements': {'skill_level': 'expert', 'equipment': 'advanced'},
                'expected_outcome': {'success_rate': 0.3, 'completion_time': 300}
            },
            'speed_run': {
                'difficulty': 0.5,
                'enemy_pattern': 'random',
                'power_up_distribution': 'abundant',
                'special_events': ['speed_boost', 'time_bonus'],
                'player_requirements': {'skill_level': 'beginner', 'equipment': 'basic'},
                'expected_outcome': {'success_rate': 0.8, 'completion_time': 120}
            }
        }
        
        # 场景数据库
        self.scene_database = []
        self.scene_counter = 0
        
        # 学习参数
        self.learning_rate = 0.01
        self.creativity_factor = 0.7
        self.adaptation_speed = 0.1
        
        # 性能统计
        self.generation_stats = {
            'total_scenes_generated': 0,
            'successful_scenes': 0,
            'average_difficulty': 0.0,
            'popular_scene_types': {},
            'learning_progress': []
        }
        
        # 场景评估历史
        self.scene_evaluations = deque(maxlen=1000)
        
        print("[场景] AI场景生成器初始化完成")
    
    def _initialize_scene_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化场景模板"""
        return {
            'wave_attack': {
                'name': '波次攻击',
                'base_difficulty': 0.3,
                'enemy_patterns': ['wave', 'formation', 'spiral'],
                'power_up_types': ['health', 'shield', 'weapon'],
                'special_events': ['boss_battle', 'time_warp', 'power_surge']
            },
            'survival_challenge': {
                'name': '生存挑战',
                'base_difficulty': 0.5,
                'enemy_patterns': ['random', 'chaos', 'swarm'],
                'power_up_types': ['health', 'shield', 'speed'],
                'special_events': ['enemy_swarm', 'health_drain', 'speed_boost']
            },
            'speed_test': {
                'name': '速度测试',
                'base_difficulty': 0.7,
                'enemy_patterns': ['formation', 'chase', 'intercept'],
                'power_up_types': ['speed', 'weapon', 'shield'],
                'special_events': ['speed_boost', 'time_slow', 'bullet_storm']
            },
            'tactical_combat': {
                'name': '战术战斗',
                'base_difficulty': 0.8,
                'enemy_patterns': ['formation', 'tactical', 'cooperative'],
                'power_up_types': ['weapon', 'shield', 'tactical'],
                'special_events': ['enemy_coordination', 'tactical_retreat', 'power_shift']
            },
            'chaos_mode': {
                'name': '混沌模式',
                'base_difficulty': 0.9,
                'enemy_patterns': ['chaos', 'random', 'unpredictable'],
                'power_up_types': ['random', 'chaos', 'surprise'],
                'special_events': ['random_event', 'chaos_burst', 'surprise_attack']
            }
        }
    
    def generate_scene(self, target_difficulty: float, player_skill_level: str) -> Dict[str, Any]:
        """生成新的游戏场景"""
        print(f"[场景] 生成新场景 - 目标难度: {target_difficulty}")
        
        # 选择场景类型
        scene_type = self._select_scene_type(target_difficulty, player_skill_level)
        
        # 生成场景参数
        scene_params = self._generate_scene_parameters(scene_type, target_difficulty)
        
        # 创建场景对象
        scene = {
            'scene_id': f"scene_{int(time.time())}_{random.randint(1000, 9999)}",
            'scene_type': scene_type,
            'difficulty': scene_params['difficulty'],
            'enemy_pattern': scene_params['enemy_pattern'],
            'power_up_distribution': scene_params['power_up_distribution'],
            'special_events': scene_params['special_events'],
            'player_requirements': scene_params['player_requirements'],
            'expected_outcome': scene_params['expected_outcome'],
            'generation_timestamp': time.time(),
            'performance_metrics': {}
        }
        
        # 添加到数据库
        self.scene_database.append(scene)
        self.scene_counter += 1
        
        print(f"[场景] 场景生成完成: {scene['scene_id']} - {scene_type}")
        return scene
    
    def _select_scene_type(self, target_difficulty: float, player_skill_level: str) -> str:
        """选择场景类型"""
        available_types = list(self.scene_templates.keys())
        
        # 基于目标难度筛选
        suitable_types = []
        for scene_type in available_types:
            template = self.scene_templates[scene_type]
            if abs(template['base_difficulty'] - target_difficulty) <= 0.3:
                suitable_types.append(scene_type)
        
        if not suitable_types:
            suitable_types = available_types
        
        return random.choice(suitable_types)
    
    def _generate_scene_parameters(self, scene_type: str, target_difficulty: float) -> Dict[str, Any]:
        """生成场景参数"""
        template = self.scene_templates[scene_type]
        
        # 基础难度调整
        base_difficulty = template['base_difficulty']
        difficulty_variation = random.uniform(-0.2, 0.2)
        final_difficulty = np.clip(base_difficulty + difficulty_variation, 0.1, 1.0)
        
        # 生成敌机模式
        enemy_pattern = self._generate_enemy_pattern(scene_type, final_difficulty)
        
        # 生成道具分布
        power_up_distribution = self._generate_power_up_distribution(scene_type, final_difficulty)
        
        # 选择背景主题
        background_theme = self._select_background_theme(scene_type)
        
        # 生成特殊事件
        special_events = self._generate_special_events(scene_type, final_difficulty)
        
        # 设置玩家要求
        player_requirements = self._generate_player_requirements(final_difficulty, 'intermediate')
        
        # 预测预期结果
        expected_outcome = self._predict_expected_outcome(final_difficulty)
        
        return {
            'difficulty': final_difficulty,
            'enemy_pattern': enemy_pattern,
            'power_up_distribution': power_up_distribution,
            'background_theme': background_theme,
            'special_events': special_events,
            'player_requirements': player_requirements,
            'expected_outcome': expected_outcome
        }
    
    def _generate_enemy_pattern(self, scene_type: str, difficulty: float) -> Dict[str, Any]:
        """生成敌机模式"""
        if scene_type == 'wave_attack':
            return {
                'type': 'wave',
                'wave_count': int(3 + difficulty * 5),
                'enemies_per_wave': int(5 + difficulty * 10),
                'wave_delay': max(1.0, 5.0 - difficulty * 3),
                'enemy_speed': int(1 + difficulty * 4),
                'enemy_health': int(1 + difficulty * 4),
                'enemy_behavior': random.choice(['straight', 'zigzag', 'circle', 'chase'])
            }
        elif scene_type == 'survival_challenge':
            return {
                'type': 'survival',
                'enemy_spawn_rate': 0.5 + difficulty * 0.5,
                'max_enemies': int(10 + difficulty * 20),
                'enemy_speed': int(2 + difficulty * 3),
                'enemy_health': int(1 + difficulty * 3),
                'enemy_behavior': random.choice(['random', 'swarm', 'persistent'])
            }
        else:
            return {
                'type': 'random',
                'enemy_count': int(15 + difficulty * 25),
                'spawn_interval': random.uniform(0.5, 2.5),
                'enemy_speed': random.randint(1, 6),
                'enemy_health': random.randint(1, 5),
                'enemy_behavior': random.choice(['chaos', 'unpredictable', 'random'])
            }
    
    def _generate_power_up_distribution(self, scene_type: str, difficulty: float) -> Dict[str, Any]:
        """生成道具分布"""
        template = self.scene_templates[scene_type]
        available_types = template['power_up_types']
        
        distribution = {}
        total_power_ups = int(3 + difficulty * 7)
        
        for power_up_type in available_types:
            count = random.randint(1, max(1, total_power_ups // len(available_types)))
            distribution[power_up_type] = count
        
        return distribution
    
    def _select_background_theme(self, scene_type: str) -> str:
        """选择背景主题"""
        themes = {
            'wave_attack': ['battlefield', 'space_station', 'military_base'],
            'survival_challenge': ['deep_space', 'asteroid_field', 'nebula'],
            'speed_test': ['highway', 'corridor', 'tunnel'],
            'tactical_combat': ['strategic_zone', 'command_center', 'battle_arena'],
            'chaos_mode': ['void', 'dimension_shift', 'reality_break']
        }
        
        available_themes = themes.get(scene_type, ['default'])
        return random.choice(available_themes)
    
    def _generate_special_events(self, scene_type: str, difficulty: float) -> List[Dict[str, Any]]:
        """生成特殊事件"""
        template = self.scene_templates[scene_type]
        available_events = template['special_events']
        
        events = []
        event_count = int(difficulty * 3)
        
        for _ in range(event_count):
            event_type = random.choice(available_events)
            event = self._create_special_event(event_type, difficulty)
            events.append(event)
        
        return events
    
    def _create_special_event(self, event_type: str, difficulty: float) -> Dict[str, Any]:
        """创建特殊事件"""
        event_templates = {
            'boss_battle': {
                'type': 'boss_battle',
                'boss_health': int(20 + difficulty * 30),
                'boss_speed': int(2 + difficulty * 3),
                'duration': 30.0
            },
            'time_warp': {
                'type': 'time_warp',
                'effect': 'slow_motion',
                'duration': 10.0 + difficulty * 20
            },
            'power_surge': {
                'type': 'power_surge',
                'effect': 'enhanced_weapons',
                'duration': 15.0 + difficulty * 15
            }
        }
        
        return event_templates.get(event_type, {'type': event_type, 'duration': 10.0})
    
    def _generate_player_requirements(self, difficulty: float, skill_level: str) -> Dict[str, Any]:
        """生成玩家要求"""
        return {
            'minimum_health': max(20, int(100 - difficulty * 60)),
            'minimum_score': int(difficulty * 1000),
            'minimum_survival_time': int(difficulty * 120),
            'minimum_accuracy': max(0.3, difficulty * 0.8)
        }
    
    def _predict_expected_outcome(self, difficulty: float) -> Dict[str, Any]:
        """预测预期结果"""
        expected_survival = 60.0 * (1.0 - difficulty * 0.5)
        expected_score = int(difficulty * 1500)
        expected_kills = int(difficulty * 25)
        expected_damage = int(difficulty * 80)
        
        return {
            'expected_survival_time': expected_survival,
            'expected_score': expected_score,
            'expected_enemies_killed': expected_kills,
            'expected_damage_taken': expected_damage,
            'success_probability': max(0.1, 1.0 - difficulty * 0.8)
        }
    
    def _generate_scene_id(self) -> str:
        """生成场景ID"""
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"scene_{timestamp}_{random_suffix}"
    
    def evaluate_scene_performance(self, scene_id: str, actual_outcome: Dict[str, Any]):
        """评估场景性能"""
        if scene_id not in self.scene_database:
            return
        
        scene = self.scene_database[scene_id]
        scene.play_count += 1
        
        # 计算成功率
        expected = scene.expected_outcome
        actual = actual_outcome
        
        survival_match = 1.0 - abs(actual.get('survival_time', 0) - expected['expected_survival_time']) / max(expected['expected_survival_time'], 1)
        score_match = 1.0 - abs(actual.get('score', 0) - expected['expected_score']) / max(expected['expected_score'], 1)
        kills_match = 1.0 - abs(actual.get('enemies_killed', 0) - expected['expected_enemies_killed']) / max(expected['expected_enemies_killed'], 1)
        
        overall_success = (survival_match + score_match + kills_match) / 3
        scene.success_rate = (scene.success_rate * (scene.play_count - 1) + overall_success) / scene.play_count
        
        # 记录评估
        evaluation = {
            'scene_id': scene_id,
            'expected': expected,
            'actual': actual,
            'success_rate': overall_success,
            'timestamp': time.time()
        }
        self.scene_evaluations.append(evaluation)
        
        print(f"📊 场景评估完成: {scene_id} - 成功率: {overall_success:.2f}")
    
    def get_scene_recommendations(self, player_skill_level: str, target_difficulty: float, count: int = 5) -> List[GameScene]:
        """获取场景推荐"""
        suitable_scenes = []
        for scene in self.scene_database.values():
            if (abs(scene.difficulty - target_difficulty) <= 0.3 and 
                scene.play_count > 0 and 
                scene.success_rate > 0.4):
                suitable_scenes.append(scene)
        
        if not suitable_scenes:
            return []
        
        # 按成功率排序
        scene_scores = []
        for scene in suitable_scenes:
            popularity_score = min(scene.play_count / 20.0, 1.0)
            difficulty_match = 1.0 - abs(scene.difficulty - target_difficulty)
            overall_score = scene.success_rate * 0.5 + popularity_score * 0.3 + difficulty_match * 0.2
            
            scene_scores.append((scene, overall_score))
        
        scene_scores.sort(key=lambda x: x[1], reverse=True)
        return [scene for scene, _ in scene_scores[:count]]
    
    def get_generation_report(self) -> Dict[str, Any]:
        """获取生成报告"""
        return {
            'generation_stats': self.generation_stats,
            'scene_database_size': len(self.scene_database),
            'learning_parameters': {
                'learning_rate': self.learning_rate,
                'creativity_factor': self.creativity_factor,
                'adaptation_speed': self.adaptation_speed
            }
        }

# 使用示例
if __name__ == "__main__":
    # 创建AI场景生成器
    generator = AISceneGenerator()
    
    # 生成场景
    scene = generator.generate_scene(target_difficulty=0.6, player_skill_level='intermediate')
    print(f"[场景] 生成的场景: {scene['scene_type']}")
    print(f"   难度: {scene['difficulty']:.2f}")
    print(f"   敌机模式: {scene['enemy_pattern']['type']}")
    print(f"   特殊事件: {len(scene['special_events'])} 个")
    
    # 模拟场景评估
    actual_outcome = {
        'survival_time': 85.0,
        'score': 1200,
        'enemies_killed': 22,
        'damage_taken': 65
    }
    
    # 评估场景
    generator.evaluate_scene_performance(scene['scene_id'], actual_outcome)
    
    # 获取推荐场景
    recommendations = generator.get_scene_recommendations('intermediate', 0.6, 3)
    print(f"📋 推荐场景数量: {len(recommendations)}")
    
    # 获取生成报告
    report = generator.get_generation_report()
    print(f"📊 生成报告: 总场景数 {report['scene_database_size']}")
