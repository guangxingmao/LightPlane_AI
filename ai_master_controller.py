#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI主控制器 - 整合所有AI系统到游戏中
"""

import time
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# 导入AI系统
from ml_game_ai import MLGameAI
from rl_game_ai import RLGameAI
from intelligent_decision_system import IntelligentDecisionSystem
from ai_learning_optimizer import AILearningOptimizer, LearningExperience

@dataclass
class GameSession:
    """游戏会话信息"""
    session_id: str
    start_time: float
    player_stats: Dict[str, Any]
    ai_decisions: List[Dict[str, Any]]
    game_outcomes: List[Dict[str, Any]]
    learning_data: Dict[str, Any]

class AIMasterController:
    """AI主控制器 - 协调所有AI系统"""
    
    def __init__(self, models_dir='./models'):
        print("🤖 初始化AI主控制器...")
        
        # 创建模型目录
        import os
        os.makedirs(models_dir, exist_ok=True)
        
        # 初始化AI系统
        self.ml_ai = MLGameAI(f"{models_dir}/ml_game_ai.pth")
        self.rl_ai = RLGameAI(model_path=f"{models_dir}/rl_game_ai.pth")
        self.decision_system = IntelligentDecisionSystem(f"{models_dir}/intelligent_decision_system.pth")
        self.learning_optimizer = AILearningOptimizer(f"{models_dir}/ai_learning_optimizer.pth")
        
        # 游戏会话管理
        self.active_sessions = {}
        self.session_history = {}
        
        # AI系统状态
        self.system_status = {
            'ml_ai': 'active',
            'rl_ai': 'active', 
            'decision_system': 'active',
            'learning_optimizer': 'active'
        }
        
        # 性能统计
        self.performance_stats = {
            'total_sessions': 0,
            'total_decisions': 0,
            'average_session_duration': 0.0,
            'ai_improvement_rate': 0.0
        }
        
        print("✅ AI主控制器初始化完成")
    
    def start_game_session(self, player_info: Dict[str, Any]) -> str:
        """开始新的游戏会话"""
        session_id = str(uuid.uuid4())[:8]
        
        session = GameSession(
            session_id=session_id,
            start_time=time.time(),
            player_stats=player_info,
            ai_decisions=[],
            game_outcomes=[],
            learning_data={}
        )
        
        self.active_sessions[session_id] = session
        self.performance_stats['total_sessions'] += 1
        
        print(f"🎮 开始游戏会话: {session_id}")
        return session_id
    
    def end_game_session(self, session_id: str, final_outcome: Dict[str, Any]):
        """结束游戏会话"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.game_outcomes.append(final_outcome)
        
        # 计算会话统计
        session_duration = time.time() - session.start_time
        session.learning_data['duration'] = session_duration
        session.learning_data['final_score'] = final_outcome.get('score', 0)
        session.learning_data['survival_time'] = final_outcome.get('survival_time', 0)
        session.learning_data['enemies_killed'] = final_outcome.get('enemies_killed', 0)
        
        # 存储到历史
        self.session_history[session_id] = session
        del self.active_sessions[session_id]
        
        # 更新性能统计
        self.performance_stats['average_session_duration'] = (
            (self.performance_stats['average_session_duration'] * (self.performance_stats['total_sessions'] - 1) + 
             session_duration) / self.performance_stats['total_sessions']
        )
        
        print(f"🏁 游戏会话结束: {session_id}, 持续时间: {session_duration:.1f}秒")
        
        # 触发学习
        self._learn_from_session(session)
    
    def make_ai_decision(self, session_id: str, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """AI系统做出决策"""
        if session_id not in self.active_sessions:
            return self._get_default_decision()
        
        session = self.active_sessions[session_id]
        decision_time = time.time()
        
        # 1. 机器学习AI分析
        ml_pattern = self.ml_ai.generate_game_pattern(game_state)
        
        # 2. 强化学习AI决策
        rl_action = self.rl_ai.act(game_state)
        
        # 3. 智能决策系统分析
        decision_result = self.decision_system.make_intelligent_decision(game_state)
        
        # 4. 综合决策
        final_decision = self._combine_ai_decisions(ml_pattern, rl_action, decision_result)
        
        # 记录决策
        decision_record = {
            'timestamp': decision_time,
            'game_state': game_state,
            'ml_pattern': ml_pattern,
            'rl_action': rl_action,
            'decision_result': decision_result,
            'final_decision': final_decision,
            'reasoning': f"ML: {ml_pattern['type']}, RL: {rl_action['type']}, IDS: {decision_result.action_type}"
        }
        
        session.ai_decisions.append(decision_record)
        self.performance_stats['total_decisions'] += 1
        
        return final_decision
    
    def _combine_ai_decisions(self, ml_pattern: Dict[str, Any], 
                             rl_action: Dict[str, Any], 
                             decision_result: Any) -> Dict[str, Any]:
        """综合多个AI系统的决策"""
        # 基于置信度加权决策
        ml_confidence = 0.7
        rl_confidence = 0.6
        ids_confidence = decision_result.confidence
        
        # 计算权重
        total_confidence = ml_confidence + rl_confidence + ids_confidence
        ml_weight = ml_confidence / total_confidence
        rl_weight = rl_confidence / total_confidence
        ids_weight = ids_confidence / total_confidence
        
        # 综合决策
        if decision_result.action_type == 'enemy_spawn':
            # 敌机生成决策
            final_decision = {
                'type': 'enemy_spawn',
                'parameters': {}
            }
            
            # 合并参数
            for key in ['wave_count', 'enemies_per_wave', 'enemy_speed', 'enemy_health']:
                if key in ml_pattern:
                    ml_val = ml_pattern[key]
                    rl_val = rl_action.get(key, ml_val)
                    ids_val = decision_result.parameters.get(key, ml_val)
                    
                    # 加权平均
                    final_decision['parameters'][key] = (
                        ml_val * ml_weight + 
                        rl_val * rl_weight + 
                        ids_val * ids_weight
                    )
                    
                    # 确保是整数
                    if key in ['wave_count', 'enemies_per_wave', 'enemy_speed', 'enemy_health']:
                        final_decision['parameters'][key] = int(round(final_decision['parameters'][key]))
            
            # 添加其他参数
            final_decision['parameters']['enemy_behavior'] = decision_result.parameters.get('enemy_behavior', 'straight')
            final_decision['parameters']['wave_delay'] = decision_result.parameters.get('wave_delay', 3.0)
            
        else:
            # 其他类型的决策
            final_decision = decision_result.parameters.copy()
        
        return final_decision
    
    def _get_default_decision(self) -> Dict[str, Any]:
        """获取默认决策"""
        return {
            'type': 'enemy_spawn',
            'parameters': {
                'type': 'wave',
                'wave_count': 5,
                'enemies_per_wave': 8,
                'wave_delay': 3.0,
                'enemy_speed': 3,
                'enemy_health': 3,
                'enemy_behavior': 'straight'
            }
        }
    
    def update_game_state(self, session_id: str, game_state: Dict[str, Any]):
        """更新游戏状态"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        # 记录游戏状态变化
        if not hasattr(session, 'state_history'):
            session.state_history = []
        
        session.state_history.append({
            'timestamp': time.time(),
            'state': game_state
        })
    
    def record_game_outcome(self, session_id: str, outcome: Dict[str, Any]):
        """记录游戏结果"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.game_outcomes.append(outcome)
    
    def _learn_from_session(self, session: GameSession):
        """从游戏会话中学习"""
        print(f"🧠 从会话 {session.session_id} 中学习...")
        
        # 1. 机器学习AI学习
        if len(session.ai_decisions) > 0 and len(session.game_outcomes) > 0:
            # 获取最后一个决策和结果
            last_decision = session.ai_decisions[-1]
            final_outcome = session.game_outcomes[-1]
            
            # 创建学习经验
            experience = LearningExperience(
                state=last_decision['game_state'],
                action=last_decision['final_decision'],
                reward=self._calculate_reward(final_outcome),
                next_state=final_outcome,
                outcome=final_outcome,
                timestamp=time.time(),
                session_id=session.session_id
            )
            
            # 各AI系统学习
            self.ml_ai.learn_from_experience(
                experience.state, 
                experience.action, 
                experience.outcome
            )
            
            self.rl_ai.learn_from_game(
                [d['game_state'] for d in session.ai_decisions],
                [hash(str(d['final_decision'])) % 20 for d in session.ai_decisions],
                final_outcome
            )
            
            self.decision_system.learn_from_decision_outcome(
                last_decision['decision_result'],
                final_outcome
            )
            
            self.learning_optimizer.learn_from_experience(experience)
        
        # 2. 优化游戏参数
        if len(session.game_outcomes) > 0:
            current_params = self._extract_current_params(session)
            performance_metrics = self._extract_performance_metrics(session)
            
            optimization_result = self.learning_optimizer.optimize_game_parameters(
                current_params, performance_metrics
            )
            
            # 应用优化结果
            self._apply_optimization(optimization_result)
        
        print(f"✅ 会话 {session.session_id} 学习完成")
    
    def _calculate_reward(self, outcome: Dict[str, Any]) -> float:
        """计算奖励"""
        reward = 0.0
        
        # 生存时间奖励
        survival_time = outcome.get('survival_time', 0)
        reward += min(survival_time / 60.0, 1.0) * 10
        
        # 击杀奖励
        enemies_killed = outcome.get('enemies_killed', 0)
        reward += min(enemies_killed / 20.0, 1.0) * 5
        
        # 分数奖励
        score = outcome.get('score', 0)
        reward += min(score / 1000.0, 1.0) * 3
        
        # 惩罚项
        damage_taken = outcome.get('damage_taken', 0)
        reward -= min(damage_taken / 100.0, 1.0) * 2
        
        return reward
    
    def _extract_current_params(self, session: GameSession) -> Dict[str, Any]:
        """提取当前游戏参数"""
        if not session.ai_decisions:
            return {}
        
        last_decision = session.ai_decisions[-1]['final_decision']
        return last_decision.get('parameters', {})
    
    def _extract_performance_metrics(self, session: GameSession) -> Dict[str, Any]:
        """提取性能指标"""
        if not session.game_outcomes:
            return {}
        
        final_outcome = session.game_outcomes[-1]
        return {
            'survival_time': final_outcome.get('survival_time', 0),
            'enemies_killed': final_outcome.get('enemies_killed', 0),
            'score': final_outcome.get('score', 0),
            'damage_taken': final_outcome.get('damage_taken', 0)
        }
    
    def _apply_optimization(self, optimization_result):
        """应用优化结果"""
        print(f"🔧 应用优化: {optimization_result.parameter_name} = {optimization_result.old_value} -> {optimization_result.new_value}")
        
        # 这里可以将优化结果应用到游戏配置中
        # 例如更新全局游戏参数，或者通知游戏系统应用新的参数
    
    def get_ai_status(self) -> Dict[str, Any]:
        """获取AI系统状态"""
        return {
            'system_status': self.system_status,
            'performance_stats': self.performance_stats,
            'active_sessions': len(self.active_sessions),
            'total_sessions': len(self.session_history),
            'ml_ai_status': self.ml_ai.device,
            'rl_ai_status': self.rl_ai.device,
            'decision_system_status': self.decision_system.get_system_status(),
            'learning_optimizer_insights': self.learning_optimizer.get_learning_insights()
        }
    
    def save_all_models(self, models_dir='./models'):
        """保存所有AI模型"""
        print("💾 保存所有AI模型...")
        
        self.ml_ai.save_model(f"{models_dir}/ml_game_ai.pth")
        self.rl_ai.save_model(f"{models_dir}/rl_game_ai.pth")
        self.decision_system.save_model(f"{models_dir}/intelligent_decision_system.pth")
        self.learning_optimizer.save_model(f"{models_dir}/ai_learning_optimizer.pth")
        
        print("✅ 所有模型保存完成")
    
    def load_all_models(self, models_dir='./models'):
        """加载所有AI模型"""
        print("📂 加载所有AI模型...")
        
        self.ml_ai.load_model(f"{models_dir}/ml_game_ai.pth")
        self.rl_ai.load_model(f"{models_dir}/rl_game_ai.pth")
        self.decision_system.load_model(f"{models_dir}/intelligent_decision_system.pth")
        self.learning_optimizer.load_model(f"{models_dir}/ai_learning_optimizer.pth")
        
        print("✅ 所有模型加载完成")

# 使用示例
if __name__ == "__main__":
    # 创建AI主控制器
    ai_controller = AIMasterController()
    
    # 开始游戏会话
    player_info = {'name': 'Player1', 'skill_level': 'intermediate'}
    session_id = ai_controller.start_game_session(player_info)
    
    # 模拟游戏状态
    game_state = {
        'player_health': 75,
        'player_score': 450,
        'enemies_killed': 12,
        'survival_time': 45,
        'enemies': [{'speed': 3, 'health': 2}] * 8,
        'power_ups': [{'type': 'health'}] * 2,
        'ai_difficulty': 1.2,
        'frame_count': 2700
    }
    
    # AI做出决策
    decision = ai_controller.make_ai_decision(session_id, game_state)
    print(f"🤖 AI决策: {decision}")
    
    # 更新游戏状态
    ai_controller.update_game_state(session_id, game_state)
    
    # 模拟游戏结果
    outcome = {
        'survival_time': 67,
        'enemies_killed': 18,
        'score': 720,
        'damage_taken': 45
    }
    
    # 记录结果
    ai_controller.record_game_outcome(session_id, outcome)
    
    # 结束会话
    ai_controller.end_game_session(session_id, outcome)
    
    # 显示AI状态
    status = ai_controller.get_ai_status()
    print(f"📊 AI状态: {status}")
    
    # 保存模型
    ai_controller.save_all_models()
