#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成AI战机控制器
使用新训练的集成AI战机模型，能够适应游戏策略AI的动态参数调整
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
    print("⚠️ Stable Baselines3 未安装，将使用规则AI控制器")

class IntegratedAIController:
    """集成AI战机控制器 - 适应动态游戏策略"""
    
    def __init__(self, hero, enemy_group, screen_width, screen_height, 
                 model_path="./models/integrated_plane_ppo/best_model/best_model",
                 env_normalize_path="./models/integrated_plane_ppo/env_normalize"):
        self.hero = hero
        self.enemy_group = enemy_group
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # AI模型
        self.model = None
        self.obs_normalizer = None
        self.use_ai_model = False
        
        # 控制参数
        self.speed = 3
        self.shoot_cooldown = 0
        self.moving = False
        self.target_x = hero.rect.centerx if hero and hasattr(hero, 'rect') else screen_width // 2
        self.target_y = hero.rect.centery if hero and hasattr(hero, 'rect') else screen_height // 2
        self.last_position = None
        
        # 策略适应参数
        self.strategy_adaptation = {
            'difficulty': 0.5,
            'enemy_spawn_rate': 0.02,
            'enemy_bullet_frequency': 0.01,
            'power_up_drop_rate': 0.005
        }
        
        # 性能统计
        self.performance_metrics = {
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'damage_taken': 0,
            'survival_time': 0,
            'efficiency_score': 0.0
        }
        
        # 动作稳定性
        self.action_stability = 0
        self.last_action = 0
        self.position_change_threshold = 2
        
        # 决策参数
        self.decision_interval = 30  # 每30帧做一次决策
        self.last_decision_time = 0
        
        # 尝试加载AI模型
        self._load_ai_model(model_path, env_normalize_path)
        
        print(f"🎯 集成AI战机控制器初始化完成")
        print(f"   AI模型加载: {self.use_ai_model}")
        print(f"   模型路径: {model_path}")
        print(f"   策略适应: 已启用")
        print(f"   决策间隔: {self.decision_interval}帧")
    
    def _load_ai_model(self, model_path, env_normalize_path):
        """加载AI模型"""
        if not SB3_AVAILABLE:
            print("⚠️ Stable Baselines3 不可用，使用规则AI控制器")
            return
        
        try:
            # 尝试加载模型
            if model_path.endswith('ppo') or model_path.endswith('PPO'):
                self.model = PPO.load(model_path)
            elif model_path.endswith('dqn') or model_path.endswith('DQN'):
                self.model = DQN.load(model_path)
            elif model_path.endswith('a2c') or model_path.endswith('A2C'):
                self.model = A2C.load(model_path)
            else:
                # 尝试自动检测
                try:
                    self.model = PPO.load(model_path)
                except:
                    try:
                        self.model = DQN.load(model_path)
                    except:
                        self.model = A2C.load(model_path)
            
            # 尝试加载环境标准化参数
            try:
                if env_normalize_path:
                    self.obs_normalizer = np.load(f"{env_normalize_path}.npz")
                    print(f"✅ 环境标准化参数加载成功")
            except:
                print(f"⚠️ 环境标准化参数加载失败，使用原始观察")
            
            self.use_ai_model = True
            print(f"✅ AI模型加载成功: {type(self.model).__name__}")
            
        except Exception as e:
            print(f"❌ AI模型加载失败: {e}")
            print("🔄 使用规则AI控制器作为备用")
            self.use_ai_model = False
            self.model = None
    
    def update(self, game_started=True, game_paused=False):
        """更新AI控制器"""
        if not game_started or game_paused:
            return
        
        # 更新性能统计
        self._update_performance_metrics()
        
        # 定期决策
        if time.time() - self.last_decision_time >= self.decision_interval / 60.0:
            self._make_decision()
            self.last_decision_time = time.time()
    
    def _update_performance_metrics(self):
        """更新性能指标"""
        if hasattr(self.hero, 'survival_time'):
            self.performance_metrics['survival_time'] = getattr(self.hero, 'survival_time', 0)
        
        # 计算效率分数
        total_actions = max(1, self.performance_metrics['survival_time'])
        kill_efficiency = self.performance_metrics['enemies_killed'] / total_actions
        collection_efficiency = self.performance_metrics['power_ups_collected'] / total_actions
        damage_penalty = self.performance_metrics['damage_taken'] / total_actions
        
        self.performance_metrics['efficiency_score'] = (
            kill_efficiency * 0.6 + 
            collection_efficiency * 0.3 - 
            damage_penalty * 0.1
        )
        self.performance_metrics['efficiency_score'] = max(0.0, min(1.0, self.performance_metrics['efficiency_score']))
    
    def _make_decision(self):
        """做出决策"""
        if self.use_ai_model and self.model:
            # 使用AI模型做决策
            self._ai_decision()
        else:
            # 使用规则AI做决策
            self._rule_decision()
    
    def _ai_decision(self):
        """AI模型决策 - 增强版"""
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
            
            # 🛡️ 安全检查：如果生命值过低，强制使用规则AI
            if getattr(self.hero, 'life', 3) <= 1:
                print("🛡️ 生命值过低，切换到规则AI保护模式")
                self._rule_decision()
                return
            
            # 执行动作
            self._execute_action(action)
            
        except Exception as e:
            print(f"❌ AI决策失败: {e}")
            print("🔄 回退到规则决策")
            self._rule_decision()
    
    def _rule_decision(self):
        """规则AI决策 - 增强生存版"""
        # 🛡️ 优先检查生命值状态
        current_life = getattr(self.hero, 'life', 3)
        
        # 找到最近的敌人
        nearest_enemy = self._find_nearest_enemy()
        
        if nearest_enemy:
            # 计算到敌人的距离
            distance = self._calculate_distance(
                (self.hero.rect.centerx, self.hero.rect.centery),
                (nearest_enemy.rect.centerx, nearest_enemy.rect.centery)
            )
            
            # 🛡️ 生命值低时，优先躲避和生存
            if current_life <= 1:
                print("🛡️ 规则AI保护模式：优先生存")
                self._evade_enemy(nearest_enemy)
                self._move_to_safe_zone()
                return
            
            # 根据距离决定行动
            if distance < 80:  # 敌人太近，紧急躲避
                print("🚨 敌人太近，紧急躲避")
                self._evade_enemy(nearest_enemy)
            elif distance < 150:  # 中等距离，谨慎射击
                print("🎯 中等距离，谨慎射击")
                self._shoot_at_enemy(nearest_enemy)
            else:  # 距离较远，安全接近
                print("📡 距离较远，安全接近")
                self._approach_enemy(nearest_enemy)
        else:
            # 没有敌人，移动到安全区域
            print("🛡️ 无敌人，移动到安全区域")
            self._move_to_safe_zone()
    
    def _execute_action(self, action):
        """执行AI模型的动作"""
        if action == 8:  # 射击
            if hasattr(self.hero, 'fire'):
                self.hero.fire()
                self.last_action = action
        else:  # 移动
            dx, dy = self._action_to_direction(action)
            self._move_hero(dx, dy)
            self.last_action = action
    
    def _action_to_direction(self, action):
        """将动作转换为方向向量"""
        directions = [
            (0, -1),   # 0: 上
            (1, -1),   # 1: 右上
            (1, 0),    # 2: 右
            (1, 1),    # 3: 右下
            (0, 1),    # 4: 下
            (-1, 1),   # 5: 左下
            (-1, 0),   # 6: 左
            (-1, -1),  # 7: 左上
        ]
        
        if 0 <= action < 8:
            return directions[action]
        return (0, 0)
    
    def _move_hero(self, dx, dy):
        """移动英雄"""
        if not hasattr(self.hero, 'rect'):
            return
        
        # 计算新位置
        new_x = self.hero.rect.x + int(dx * self.speed)
        new_y = self.hero.rect.y + int(dy * self.speed)
        
        # 边界检查
        new_x = max(0, min(new_x, self.screen_width - self.hero.rect.width))
        new_y = max(0, min(new_y, self.screen_height - self.hero.rect.height))
        
        # 更新位置
        self.hero.rect.x = new_x
        self.hero.rect.y = new_y
        
        # 检查位置变化
        if self.last_position:
            distance_moved = self._calculate_distance(
                self.last_position, (new_x, new_y)
            )
            if distance_moved > self.position_change_threshold:
                self.action_stability = 0
            else:
                self.action_stability += 1
        
        self.last_position = (new_x, new_y)
    
    def _find_nearest_enemy(self):
        """找到最近的敌人"""
        if not self.enemy_group:
            return None
        
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in self.enemy_group:
            if hasattr(enemy, 'rect'):
                distance = self._calculate_distance(
                    (self.hero.rect.centerx, self.hero.rect.centery),
                    (enemy.rect.centerx, enemy.rect.centery)
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest_enemy = enemy
        
        return nearest_enemy
    
    def _calculate_distance(self, pos1, pos2):
        """计算两点间距离"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def _evade_enemy(self, enemy):
        """躲避敌人"""
        # 计算躲避方向
        dx = self.hero.rect.centerx - enemy.rect.centerx
        dy = self.hero.rect.centery - enemy.rect.centery
        
        # 标准化方向向量
        length = np.sqrt(dx**2 + dy**2)
        if length > 0:
            dx = dx / length
            dy = dy / length
        
        # 移动躲避
        self._move_hero(dx, dy)
    
    def _shoot_at_enemy(self, enemy):
        """射击敌人"""
        if hasattr(self.hero, 'fire'):
            self.hero.fire()
    
    def _approach_enemy(self, enemy):
        """接近敌人"""
        # 计算接近方向
        dx = enemy.rect.centerx - self.hero.rect.centerx
        dy = enemy.rect.centery - self.hero.rect.centery
        
        # 标准化方向向量
        length = np.sqrt(dx**2 + dy**2)
        if length > 0:
            dx = dx / length
            dy = dy / length
        
        # 移动接近
        self._move_hero(dx, dy)
    
    def _explore_or_hold_position(self):
        """探索或保持位置"""
        # 随机探索
        if random.random() < 0.1:  # 10%概率随机移动
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            self._move_hero(dx, dy)
    
    def _get_observation(self):
        """获取当前游戏状态的观察向量"""
        obs = np.zeros(26, dtype=np.float32)
        
        if not hasattr(self.hero, 'rect'):
            return obs
        
        # 英雄信息 [0-3]
        obs[0] = self.hero.rect.centerx / self.screen_width * 2 - 1
        obs[1] = self.hero.rect.centery / self.screen_height * 2 - 1
        obs[2] = 0.0  # 速度x（简化）
        obs[3] = 0.0  # 速度y（简化）
        
        # 敌机信息 [4-11]
        for i, enemy in enumerate(list(self.enemy_group)[:2]):  # 最多2个敌机
            if hasattr(enemy, 'rect'):
                idx = 4 + i * 4
                obs[idx] = enemy.rect.centerx / self.screen_width * 2 - 1
                obs[idx + 1] = enemy.rect.centery / self.screen_height * 2 - 1
                obs[idx + 2] = getattr(enemy, 'speed', 2) / 10.0
                obs[idx + 3] = 1.0  # 存在标志
        
        # 游戏状态 [20-21]
        obs[20] = getattr(self.hero, 'score', 0) / 10000.0
        obs[21] = getattr(self.hero, 'life', 3) / 3.0
        
        # 🎯 策略参数 [22-25] - 匹配训练环境
        obs[22] = self.strategy_adaptation['difficulty']
        obs[23] = self.strategy_adaptation['enemy_spawn_rate'] * 10
        obs[24] = self.strategy_adaptation['enemy_bullet_frequency'] * 20
        obs[25] = self.strategy_adaptation['power_up_drop_rate'] * 50
        
        return obs
    
    def _check_safe_position(self) -> bool:
        """检查是否在安全位置"""
        if not hasattr(self.hero, 'rect'):
            return False
        
        # 屏幕中央相对安全
        safe_x = self.screen_width // 2
        safe_y = self.screen_height - 100  # 底部相对安全
        
        # 检查是否在安全区域
        if (abs(self.hero.rect.centerx - safe_x) < 100 and 
            abs(self.hero.rect.centery - safe_y) < 50):
            return True
        
        return False
    
    def _move_to_safe_zone(self):
        """移动到安全区域"""
        if not hasattr(self.hero, 'rect'):
            return
        
        # 定义安全区域（屏幕底部中央）
        safe_x = self.screen_width // 2
        safe_y = self.screen_height - 80
        
        # 计算到安全区域的方向
        dx = safe_x - self.hero.rect.centerx
        dy = safe_y - self.hero.rect.centery
        
        # 标准化方向向量
        length = np.sqrt(dx**2 + dy**2)
        if length > 0:
            dx = dx / length
            dy = dy / length
        
        # 移动到安全区域
        self._move_hero(dx, dy)
        print(f"🛡️ 移动到安全区域: ({safe_x}, {safe_y})")
    
    def update_strategy_adaptation(self, strategy_params):
        """更新策略适应参数"""
        if strategy_params:
            for key, value in strategy_params.items():
                if key in self.strategy_adaptation:
                    self.strategy_adaptation[key] = value
                    print(f"🎯 策略适应更新: {key} = {value}")
    
    def get_ai_info(self):
        """获取AI信息"""
        return {
            'controller_type': '集成AI战机控制器',
            'ai_model_loaded': self.use_ai_model,
            'model_path': './models/integrated_plane_ppo/final',
            'action_stability': self.action_stability,
            'last_action': self.last_action,
            'moving': self.moving,
            'decision_interval': self.decision_interval,
            'move_speed': self.speed,
            'strategy_adaptation': self.strategy_adaptation.copy(),
            'performance_metrics': self.performance_metrics.copy()
        }
    
    def apply_strategy(self, strategy):
        """应用外部策略"""
        print(f"🎯 应用外部策略到集成AI战机")
        for key, value in strategy.items():
            if key in self.strategy_adaptation:
                self.strategy_adaptation[key] = value
                print(f"   {key}: {value}")
    
    def reset(self):
        """重置控制器状态"""
        self.action_stability = 0
        self.last_action = 0
        self.moving = False
        self.last_position = None
        
        # 重置性能统计
        self.performance_metrics = {
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'damage_taken': 0,
            'survival_time': 0,
            'efficiency_score': 0.0
        }
        
        # 重置策略适应参数
        self.strategy_adaptation = {
            'difficulty': 0.5,
            'enemy_spawn_rate': 0.02,
            'enemy_bullet_frequency': 0.01,
            'power_up_drop_rate': 0.005
        }
        
        print(f"🔄 集成AI战机控制器已重置")

def create_integrated_ai_controller(hero, enemy_group, screen_width, screen_height, 
                                  model_path="./models/integrated_plane_ppo/final"):
    """创建集成AI战机控制器的工厂函数"""
    return IntegratedAIController(hero, enemy_group, screen_width, screen_height, model_path)

if __name__ == "__main__":
    # 测试代码
    print("🧪 测试集成AI战机控制器...")
    
    # 模拟对象
    class MockHero:
        def __init__(self):
            self.rect = type('obj', (object,), {'centerx': 400, 'centery': 500, 'x': 400, 'y': 500, 'width': 50, 'height': 50})()
            self.score = 0
            self.life = 3
        
        def fire(self):
            print("    🔫 射击动作执行")
    
    class MockEnemy:
        def __init__(self, x, y):
            self.rect = type('obj', (object,), {'centerx': x, 'centery': y, 'x': x, 'y': y, 'width': 40, 'height': 40})()
            self.speed = 2
    
    # 创建测试对象
    hero = MockHero()
    enemy_group = [MockEnemy(300, 100), MockEnemy(500, 150)]
    
    # 创建控制器
    controller = IntegratedAIController(hero, enemy_group, 800, 600)
    
    # 测试功能
    print(f"控制器类型: {controller.get_ai_info()['controller_type']}")
    print(f"AI模型加载: {controller.get_ai_info()['ai_model_loaded']}")
    
    # 测试策略适应
    test_strategy = {'difficulty': 0.8, 'enemy_spawn_rate': 0.05}
    controller.update_strategy_adaptation(test_strategy)
    
    print("✅ 测试完成")
