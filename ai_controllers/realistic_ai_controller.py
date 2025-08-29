#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实游戏环境AI战机控制器
使用与真实游戏完全匹配的环境训练的模型
"""

import numpy as np
import pygame
import os
import sys
from typing import Dict, Any, List, Tuple

# 导入游戏精灵类
from plane_sprites import Hero, Enemy, Bullet_Hero, Bullet_Enemy

class RealisticAIController:
    """
    真实游戏环境AI战机控制器
    使用与真实游戏完全匹配的环境训练的模型
    """
    
    def __init__(self, hero, enemy_group, screen_width, screen_height, 
                 model_path="./models/realistic_plane_ppo/best_model/best_model",
                 env_normalize_path="./models/realistic_plane_ppo/env_normalize"):
        """
        初始化AI控制器
        
        Args:
            hero: 英雄飞机
            enemy_group: 敌机组
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            model_path: 训练模型路径
            env_normalize_path: 环境标准化参数路径
        """
        self.hero = hero
        self.enemy_group = enemy_group
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 🎯 真实游戏参数 - 与训练环境完全一致
        self.game_params = {
            'enemy_spawn_base_rate': 0.02,      # 基础敌机生成率
            'enemy_bullet_base_rate': 0.01,     # 基础敌机射击率
            'power_up_base_rate': 0.005,        # 基础道具掉落率
            'max_enemies': 8,                   # 最大敌机数量
            'max_enemy_bullets': 20,            # 最大敌机子弹数量
            'max_power_ups': 5,                 # 最大道具数量
        }
        
        # 🤖 AI模型相关
        self.model = None
        self.obs_normalizer = None
        self.model_loaded = False
        
        # 📊 性能统计
        self.performance_stats = {
            'survival_time': 0,
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'damage_taken': 0,
            'last_action': 0,
            'action_stability': 0,
            'last_position': None
        }
        
        # 🎮 游戏状态
        self.frame_count = 0
        self.last_hero_position = None
        
        # 🔧 尝试加载AI模型
        self._load_ai_model(model_path, env_normalize_path)
        
        # 🛡️ 备用规则AI
        self.rule_ai_enabled = True
        self.rule_ai_threshold = 0.3  # 规则AI触发阈值
        
        print(f"🎮 真实游戏环境AI战机控制器初始化完成")
        print(f"   AI模型: {'✅ 已加载' if self.model_loaded else '❌ 未加载'}")
        print(f"   规则AI: {'✅ 已启用' if self.rule_ai_enabled else '❌ 已禁用'}")
    
    def _load_ai_model(self, model_path, env_normalize_path):
        """加载AI模型"""
        try:
            # 检查模型文件是否存在
            if not os.path.exists(model_path + ".zip"):
                print(f"⚠️ AI模型文件不存在: {model_path}")
                return
            
            # 导入Stable Baselines3
            try:
                from stable_baselines3 import PPO
                print("✅ Stable Baselines3 导入成功")
            except ImportError:
                print("❌ Stable Baselines3 未安装，无法加载AI模型")
                return
            
            # 加载模型
            print(f"🤖 正在加载AI模型: {model_path}")
            self.model = PPO.load(model_path)
            
            # 加载环境标准化参数
            if os.path.exists(env_normalize_path + ".pkl"):
                try:
                    from stable_baselines3.common.vec_env import VecNormalize
                    self.obs_normalizer = VecNormalize.load(env_normalize_path, dummy_vec_env=True)
                    print("✅ 环境标准化参数加载成功")
                except Exception as e:
                    print(f"⚠️ 环境标准化参数加载失败: {e}")
            
            self.model_loaded = True
            print("✅ AI模型加载成功!")
            
        except Exception as e:
            print(f"❌ AI模型加载失败: {e}")
            self.model_loaded = False
    
    def update(self, frame_count=None):
        """更新AI控制器"""
        self.frame_count = frame_count or 0
        
        # 更新性能统计
        self._update_performance_stats()
        
        # 选择AI策略
        if self.model_loaded and self._should_use_ai_model():
            self._ai_decision()
        else:
            self._rule_decision()
    
    def _should_use_ai_model(self):
        """判断是否应该使用AI模型"""
        # 如果生命值过低，使用规则AI
        if getattr(self.hero, 'life', 3) <= 1:
            return False
        
        # 如果敌机数量过多，使用规则AI
        if len(self.enemy_group) > 6:
            return False
        
        # 如果最近表现不好，使用规则AI
        if self.performance_stats['damage_taken'] > 2:
            return False
        
        return True
    
    def _ai_decision(self):
        """AI模型决策"""
        try:
            # 获取当前游戏状态观察
            observation = self._get_observation()
            
            # 标准化观察（如果可用）
            if self.obs_normalizer is not None:
                obs_mean = self.obs_normalizer.obs_running_mean
                obs_var = self.obs_normalizer.obs_running_var
                observation = (observation - obs_mean) / np.sqrt(obs_var + 1e-8)
            
            # 使用模型预测动作
            action, _ = self.model.predict(observation, deterministic=True)
            
            # 执行动作
            self._execute_action(action)
            
            # 更新统计
            self.performance_stats['last_action'] = action
            
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
    
    def _get_observation(self):
        """获取当前游戏状态的观察向量 - 与训练环境完全一致"""
        obs = np.zeros(40, dtype=np.float32)
        
        if not hasattr(self.hero, 'rect'):
            return obs
        
        # 英雄信息 [0-3]
        obs[0] = self.hero.rect.centerx / self.screen_width * 2 - 1
        obs[1] = self.hero.rect.centery / self.screen_height * 2 - 1
        obs[2] = 0.0  # 速度x
        obs[3] = 0.0  # 速度y
        
        # 敌机信息 [4-19] - 最多4个敌机
        for i, enemy in enumerate(list(self.enemy_group)[:4]):
            if hasattr(enemy, 'rect'):
                idx = 4 + i * 4
                obs[idx] = enemy.rect.centerx / self.screen_width * 2 - 1
                obs[idx + 1] = enemy.rect.centery / self.screen_height * 2 - 1
                obs[idx + 2] = getattr(enemy, 'speed', 2) / 10.0
                obs[idx + 3] = 1.0  # 存在标志
        
        # 敌机子弹信息 [20-27] - 最多2个子弹
        # 注意：这里需要从游戏状态获取子弹信息
        # 由于当前环境限制，暂时使用模拟数据
        for i in range(2):
            idx = 20 + i * 4
            obs[idx] = 0.0  # 子弹x位置
            obs[idx + 1] = 0.0  # 子弹y位置
            obs[idx + 2] = 0.0  # 子弹速度
            obs[idx + 3] = 0.0  # 存在标志
        
        # 道具信息 [28-31] - 最多1个道具
        # 同样使用模拟数据
        for i in range(1):
            idx = 28 + i * 4
            obs[idx] = 0.0  # 道具x位置
            obs[idx + 1] = 0.0  # 道具y位置
            obs[idx + 2] = 0.0  # 道具速度
            obs[idx + 3] = 0.0  # 存在标志
        
        # 游戏状态 [32-35]
        obs[32] = getattr(self.hero, 'score', 0) / 10000.0
        obs[33] = getattr(self.hero, 'life', 3) / 3.0
        obs[34] = min(self.performance_stats['survival_time'] / 60.0, 1.0)
        obs[35] = min(self.frame_count / 3600.0, 1.0)
        
        # 游戏参数 [36-39]
        obs[36] = self.game_params['enemy_spawn_base_rate'] * 10
        obs[37] = self.game_params['enemy_bullet_base_rate'] * 20
        obs[38] = self.game_params['power_up_base_rate'] * 50
        obs[39] = 0.5  # 基础难度
        
        return obs
    
    def _execute_action(self, action):
        """执行动作"""
        if action == 8:  # 射击
            if hasattr(self.hero, 'fire'):
                self.hero.fire()
        else:  # 移动
            dx, dy = self._action_to_direction(action)
            self._move_hero(dx, dy)
    
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
        new_x = self.hero.rect.x + int(dx * 5)  # 移动速度5像素
        new_y = self.hero.rect.y + int(dy * 5)
        
        # 边界检查
        new_x = max(0, min(new_x, self.screen_width - self.hero.rect.width))
        new_y = max(0, min(new_y, self.screen_height - self.hero.rect.height))
        
        # 更新位置
        self.hero.rect.x = new_x
        self.hero.rect.y = new_y
    
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
        if not hasattr(self.hero, 'rect') or not hasattr(enemy, 'rect'):
            return
        
        # 计算躲避方向
        dx = self.hero.rect.centerx - enemy.rect.centerx
        dy = self.hero.rect.centery - enemy.rect.centery
        
        # 标准化方向向量
        length = np.sqrt(dx**2 + dy**2)
        if length > 0:
            dx = dx / length
            dy = dy / length
        
        # 移动到安全位置
        self._move_hero(dx, dy)
    
    def _shoot_at_enemy(self, enemy):
        """射击敌人"""
        if hasattr(self.hero, 'fire'):
            self.hero.fire()
    
    def _approach_enemy(self, enemy):
        """接近敌人"""
        if not hasattr(self.hero, 'rect') or not hasattr(enemy, 'rect'):
            return
        
        # 计算接近方向
        dx = enemy.rect.centerx - self.hero.rect.centerx
        dy = enemy.rect.centery - self.hero.rect.centery
        
        # 标准化方向向量
        length = np.sqrt(dx**2 + dy**2)
        if length > 0:
            dx = dx / length
            dy = dy / length
        
        # 接近敌人
        self._move_hero(dx * 0.5, dy * 0.5)  # 减速接近
    
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
    
    def _update_performance_stats(self):
        """更新性能统计"""
        # 更新生存时间
        self.performance_stats['survival_time'] += 1/60.0
        
        # 更新位置稳定性
        if hasattr(self.hero, 'rect'):
            current_pos = (self.hero.rect.centerx, self.hero.rect.centery)
            if self.last_hero_position:
                distance = self._calculate_distance(current_pos, self.last_hero_position)
                if distance < 10:  # 位置变化很小
                    self.performance_stats['action_stability'] += 1
                else:
                    self.performance_stats['action_stability'] = max(0, self.performance_stats['action_stability'] - 1)
            
            self.last_hero_position = current_pos
    
    def get_performance_stats(self):
        """获取性能统计"""
        return self.performance_stats.copy()
    
    def get_ai_status(self):
        """获取AI状态"""
        return {
            'model_loaded': self.model_loaded,
            'rule_ai_enabled': self.rule_ai_enabled,
            'current_strategy': 'ai_model' if self.model_loaded and self._should_use_ai_model() else 'rule_ai',
            'performance': self.performance_stats
        }

# 工厂函数
def create_realistic_ai_controller(hero, enemy_group, screen_width, screen_height, 
                                  model_path=None, env_normalize_path=None):
    """创建真实游戏环境AI控制器"""
    if model_path is None:
        model_path = "./models/realistic_plane_ppo/best_model/best_model"
    if env_normalize_path is None:
        env_normalize_path = "./models/realistic_plane_ppo/env_normalize"
    
    return RealisticAIController(
        hero, enemy_group, screen_width, screen_height,
        model_path, env_normalize_path
    )

# 测试代码
if __name__ == "__main__":
    print("🧪 测试真实游戏环境AI控制器...")
    
    # 模拟游戏对象
    class MockHero:
        def __init__(self):
            self.rect = pygame.Rect(640, 600, 50, 50)
            self.score = 0
            self.life = 3
        
        def fire(self):
            print("🔥 射击!")
    
    class MockEnemy:
        def __init__(self, x, y):
            self.rect = pygame.Rect(x, y, 40, 40)
            self.speed = 2
    
    # 创建控制器
    hero = MockHero()
    enemy_group = [MockEnemy(100, 100), MockEnemy(200, 150)]
    
    controller = create_realistic_ai_controller(
        hero, enemy_group, 1280, 720
    )
    
    # 测试更新
    for i in range(5):
        controller.update(i)
        stats = controller.get_performance_stats()
        print(f"步骤 {i+1}: 稳定性={stats['action_stability']}, 生存时间={stats['survival_time']:.2f}")
    
    print("✅ 控制器测试完成!")

