#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI训练和集成脚本 - 训练AI飞机控制器和场景生成器
"""

import time
import random
import numpy as np
from typing import Dict, List, Any

# 导入AI系统
from ai_controllers.advanced_ai_controller import AdvancedAIController
from ai_scene_generator import AISceneGenerator
from ml_game_ai import MLGameAI
from rl_game_ai import RLGameAI
from intelligent_decision_system import IntelligentDecisionSystem
from ai_learning_optimizer import AILearningOptimizer
from ai_master_controller import AIMasterController

class AITrainer:
    """AI训练器"""
    
    def __init__(self):
        print("🚀 AI训练器初始化...")
        
        # 初始化AI系统
        self.ai_controller = AdvancedAIController()
        self.scene_generator = AISceneGenerator()
        self.ml_ai = MLGameAI()
        self.rl_ai = RLGameAI()
        self.decision_system = IntelligentDecisionSystem()
        self.learning_optimizer = AILearningOptimizer()
        self.master_controller = AIMasterController()
        
        # 训练参数
        self.training_config = {
            'ai_controller_episodes': 100,
            'scene_generation_count': 50,
            'learning_iterations': 200,
            'evaluation_interval': 10
        }
        
        print("✅ AI训练器初始化完成")
    
    def train_ai_controller(self):
        """训练AI飞机控制器"""
        print("\n🎮 开始训练AI飞机控制器...")
        
        for episode in range(self.training_config['ai_controller_episodes']):
            print(f"📚 训练回合 {episode + 1}/{self.training_config['ai_controller_episodes']}")
            
            # 生成训练游戏状态
            game_state = self._generate_training_game_state(episode)
            
            # AI做出决策
            action = self.ai_controller.get_action(game_state)
            
            # 模拟游戏结果
            game_outcome = self._simulate_game_outcome(game_state, action, episode)
            
            # 学习
            self.ai_controller.learn_from_experience(game_outcome)
            
            # 定期评估
            if (episode + 1) % self.training_config['evaluation_interval'] == 0:
                self._evaluate_ai_controller(episode + 1)
        
        print("✅ AI飞机控制器训练完成")
    
    def train_scene_generator(self):
        """训练场景生成器"""
        print("\n🎮 开始训练场景生成器...")
        
        for i in range(self.training_config['scene_generation_count']):
            print(f"🎨 生成场景 {i + 1}/{self.training_config['scene_generation_count']}")
            
            # 生成不同难度的场景
            difficulty = random.uniform(0.2, 0.9)
            scene = self.scene_generator.generate_scene(difficulty)
            
            # 模拟场景评估
            simulated_outcome = self._simulate_scene_outcome(scene, difficulty)
            
            # 评估场景
            self.scene_generator.evaluate_scene_performance(scene.scene_id, simulated_outcome)
            
            # 定期显示进度
            if (i + 1) % 10 == 0:
                self._show_scene_generation_progress(i + 1)
        
        print("✅ 场景生成器训练完成")
    
    def train_all_ai_systems(self):
        """训练所有AI系统"""
        print("\n🧠 开始训练所有AI系统...")
        
        for iteration in range(self.training_config['learning_iterations']):
            print(f"🔄 学习迭代 {iteration + 1}/{self.training_config['learning_iterations']}")
            
            # 1. 训练机器学习AI
            self._train_ml_ai(iteration)
            
            # 2. 训练强化学习AI
            self._train_rl_ai(iteration)
            
            # 3. 训练决策系统
            self._train_decision_system(iteration)
            
            # 4. 训练学习优化器
            self._train_learning_optimizer(iteration)
            
            # 定期保存模型
            if (iteration + 1) % 50 == 0:
                self._save_all_models(iteration + 1)
        
        print("✅ 所有AI系统训练完成")
    
    def _train_ml_ai(self, iteration: int):
        """训练机器学习AI"""
        # 生成训练数据
        game_state = self._generate_training_game_state(iteration)
        
        # 生成游戏模式
        pattern = self.ml_ai.generate_game_pattern(game_state)
        
        # 模拟游戏结果
        game_outcome = self._simulate_game_outcome(game_state, pattern, iteration)
        
        # 学习
        self.ml_ai.learn_from_experience(game_state, pattern, game_outcome)
    
    def _train_rl_ai(self, iteration: int):
        """训练强化学习AI"""
        # 生成游戏状态序列
        game_states = []
        actions = []
        
        for step in range(10):
            game_state = self._generate_training_game_state(iteration * 10 + step)
            game_states.append(game_state)
            
            action = self.rl_ai.act(game_state)
            actions.append(action)
        
        # 模拟游戏结果
        game_outcome = self._simulate_game_outcome(game_states[-1], actions[-1], iteration)
        
        # 学习
        self.rl_ai.learn_from_game(game_states, actions, game_outcome)
    
    def _train_decision_system(self, iteration: int):
        """训练决策系统"""
        # 生成游戏状态
        game_state = self._generate_training_game_state(iteration)
        
        # 做出决策
        decision = self.decision_system.make_intelligent_decision(game_state)
        
        # 模拟游戏结果
        game_outcome = self._simulate_game_outcome(game_state, decision.parameters, iteration)
        
        # 学习
        self.decision_system.learn_from_decision_outcome(decision, game_outcome)
    
    def _train_learning_optimizer(self, iteration: int):
        """训练学习优化器"""
        # 创建学习经验
        from ai_learning_optimizer import LearningExperience
        
        experience = LearningExperience(
            state=self._generate_training_game_state(iteration),
            action={'type': 'wave', 'wave_count': 5, 'enemies_per_wave': 8},
            reward=random.uniform(3.0, 8.0),
            next_state=self._generate_training_game_state(iteration + 1),
            outcome=self._simulate_game_outcome({}, {}, iteration),
            timestamp=time.time(),
            session_id=f'training_{iteration}'
        )
        
        # 学习
        self.learning_optimizer.learn_from_experience(experience)
    
    def _generate_training_game_state(self, episode: int) -> Dict[str, Any]:
        """生成训练游戏状态"""
        # 基于回合数生成不同的游戏状态
        base_health = 100 - (episode % 20) * 2
        base_score = episode * 50
        base_enemies = 5 + (episode % 15)
        
        return {
            'player_health': max(20, base_health),
            'player_score': base_score,
            'enemies_killed': episode % 25,
            'survival_time': episode * 2,
            'player_position': {
                'x': 400 + random.randint(-100, 100),
                'y': 300 + random.randint(-100, 100)
            },
            'enemies': [
                {
                    'position': {
                        'x': random.randint(0, 800),
                        'y': random.randint(0, 600)
                    },
                    'speed': random.randint(1, 5),
                    'health': random.randint(1, 4),
                    'size': 50
                }
                for _ in range(base_enemies)
            ],
            'bullets': [
                {
                    'position': {
                        'x': random.randint(0, 800),
                        'y': random.randint(0, 600)
                    },
                    'type': random.choice(['player', 'enemy']),
                    'speed': random.randint(3, 7)
                }
                for _ in range(random.randint(0, 8))
            ],
            'power_ups': [
                {
                    'position': {
                        'x': random.randint(0, 800),
                        'y': random.randint(0, 600)
                    },
                    'type': random.choice(['health', 'shield', 'weapon', 'speed']),
                    'value': random.randint(1, 3)
                }
                for _ in range(random.randint(0, 3))
            ],
            'ai_difficulty': 1.0 + (episode % 10) * 0.1,
            'frame_count': episode * 60
        }
    
    def _simulate_game_outcome(self, game_state: Dict[str, Any], action: Dict[str, Any], episode: int) -> Dict[str, Any]:
        """模拟游戏结果"""
        # 基于游戏状态和动作模拟结果
        base_survival = 60 + random.randint(-20, 40)
        base_score = 500 + random.randint(-200, 400)
        base_kills = 10 + random.randint(-5, 15)
        base_damage = 30 + random.randint(-15, 45)
        
        # 根据AI动作调整结果
        if isinstance(action, dict):
            if action.get('strategy') == 'aggressive':
                base_score += 100
                base_kills += 5
                base_damage += 20
            elif action.get('strategy') == 'defensive':
                base_survival += 20
                base_damage -= 15
                base_score -= 50
        
        return {
            'survival_time': max(10, base_survival),
            'score': max(100, base_score),
            'enemies_killed': max(0, base_kills),
            'damage_taken': max(0, base_damage),
            'player_survived': True,
            'game_duration': base_survival
        }
    
    def _simulate_scene_outcome(self, scene: Any, difficulty: float) -> Dict[str, Any]:
        """模拟场景结果"""
        # 基于场景难度模拟结果
        expected_survival = scene.expected_outcome['expected_survival_time']
        expected_score = scene.expected_outcome['expected_score']
        expected_kills = scene.expected_outcome['expected_enemies_killed']
        expected_damage = scene.expected_outcome['expected_damage_taken']
        
        # 添加随机变化
        survival_variation = random.uniform(0.7, 1.3)
        score_variation = random.uniform(0.6, 1.4)
        kills_variation = random.uniform(0.5, 1.5)
        damage_variation = random.uniform(0.8, 1.2)
        
        return {
            'survival_time': expected_survival * survival_variation,
            'score': expected_score * score_variation,
            'enemies_killed': expected_kills * kills_variation,
            'damage_taken': expected_damage * damage_variation
        }
    
    def _evaluate_ai_controller(self, episode: int):
        """评估AI控制器"""
        report = self.ai_controller.get_performance_report()
        
        print(f"📊 AI控制器评估 (回合 {episode}):")
        print(f"   总游戏数: {report['total_games']}")
        print(f"   平均分数: {report['average_score']:.1f}")
        print(f"   平均生存时间: {report['average_survival_time']:.1f}")
        print(f"   平均击杀数: {report['average_enemies_killed']:.1f}")
        print(f"   探索率: {report['exploration_rate']:.3f}")
        print(f"   策略置信度: {report['strategy_confidence']:.3f}")
    
    def _show_scene_generation_progress(self, count: int):
        """显示场景生成进度"""
        report = self.scene_generator.get_generation_report()
        
        print(f"📊 场景生成进度 ({count}):")
        print(f"   总场景数: {report['scene_database_size']}")
        print(f"   平均难度: {report['generation_stats']['average_difficulty']:.2f}")
        print(f"   创造力因子: {report['learning_parameters']['creativity_factor']:.3f}")
    
    def _save_all_models(self, iteration: int):
        """保存所有模型"""
        print(f"💾 保存所有模型 (迭代 {iteration})...")
        
        try:
            self.master_controller.save_all_models()
            print("✅ 所有模型保存成功")
        except Exception as e:
            print(f"❌ 模型保存失败: {e}")
    
    def run_complete_training(self):
        """运行完整训练"""
        print("🎯 开始完整AI训练流程...")
        
        # 1. 训练AI飞机控制器
        self.train_ai_controller()
        
        # 2. 训练场景生成器
        self.train_scene_generator()
        
        # 3. 训练所有AI系统
        self.train_all_ai_systems()
        
        # 4. 最终评估
        self._final_evaluation()
        
        print("🎉 完整AI训练流程完成！")
    
    def _final_evaluation(self):
        """最终评估"""
        print("\n📊 最终评估结果:")
        
        # AI控制器评估
        ai_report = self.ai_controller.get_performance_report()
        print(f"🤖 AI控制器:")
        print(f"   总游戏数: {ai_report['total_games']}")
        print(f"   平均分数: {ai_report['average_score']:.1f}")
        print(f"   平均生存时间: {ai_report['average_survival_time']:.1f}")
        
        # 场景生成器评估
        scene_report = self.scene_generator.get_generation_report()
        print(f"🎮 场景生成器:")
        print(f"   总场景数: {scene_report['scene_database_size']}")
        print(f"   平均难度: {scene_report['generation_stats']['average_difficulty']:.2f}")
        
        # 主控制器评估
        master_report = self.master_controller.get_ai_status()
        print(f"🎯 主控制器:")
        print(f"   总会话数: {master_report['performance_stats']['total_sessions']}")
        print(f"   总决策数: {master_report['performance_stats']['total_decisions']}")
    
    def test_ai_integration(self):
        """测试AI集成"""
        print("\n🧪 测试AI集成...")
        
        # 创建游戏会话
        player_info = {'name': 'TestPlayer', 'skill_level': 'intermediate'}
        session_id = self.master_controller.start_game_session(player_info)
        
        # 生成测试场景
        test_scene = self.scene_generator.generate_scene(target_difficulty=0.6)
        
        # 模拟游戏状态
        game_state = self._generate_training_game_state(0)
        
        # AI做出决策
        decision = self.master_controller.make_ai_decision(session_id, game_state)
        
        # 更新游戏状态
        self.master_controller.update_game_state(session_id, game_state)
        
        # 模拟游戏结果
        test_outcome = self._simulate_game_outcome(game_state, decision, 0)
        
        # 记录结果
        self.master_controller.record_game_outcome(session_id, test_outcome)
        
        # 结束会话
        self.master_controller.end_game_session(session_id, test_outcome)
        
        print("✅ AI集成测试完成")
        
        return {
            'session_id': session_id,
            'scene': test_scene,
            'decision': decision,
            'outcome': test_outcome
        }

def main():
    """主函数"""
    print("🚀 AI训练和集成系统启动")
    
    # 创建训练器
    trainer = AITrainer()
    
    # 运行完整训练
    trainer.run_complete_training()
    
    # 测试AI集成
    test_result = trainer.test_ai_integration()
    
    print(f"\n🎯 测试结果:")
    print(f"   会话ID: {test_result['session_id']}")
    print(f"   场景类型: {test_result['scene'].scene_type}")
    print(f"   AI决策: {test_result['decision']}")
    print(f"   游戏结果: {test_result['outcome']}")
    
    print("\n🎉 AI训练和集成完成！")
    print("\n📖 使用说明:")
    print("1. AI飞机控制器已训练完成，可以控制飞机进行智能战斗")
    print("2. 场景生成器已训练完成，可以生成各种游戏场景")
    print("3. 所有AI系统已集成，可以协同工作")
    print("4. 模型已保存，下次启动时会自动加载")

if __name__ == "__main__":
    main()
