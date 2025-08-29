#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏策略AI控制器
使用训练好的AI模型生成游戏策略
包括难度调整、敌机生成、道具掉落、背景切换等
"""

import numpy as np
import random
import time
from typing import Dict, List, Any, Optional

try:
    from stable_baselines3 import PPO, DQN, A2C
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False
    print("⚠️ Stable Baselines3 未安装，将使用规则策略生成器")

class GameStrategyController:
    """游戏策略AI控制器"""
    
    def __init__(self, model_path="./models/game_strategy_ppo/final", 
                 env_normalize_path="./models/game_strategy_ppo/env_normalize"):
        self.model_path = model_path
        self.env_normalize_path = env_normalize_path
        
        # AI模型
        self.model = None
        self.obs_normalizer = None
        self.use_ai_model = False
        
        # 策略参数
        self.current_strategy = {
            'difficulty': 0.5,           # 游戏难度 [0.0, 1.0]
            'enemy_spawn_rate': 0.02,    # 敌机生成率 [0.0, 0.1]
            'enemy_bullet_frequency': 0.01,  # 敌机射击频率 [0.0, 0.05]
            'power_up_drop_rate': 0.005,     # 道具掉落率 [0.0, 0.02]
            'background_intensity': 0.5,     # 背景强度 [0.0, 1.0]
            'special_event_chance': 0.1      # 特殊事件概率 [0.0, 0.3]
        }
        
        # 策略历史
        self.strategy_history = []
        self.max_history = 50
        
        # 控制参数
        self.strategy_update_interval = 100  # 每100帧更新一次策略
        self.last_strategy_update = 0
        self.frame_count = 0
        
        # 游戏状态监控
        self.game_state = {
            'score': 0,
            'lives': 3,
            'enemies_active': 0,
            'power_ups_active': 0,
            'bullets_active': 0,
            'background_type': 0,
            'special_event_active': False
        }
        
        # 玩家表现指标
        self.player_performance = {
            'survival_time': 0,
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'damage_taken': 0,
            'accuracy_rate': 0.0,
            'efficiency_score': 0.0
        }
        
        # 尝试加载AI模型
        self._load_ai_model()
        
        print(f"🎯 游戏策略AI控制器初始化完成")
        print(f"   AI模型加载: {self.use_ai_model}")
        print(f"   模型路径: {model_path}")
        print(f"   策略更新间隔: {self.strategy_update_interval}帧")
    
    def _load_ai_model(self):
        """加载AI模型"""
        if not SB3_AVAILABLE:
            print("⚠️ Stable Baselines3 不可用，使用规则策略生成器")
            return
        
        try:
            # 尝试加载模型
            if self.model_path.endswith('ppo') or self.model_path.endswith('PPO'):
                self.model = PPO.load(self.model_path)
            elif self.model_path.endswith('dqn') or self.model_path.endswith('DQN'):
                self.model = DQN.load(self.model_path)
            elif self.model_path.endswith('a2c') or self.model_path.endswith('A2C'):
                self.model = A2C.load(self.model_path)
            else:
                # 尝试自动检测
                try:
                    self.model = PPO.load(self.model_path)
                except:
                    try:
                        self.model = DQN.load(self.model_path)
                    except:
                        self.model = A2C.load(self.model_path)
            
            # 尝试加载环境标准化参数
            try:
                if self.env_normalize_path:
                    self.obs_normalizer = np.load(f"{self.env_normalize_path}.npz")
                    print(f"✅ 环境标准化参数加载成功")
            except:
                print(f"⚠️ 环境标准化参数加载失败，使用原始观察")
            
            self.use_ai_model = True
            print(f"✅ AI模型加载成功: {type(self.model).__name__}")
            
        except Exception as e:
            print(f"❌ AI模型加载失败: {e}")
            print("🔄 使用规则策略生成器作为备用")
            self.use_ai_model = False
            self.model = None
    
    def update(self, game_started=True, game_paused=False):
        """更新游戏策略"""
        if not game_started or game_paused:
            return
        
        self.frame_count += 1
        
        # 定期更新策略
        if self.frame_count - self.last_strategy_update >= self.strategy_update_interval:
            self._update_strategy()
            self.last_strategy_update = self.frame_count
    
    def _update_strategy(self):
        """更新游戏策略"""
        if self.use_ai_model and self.model:
            # 使用AI模型生成策略
            self._generate_ai_strategy()
        else:
            # 使用规则生成策略
            self._generate_rule_strategy()
        
        # 记录策略历史
        self._record_strategy_change()
        
        print(f"🎯 策略更新 - 帧数: {self.frame_count}")
        print(f"   难度: {self.current_strategy['difficulty']:.3f}")
        print(f"   敌机生成率: {self.current_strategy['enemy_spawn_rate']:.4f}")
        print(f"   敌机射击率: {self.current_strategy['enemy_bullet_frequency']:.4f}")
        print(f"   道具掉落率: {self.current_strategy['power_up_drop_rate']:.4f}")
    
    def _generate_ai_strategy(self):
        """使用AI模型生成策略"""
        try:
            # 获取当前游戏状态观察
            observation = self._get_observation()
            
            # 标准化观察（如果可用）
            if self.obs_normalizer is not None:
                obs_mean = self.obs_normalizer['obs_running_mean']
                obs_var = self.obs_normalizer['obs_running_var']
                observation = (observation - obs_mean) / np.sqrt(obs_var + 1e-8)
            
            # 使用模型预测动作
            action, _ = self.model.predict(observation, deterministic=True)
            
            # 执行策略动作
            self._execute_strategy_action(action)
            
        except Exception as e:
            print(f"❌ AI策略生成失败: {e}")
            print("🔄 回退到规则策略生成")
            self._generate_rule_strategy()
    
    def _generate_rule_strategy(self):
        """使用规则生成策略"""
        # 基于当前游戏状态调整策略
        
        # 难度调整 - 基于玩家表现
        if self.player_performance['efficiency_score'] > 0.5:
            # 玩家表现好，增加难度
            self.current_strategy['difficulty'] = min(1.0, self.current_strategy['difficulty'] + 0.05)
        elif self.player_performance['efficiency_score'] < 0.2:
            # 玩家表现差，降低难度
            self.current_strategy['difficulty'] = max(0.0, self.current_strategy['difficulty'] - 0.05)
        
        # 敌机生成率调整
        target_enemies = 3 + int(self.current_strategy['difficulty'] * 7)
        current_enemies = self.game_state['enemies_active']
        
        if current_enemies < target_enemies:
            # 敌机太少，增加生成率
            self.current_strategy['enemy_spawn_rate'] = min(0.1, self.current_strategy['enemy_spawn_rate'] + 0.001)
        elif current_enemies > target_enemies + 2:
            # 敌机太多，减少生成率
            self.current_strategy['enemy_spawn_rate'] = max(0.0, self.current_strategy['enemy_spawn_rate'] - 0.001)
        
        # 敌机射击频率调整
        target_bullets = 5 + int(self.current_strategy['difficulty'] * 15)
        current_bullets = self.game_state['bullets_active']
        
        if current_bullets < target_bullets:
            self.current_strategy['enemy_bullet_frequency'] = min(0.05, self.current_strategy['enemy_bullet_frequency'] + 0.0005)
        elif current_bullets > target_bullets + 5:
            self.current_strategy['enemy_bullet_frequency'] = max(0.0, self.current_strategy['enemy_bullet_frequency'] - 0.0005)
        
        # 道具掉落率调整 - 基于玩家生命值
        if self.game_state['lives'] <= 1:
            # 生命值低，增加道具掉落
            self.current_strategy['power_up_drop_rate'] = min(0.02, self.current_strategy['power_up_drop_rate'] + 0.0002)
        elif self.game_state['lives'] >= 3:
            # 生命值高，减少道具掉落
            self.current_strategy['power_up_drop_rate'] = max(0.0, self.current_strategy['power_up_drop_rate'] - 0.0001)
        
        # 背景强度调整 - 基于游戏进程
        survival_ratio = self.player_performance['survival_time'] / max(1, self.frame_count)
        self.current_strategy['background_intensity'] = np.clip(survival_ratio, 0.0, 1.0)
        
        # 特殊事件概率调整 - 基于游戏多样性
        try:
            recent_variety = len(set(strategy.get('action', 0) for strategy in self.strategy_history[-10:]))
            self.current_strategy['special_event_chance'] = np.clip(recent_variety / 10.0, 0.0, 0.3)
        except Exception as e:
            # 如果无法计算多样性，使用默认值
            self.current_strategy['special_event_chance'] = 0.1
    
    def _execute_strategy_action(self, action: int):
        """执行策略调整动作"""
        if action == 0:  # 调整难度
            adjustment = random.uniform(-0.1, 0.1)
            self.current_strategy['difficulty'] = np.clip(
                self.current_strategy['difficulty'] + adjustment, 0.0, 1.0
            )
            
        elif action == 1:  # 调整敌机生成率
            adjustment = random.uniform(-0.005, 0.005)
            self.current_strategy['enemy_spawn_rate'] = np.clip(
                self.current_strategy['enemy_spawn_rate'] + adjustment, 0.0, 0.1
            )
            
        elif action == 2:  # 调整敌机射击频率
            adjustment = random.uniform(-0.002, 0.002)
            self.current_strategy['enemy_bullet_frequency'] = np.clip(
                self.current_strategy['enemy_bullet_frequency'] + adjustment, 0.0, 0.05
            )
            
        elif action == 3:  # 调整道具掉落率
            adjustment = random.uniform(-0.001, 0.001)
            self.current_strategy['power_up_drop_rate'] = np.clip(
                self.current_strategy['power_up_drop_rate'] + adjustment, 0.0, 0.02
            )
            
        elif action == 4:  # 切换背景
            self.current_strategy['background_intensity'] = random.uniform(0.0, 1.0)
            
        elif action == 5:  # 触发特殊事件
            if random.random() < self.current_strategy['special_event_chance']:
                self.game_state['special_event_active'] = True
            else:
                self.game_state['special_event_active'] = False
    
    def _get_observation(self) -> np.ndarray:
        """获取当前游戏状态的观察向量"""
        obs = np.zeros(25, dtype=np.float32)
        
        # 游戏状态 [0-4]
        obs[0] = self.game_state['score'] / 1000.0  # 分数归一化
        obs[1] = self.game_state['lives'] / 3.0     # 生命值比例
        obs[2] = self.game_state['enemies_active'] / 10.0  # 敌人数量比例
        obs[3] = self.game_state['power_ups_active'] / 5.0  # 道具数量比例
        obs[4] = self.game_state['bullets_active'] / 20.0   # 子弹数量比例
        
        # 玩家表现 [5-9]
        obs[5] = self.player_performance['survival_time'] / max(1, self.frame_count)  # 生存时间比例
        obs[6] = self.player_performance['enemies_killed'] / 100.0  # 击杀数归一化
        obs[7] = self.player_performance['power_ups_collected'] / 50.0  # 道具收集数归一化
        obs[8] = self.player_performance['accuracy_rate']  # 命中率
        obs[9] = np.clip(self.player_performance['efficiency_score'], -1.0, 1.0)  # 效率分数
        
        # 游戏平衡 [10-14] - 基于当前策略计算
        challenge_level = (self.game_state['enemies_active'] / 10.0 * 0.6 + 
                          self.game_state['bullets_active'] / 20.0 * 0.4)
        obs[10] = challenge_level
        
        engagement_score = np.clip(
            (self.player_performance['enemies_killed'] / max(1, self.frame_count) * 10 +
             self.player_performance['power_ups_collected'] / max(1, self.frame_count) * 5), 0.0, 1.0
        )
        obs[11] = engagement_score
        
        # 趣味性和多样性
        try:
            strategy_variety = len(set(strategy.get('action', 0) for strategy in self.strategy_history[-10:]))
            special_event_bonus = 0.2 if self.game_state['special_event_active'] else 0.0
            obs[12] = np.clip(strategy_variety / 6.0 + special_event_bonus, 0.0, 1.0)
        except Exception as e:
            # 如果无法计算多样性，使用默认值
            obs[12] = 0.1
        
        obs[13] = self.frame_count / 2000.0  # 难度递进
        obs[14] = len(self.strategy_history) / self.max_history  # 多样性评分
        
        # 策略效果 [15-19]
        obs[15] = self.current_strategy['difficulty']
        obs[16] = self.current_strategy['enemy_spawn_rate'] * 10
        obs[17] = self.current_strategy['enemy_bullet_frequency'] * 20
        obs[18] = self.current_strategy['power_up_drop_rate'] * 50
        obs[19] = self.current_strategy['background_intensity']
        
        # 环境状态 [20-24]
        obs[20] = self.game_state['background_type'] / 3.0
        obs[21] = 1.0 if self.game_state['special_event_active'] else 0.0
        obs[22] = self.frame_count / 2000.0
        obs[23] = len(self.strategy_history) / self.max_history
        obs[24] = 0.0  # 总奖励（游戏中使用时不需要）
        
        return obs
    
    def _record_strategy_change(self):
        """记录策略变化"""
        strategy_record = {
            'frame': self.frame_count,
            'strategy': self.current_strategy.copy(),
            'game_state': self.game_state.copy(),
            'player_performance': self.player_performance.copy(),
            'timestamp': time.time()
        }
        
        self.strategy_history.append(strategy_record)
        
        # 限制历史记录长度
        if len(self.strategy_history) > self.max_history:
            self.strategy_history.pop(0)
    
    def update_game_state(self, game_state: Dict[str, Any]):
        """更新游戏状态"""
        self.game_state.update(game_state)
    
    def update_player_performance(self, performance: Dict[str, Any]):
        """更新玩家表现"""
        self.player_performance.update(performance)
    
    def get_current_strategy(self) -> Dict[str, Any]:
        """获取当前策略"""
        return self.current_strategy.copy()
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """获取策略信息"""
        return {
            'controller_type': '游戏策略AI控制器',
            'ai_model_loaded': self.use_ai_model,
            'model_path': self.model_path,
            'current_strategy': self.current_strategy.copy(),
            'frame_count': self.frame_count,
            'strategy_update_interval': self.strategy_update_interval,
            'strategy_history_length': len(self.strategy_history)
        }
    
    def apply_strategy(self, strategy: Dict[str, Any]):
        """应用外部策略"""
        print(f"🎯 应用外部策略到游戏策略AI")
        for key, value in strategy.items():
            if key in self.current_strategy:
                self.current_strategy[key] = value
                print(f"   {key}: {value}")
    
    def reset(self):
        """重置控制器状态"""
        self.frame_count = 0
        self.last_strategy_update = 0
        self.strategy_history.clear()
        
        # 重置策略参数到默认值
        self.current_strategy = {
            'difficulty': 0.5,
            'enemy_spawn_rate': 0.02,
            'enemy_bullet_frequency': 0.01,
            'power_up_drop_rate': 0.005,
            'background_intensity': 0.5,
            'special_event_chance': 0.1
        }
        
        print(f"🔄 游戏策略AI控制器已重置")

def create_game_strategy_controller(model_path="./models/game_strategy_ppo/final"):
    """创建游戏策略AI控制器的工厂函数"""
    return GameStrategyController(model_path)

if __name__ == "__main__":
    # 测试代码
    print("🧪 测试游戏策略AI控制器...")
    
    controller = GameStrategyController()
    
    # 测试策略生成
    for i in range(5):
        controller.update()
        strategy = controller.get_current_strategy()
        print(f"帧 {i*100}: 难度={strategy['difficulty']:.3f}, "
              f"敌机生成率={strategy['enemy_spawn_rate']:.4f}")
    
    print("✅ 测试完成")
