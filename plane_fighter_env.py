"""
飞机大战强化学习训练环境
使用Gymnasium标准接口，支持Stable Baselines3训练
"""

import os
# 设置SDL为虚拟模式，避免在训练时弹出窗口
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
import math
import random
from typing import Optional, Tuple, Dict, Any

# 导入游戏模块
from plane_sprites import *


class TrainingHero(pygame.sprite.Sprite):
    """训练专用的简化英雄类，避免pygame事件冲突"""
    
    def __init__(self, image_path):
        super().__init__()
        
        # 加载图片
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        
        # 创建子弹组
        self.bullets = pygame.sprite.Group()
        
        # 射击计时器（简化版本）
        self.time_count = 1
        self.fire_cooldown = 0
        
        # 添加存活状态
        self._alive = True
    
    def update(self):
        """更新英雄状态"""
        # 更新子弹
        self.bullets.update()
        
        # 清理超出屏幕的子弹
        for bullet in self.bullets:
            if bullet.rect.bottom < 0:
                bullet.kill()
        
        # 更新射击冷却
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        else:
            self.time_count = 1
    
    def alive(self):
        """检查英雄是否存活"""
        return self._alive
    
    def fire(self):
        """发射子弹"""
        if self.time_count > 0 and self.fire_cooldown <= 0:
            bullet = Bullet_Hero()
            bullet.rect.centerx = self.rect.centerx
            bullet.rect.bottom = self.rect.top
            self.bullets.add(bullet)
            self.fire_cooldown = 10  # 射击冷却时间
            self.time_count = 0
    
    def _find_nearest_enemy(self, enemy_group):
        """找到最近的敌人"""
        if not enemy_group:
            return None
        
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemy_group:
            distance = self._calculate_distance(
                self.rect.center, enemy.rect.center
            )
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        
        return nearest_enemy
    
    def _calculate_distance(self, pos1, pos2):
        """计算两点间距离"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


class PlaneFighterEnv(gym.Env):
    """
    飞机大战训练环境
    
    观察空间: 游戏状态向量 (位置、敌人信息、子弹信息等)
    动作空间: 离散动作 (8个方向移动 + 射击)
    奖励函数: 基于击杀敌人、存活时间、避免碰撞等
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(self, screen_width=1280, screen_height=720, render_mode=None):
        super().__init__()
        
        # 环境参数
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.render_mode = render_mode
        self.max_steps = 5000  # 最大步数
        
        # 游戏状态
        self.step_count = 0
        self.score = 0
        self.lives = 3
        self.is_terminated = False
        self.is_truncated = False
        
        # Pygame初始化（训练时也需要，但不使用显示）
        pygame.init()
        
        if self.render_mode is not None:
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            self.clock = pygame.time.Clock()
        else:
            # 训练时使用虚拟屏幕
            pygame.display.set_mode((1, 1))  # 最小的虚拟屏幕
            self.screen = pygame.Surface((screen_width, screen_height))
            self.clock = None
            
        # 动作空间：9个离散动作
        # 0-7: 8个方向移动, 8: 射击
        self.action_space = spaces.Discrete(9)
        
        # 观察空间：状态向量
        # [hero_x, hero_y, hero_vx, hero_vy, 
        #  enemy1_x, enemy1_y, enemy1_vx, enemy1_vy, enemy1_exists,
        #  enemy2_x, enemy2_y, enemy2_vx, enemy2_vy, enemy2_exists,
        #  bullet1_x, bullet1_y, bullet1_exists,
        #  bullet2_x, bullet2_y, bullet2_exists,
        #  score, lives, step_count_normalized]
        obs_dim = 22
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(obs_dim,), dtype=np.float32
        )
        
        # 游戏精灵初始化
        self.hero = None
        self.enemy_group = None
        self.bullets = None
        self.enemy_bullets = None
        
        # 重置环境
        self.reset()
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """重置环境到初始状态"""
        super().reset(seed=seed)
        
        # 重置游戏状态
        self.step_count = 0
        self.score = 0
        self.lives = 3
        self.is_terminated = False
        self.is_truncated = False
        
        # 创建游戏对象
        self._create_sprites()
        
        # 返回初始观察和信息
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """执行一步动作"""
        if self.is_terminated or self.is_truncated:
            return self._get_observation(), 0.0, self.is_terminated, self.is_truncated, self._get_info()
        
        # 执行动作
        reward = self._execute_action(action)
        
        # 更新游戏状态
        self._update_game()
        
        # 计算奖励
        reward += self._calculate_reward()
        
        # 检查终止条件
        self._check_termination()
        
        # 更新步数
        self.step_count += 1
        if self.step_count >= self.max_steps:
            self.is_truncated = True
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, reward, self.is_terminated, self.is_truncated, info
    
    def render(self):
        """渲染游戏画面"""
        if self.render_mode is None:
            return
            
        if self.screen is None:
            return
            
        # 清空屏幕
        self.screen.fill((0, 0, 0))
        
        # 绘制游戏对象
        if self.hero and self.hero.alive():
            self.screen.blit(self.hero.image, self.hero.rect)
            
        for enemy in self.enemy_group:
            if enemy.alive():
                self.screen.blit(enemy.image, enemy.rect)
        
        for bullet in self.hero.bullets:
            if bullet.alive():
                self.screen.blit(bullet.image, bullet.rect)
                
        for bullet in self.enemy_bullets:
            if bullet.alive():
                self.screen.blit(bullet.image, bullet.rect)
        
        # 显示得分和生命
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        
        if self.render_mode == "human":
            # 显示到实际屏幕（需要实际的pygame显示窗口）
            pass
        elif self.render_mode == "rgb_array":
            return pygame.surfarray.array3d(self.screen)
    
    def close(self):
        """关闭环境"""
        if self.screen is not None:
            pygame.quit()
    
    def _create_sprites(self):
        """创建游戏精灵"""
        # 创建英雄 - 使用训练专用的简化版本
        self.hero = TrainingHero('./images/life.png')
        # 将AI飞机放在屏幕左侧，远离敌人
        self.hero.rect.centerx = self.screen_width // 6
        self.hero.rect.centery = self.screen_height // 2
        
        # 创建敌人组
        self.enemy_group = pygame.sprite.Group()
        
        # 创建敌人子弹组
        self.enemy_bullets = pygame.sprite.Group()
        
        # 初始生成一些敌人 - 减少初始敌人数量，给AI学习空间
        for _ in range(1):  # 只生成1个敌人
            self._spawn_enemy()
    
    def _spawn_enemy(self):
        """生成新敌人 - 避免与AI飞机初始位置冲突"""
        if len(self.enemy_group) < 5:  # 最多5个敌人
            enemy = Enemy()
            # 敌人生成在屏幕中央偏右，避免与AI飞机初始位置冲突
            enemy.rect.x = random.randint(self.screen_width // 2, self.screen_width * 0.7)
            enemy.rect.y = random.randint(50, self.screen_height - 50)
            self.enemy_group.add(enemy)
    
    def _execute_action(self, action: int) -> float:
        """执行动作并返回即时奖励"""
        reward = 0.0
        
        if not self.hero or not self.hero.alive():
            return reward
        
        # 移动动作 (0-7: 8个方向)
        if action < 8:
            # 计算移动方向
            directions = [
                (0, -1),   # 上
                (1, -1),   # 右上
                (1, 0),    # 右
                (1, 1),    # 右下
                (0, 1),    # 下
                (-1, 1),   # 左下
                (-1, 0),   # 左
                (-1, -1),  # 左上
            ]
            
            dx, dy = directions[action]
            move_speed = 5
            
            new_x = self.hero.rect.centerx + dx * move_speed
            new_y = self.hero.rect.centery + dy * move_speed
            
            # 边界检查
            new_x = max(25, min(self.screen_width - 25, new_x))
            new_y = max(25, min(self.screen_height - 25, new_y))
            
            self.hero.rect.centerx = new_x
            self.hero.rect.centery = new_y
            
        # 射击动作 (8)
        elif action == 8:
            if self.hero.time_count > 0:
                self.hero.fire()
                reward += 0.1  # 射击小奖励
        
        return reward
    
    def _update_game(self):
        """更新游戏状态"""
        if not self.hero:
            return
            
        # 更新英雄子弹
        self.hero.bullets.update()
        
        # 更新敌人
        self.enemy_group.update()
        
        # 更新敌人子弹
        self.enemy_bullets.update()
        
        # 随机生成新敌人 - 降低生成频率
        if random.random() < 0.005:  # 0.5%概率生成敌人
            self._spawn_enemy()
        
        # 敌人随机射击
        for enemy in self.enemy_group:
            if random.random() < 0.01:  # 1%概率射击
                # 创建敌人子弹
                bullet = Bullet_Enemy()
                bullet.rect.centerx = enemy.rect.centerx
                bullet.rect.top = enemy.rect.bottom
                self.enemy_bullets.add(bullet)
    
    def _calculate_reward(self) -> float:
        """计算奖励 - 优化版本"""
        reward = 0.0
        
        if not self.hero or not self.hero.alive():
            print(f"AI飞机已死亡，位置: {self.hero.rect.center if self.hero else 'None'}")
            return reward
        
        # 基础存活奖励 - 增加存活的重要性
        reward += 0.1
        
        # 击杀奖励 - 大幅提高击杀奖励
        hit_enemies = pygame.sprite.groupcollide(
            self.hero.bullets, self.enemy_group, True, True
        )
        if hit_enemies:
            kills = len(hit_enemies)
            reward += kills * 50.0  # 大幅提高击杀奖励
            self.score += kills
        
        # 被击中惩罚 - 减少惩罚，避免AI过于保守
        hit_by_enemies = pygame.sprite.spritecollide(
            self.hero, self.enemy_group, True
        )
        if hit_by_enemies:
            print(f"AI飞机被敌人撞击! 位置: {self.hero.rect.center}")
            reward -= 2.0  # 减少惩罚
            self.lives -= 1
        
        # 被子弹击中惩罚
        hit_by_bullets = pygame.sprite.spritecollide(
            self.hero, self.enemy_bullets, True
        )
        if hit_by_bullets:
            reward -= 1.0  # 减少惩罚
            self.lives -= 1
        
        # 位置奖励 - 鼓励在安全区域活动
        if self.hero.rect.centerx < self.screen_width // 3:
            reward += 0.02  # 增加安全区域奖励
        
        # 距离奖励 - 鼓励接近敌人进行攻击
        nearest_enemy = self.hero._find_nearest_enemy(self.enemy_group)
        if nearest_enemy:
            distance = self.hero._calculate_distance(
                self.hero.rect.center, nearest_enemy.rect.center
            )
            if distance < 200:  # 在攻击范围内
                reward += 0.05  # 鼓励接近敌人
        
        # 射击奖励 - 鼓励射击
        if hasattr(self.hero, 'time_count') and self.hero.time_count <= 0:
            reward += 0.01  # 射击后的小奖励
        
        return reward
    
    def _check_termination(self):
        """检查游戏是否结束"""
        if self.lives <= 0:
            self.is_terminated = True
        elif not self.hero or not self.hero.alive():
            self.is_terminated = True
    
    def _get_observation(self) -> np.ndarray:
        """获取当前观察状态"""
        obs = np.zeros(22, dtype=np.float32)
        
        if self.hero and self.hero.alive():
            # 英雄位置 (归一化到[-1, 1])
            obs[0] = (self.hero.rect.centerx / self.screen_width) * 2 - 1
            obs[1] = (self.hero.rect.centery / self.screen_height) * 2 - 1
            obs[2] = 0.0  # 速度暂时设为0
            obs[3] = 0.0
        
        # 敌人信息（最多2个敌人）
        enemies = list(self.enemy_group)[:2]
        for i, enemy in enumerate(enemies):
            offset = 4 + i * 5
            obs[offset] = (enemy.rect.centerx / self.screen_width) * 2 - 1
            obs[offset + 1] = (enemy.rect.centery / self.screen_height) * 2 - 1
            obs[offset + 2] = 0.0  # 速度
            obs[offset + 3] = 0.0
            obs[offset + 4] = 1.0  # 存在标志
        
        # 子弹信息（最多2颗子弹）
        bullets = list(self.enemy_bullets)[:2]
        for i, bullet in enumerate(bullets):
            offset = 14 + i * 3
            obs[offset] = (bullet.rect.centerx / self.screen_width) * 2 - 1
            obs[offset + 1] = (bullet.rect.centery / self.screen_height) * 2 - 1
            obs[offset + 2] = 1.0  # 存在标志
        
        # 游戏状态
        obs[20] = self.score / 100.0  # 归一化得分
        obs[21] = self.step_count / self.max_steps  # 归一化步数
        
        return obs
    
    def _get_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        return {
            "score": self.score,
            "lives": self.lives,
            "step_count": self.step_count,
            "enemies": len(self.enemy_group),
            "bullets": len(self.enemy_bullets),
        }


# 注册环境
gym.register(
    id='PlaneFighter-v0',
    entry_point='plane_fighter_env:PlaneFighterEnv',
    max_episode_steps=5000,
)


if __name__ == "__main__":
    # 测试环境
    env = PlaneFighterEnv(render_mode="rgb_array")
    
    print("开始测试环境...")
    obs, info = env.reset()
    print(f"初始观察空间形状: {obs.shape}")
    print(f"动作空间: {env.action_space}")
    print(f"观察空间: {env.observation_space}")
    
    # 运行几步测试
    for step in range(100):
        action = env.action_space.sample()  # 随机动作
        obs, reward, terminated, truncated, info = env.step(action)
        
        if step % 10 == 0:
            print(f"步数: {step}, 奖励: {reward:.3f}, 得分: {info['score']}, 生命: {info['lives']}")
        
        if terminated or truncated:
            print(f"游戏结束! 最终得分: {info['score']}")
            break
    
    env.close()
    print("环境测试完成!")
