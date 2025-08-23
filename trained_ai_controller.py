"""
训练好的AI控制器
使用Stable Baselines3训练的PPO模型控制飞机
"""

import numpy as np
import math
import os
from typing import Optional

try:
    from stable_baselines3 import PPO
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False
    print("⚠️ Stable Baselines3 未安装，将使用简单AI作为备用")


class TrainedAIController:
    """基于训练模型的AI控制器"""
    
    def __init__(self, hero, enemy_group, screen_width, screen_height, model_path="./models/ppo_plane_fighter_final"):
        self.hero = hero
        self.enemy_group = enemy_group
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.model_path = model_path
        
        # 尝试加载训练好的模型
        self.model = None
        self.use_trained_model = False
        
        if SB3_AVAILABLE:
            self._load_model()
        
        # 如果没有训练好的模型，使用简单AI作为备用
        if not self.use_trained_model:
            print("🤖 使用简单AI控制器作为备用")
            from ai_game_page import OptimizedAIController
            self.backup_ai = OptimizedAIController(hero, enemy_group, screen_width, screen_height, False)
        else:
            self.backup_ai = None
            
        # 动作映射
        self.action_directions = [
            (0, -1),   # 0: 上
            (1, -1),   # 1: 右上
            (1, 0),    # 2: 右
            (1, 1),    # 3: 右下
            (0, 1),    # 4: 下
            (-1, 1),   # 5: 左下
            (-1, 0),   # 6: 左
            (-1, -1),  # 7: 左上
        ]
        
        # 移动参数
        self.move_speed = 5
        self.last_action = 0
        self.action_cooldown = 0
    
    def _load_model(self):
        """加载训练好的模型"""
        try:
            if os.path.exists(f"{self.model_path}.zip"):
                self.model = PPO.load(self.model_path)
                self.use_trained_model = True
                print(f"✅ 成功加载训练模型: {self.model_path}")
            else:
                print(f"⚠️ 模型文件不存在: {self.model_path}.zip")
                print("💡 你可以先运行训练脚本: python train_ai.py --mode train")
        except Exception as e:
            print(f"❌ 加载模型失败: {e}")
    
    def update(self, game_started=True, game_paused=False):
        """更新AI控制"""
        # 如果游戏未开始或已暂停，不执行AI逻辑
        if not game_started or game_paused:
            return
        
        if self.use_trained_model and self.model:
            self._update_with_trained_model()
        elif self.backup_ai:
            self.backup_ai.update(game_started, game_paused)
    
    def _update_with_trained_model(self):
        """使用训练好的模型进行控制"""
        try:
            # 获取当前游戏状态
            observation = self._get_observation()
            
            # 使用模型预测动作
            action, _states = self.model.predict(observation, deterministic=True)
            
            # 执行动作
            self._execute_action(int(action))
            
        except Exception as e:
            print(f"❌ AI控制出错: {e}")
            # 出错时切换到备用AI
            if self.backup_ai:
                self.backup_ai.update(True, False)
    
    def _get_observation(self) -> np.ndarray:
        """获取当前游戏状态观察"""
        obs = np.zeros(22, dtype=np.float32)
        
        if self.hero and hasattr(self.hero, 'rect'):
            # 英雄位置 (归一化到[-1, 1])
            obs[0] = (self.hero.rect.centerx / self.screen_width) * 2 - 1
            obs[1] = (self.hero.rect.centery / self.screen_height) * 2 - 1
            obs[2] = 0.0  # 速度
            obs[3] = 0.0
        
        # 敌人信息（最多2个最近的敌人）
        enemies = self._get_nearest_enemies(2)
        for i, enemy in enumerate(enemies):
            if enemy and hasattr(enemy, 'rect'):
                offset = 4 + i * 5
                obs[offset] = (enemy.rect.centerx / self.screen_width) * 2 - 1
                obs[offset + 1] = (enemy.rect.centery / self.screen_height) * 2 - 1
                obs[offset + 2] = 0.0  # 速度
                obs[offset + 3] = 0.0
                obs[offset + 4] = 1.0  # 存在标志
        
        # 子弹信息（获取最近的敌人子弹）
        enemy_bullets = self._get_nearest_bullets(2)
        for i, bullet in enumerate(enemy_bullets):
            if bullet and hasattr(bullet, 'rect'):
                offset = 14 + i * 3
                obs[offset] = (bullet.rect.centerx / self.screen_width) * 2 - 1
                obs[offset + 1] = (bullet.rect.centery / self.screen_height) * 2 - 1
                obs[offset + 2] = 1.0  # 存在标志
        
        # 游戏状态
        obs[20] = 0.0  # 得分（在实际游戏中不直接使用）
        obs[21] = 0.0  # 步数（在实际游戏中不直接使用）
        
        return obs
    
    def _get_nearest_enemies(self, max_count=2):
        """获取最近的敌人"""
        if not self.hero or not hasattr(self.hero, 'rect'):
            return []
        
        enemies_with_distance = []
        for enemy in self.enemy_group:
            if enemy and hasattr(enemy, 'rect'):
                distance = math.sqrt(
                    (enemy.rect.centerx - self.hero.rect.centerx) ** 2 +
                    (enemy.rect.centery - self.hero.rect.centery) ** 2
                )
                enemies_with_distance.append((distance, enemy))
        
        # 按距离排序，返回最近的几个
        enemies_with_distance.sort(key=lambda x: x[0])
        return [enemy for _, enemy in enemies_with_distance[:max_count]]
    
    def _get_nearest_bullets(self, max_count=2):
        """获取最近的敌人子弹"""
        # 这里需要访问敌人子弹，但由于游戏结构限制，暂时返回空列表
        # 在实际集成时需要传入敌人子弹组
        return []
    
    def _execute_action(self, action: int):
        """执行预测的动作"""
        if not self.hero or not hasattr(self.hero, 'rect'):
            return
        
        # 动作冷却
        if self.action_cooldown > 0:
            self.action_cooldown -= 1
            return
        
        # 移动动作 (0-7: 8个方向)
        if action < 8:
            dx, dy = self.action_directions[action]
            
            new_x = self.hero.rect.centerx + dx * self.move_speed
            new_y = self.hero.rect.centery + dy * self.move_speed
            
            # 边界检查 - 限制在左侧区域（因为AI飞机现在在左下角）
            new_x = max(25, min(self.screen_width * 0.4, new_x))
            new_y = max(25, min(self.screen_height - 25, new_y))
            
            self.hero.rect.centerx = int(new_x)
            self.hero.rect.centery = int(new_y)
        
        # 射击动作 (8)
        elif action == 8:
            if hasattr(self.hero, 'time_count') and self.hero.time_count > 0:
                if hasattr(self.hero, 'fire'):
                    self.hero.fire()
                    self.action_cooldown = 5  # 射击冷却
        
        self.last_action = action


class HybridAIController:
    """混合AI控制器 - 结合训练模型和规则AI"""
    
    def __init__(self, hero, enemy_group, screen_width, screen_height, model_path="./models/ppo_plane_fighter_final"):
        # 创建训练AI控制器
        self.trained_ai = TrainedAIController(hero, enemy_group, screen_width, screen_height, model_path)
        
        # 创建简单AI作为备用
        from ai_game_page import OptimizedAIController
        self.simple_ai = OptimizedAIController(hero, enemy_group, screen_width, screen_height, False)
        
        # 控制参数
        self.use_trained_model = self.trained_ai.use_trained_model
        self.switch_timer = 0
        self.performance_threshold = 100  # 性能阈值
        
        print(f"🤝 混合AI控制器初始化完成")
        print(f"   训练模型可用: {self.use_trained_model}")
    
    def update(self, game_started=True, game_paused=False):
        """更新混合AI控制"""
        if not game_started or game_paused:
            return
        
        if self.use_trained_model:
            # 优先使用训练好的模型
            self.trained_ai.update(game_started, game_paused)
        else:
            # 使用简单AI
            self.simple_ai.update(game_started, game_paused)


# 为了向后兼容，创建一个工厂函数
def create_ai_controller(hero, enemy_group, screen_width, screen_height, controller_type="hybrid"):
    """
    创建AI控制器
    
    Args:
        controller_type: "trained", "simple", "hybrid"
    """
    if controller_type == "trained":
        return TrainedAIController(hero, enemy_group, screen_width, screen_height)
    elif controller_type == "simple":
        from ai_game_page import OptimizedAIController
        return OptimizedAIController(hero, enemy_group, screen_width, screen_height, False)
    else:  # hybrid
        return HybridAIController(hero, enemy_group, screen_width, screen_height)


if __name__ == "__main__":
    print("🧪 测试AI控制器...")
    print(f"📦 Stable Baselines3 可用: {SB3_AVAILABLE}")
    
    # 这里可以添加测试代码
    print("✅ AI控制器模块加载成功")
