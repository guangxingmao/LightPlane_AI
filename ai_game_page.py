import pygame
import sys
import os
import random
import math
import colorsys
import time

# 导入游戏相关模块
from plane_sprites import *
from game_function import check_KEY, check_mouse
from Tools import Music, Button as GameButton

# 导入AI库
from ai_game_rule_generator import AIGameRuleGenerator
from ai_strategy_generator import AIGameStrategyGenerator

# 注意：目前使用优化的简单AI控制器，强化学习控制器暂时未使用

class RandomBackgroundGenerator:
    """随机背景生成器"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.backgrounds = []
        self.current_bg = 0
        self.change_timer = 0
        self.change_interval = 600  # 10秒切换一次背景
        
        # 预生成一些随机背景
        self._generate_backgrounds()
    
    def _generate_backgrounds(self):
        """生成多种随机背景"""
        # 渐变背景
        for i in range(5):
            bg = self._create_gradient_background()
            self.backgrounds.append(bg)
        
        # 星空背景
        for i in range(3):
            bg = self._create_starfield_background()
            self.backgrounds.append(bg)
        
        # 几何图案背景
        for i in range(3):
            bg = self._create_geometric_background()
            self.backgrounds.append(bg)
        
        # 粒子背景
        for i in range(2):
            bg = self._create_particle_background()
            self.backgrounds.append(bg)
    
    def _create_gradient_background(self):
        """创建渐变背景"""
        bg = pygame.Surface((self.screen_width, self.screen_height))
        
        # 随机选择颜色
        color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        color2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        # 创建渐变
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(bg, (r, g, b), (0, y), (self.screen_width, y))
        
        return bg
    
    def _create_starfield_background(self):
        """创建星空背景"""
        bg = pygame.Surface((self.screen_width, self.screen_height))
        bg.fill((0, 0, 20))  # 深蓝色背景
        
        # 添加星星
        for _ in range(200):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(1, 3)
            brightness = random.randint(100, 255)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(bg, color, (x, y), size)
        
        return bg
    
    def _create_geometric_background(self):
        """创建几何图案背景"""
        bg = pygame.Surface((self.screen_width, self.screen_height))
        bg.fill((random.randint(20, 50), random.randint(20, 50), random.randint(20, 50)))
        
        # 添加几何图形
        for _ in range(50):
            shape_type = random.choice(['circle', 'rect', 'triangle'])
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(10, 40)
            color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
            
            if shape_type == 'circle':
                pygame.draw.circle(bg, color, (x, y), size)
            elif shape_type == 'rect':
                rect = pygame.Rect(x - size//2, y - size//2, size, size)
                pygame.draw.rect(bg, color, rect)
            elif shape_type == 'triangle':
                points = [(x, y - size), (x - size//2, y + size//2), (x + size//2, y + size//2)]
                pygame.draw.polygon(bg, color, points)
        
        return bg
    
    def _create_particle_background(self):
        """创建粒子背景"""
        bg = pygame.Surface((self.screen_width, self.screen_height))
        bg.fill((0, 0, 0))
        
        # 添加粒子
        for _ in range(100):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(2, 6)
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            pygame.draw.circle(bg, color, (x, y), size)
        
        return bg
    
    def update(self):
        """更新背景"""
        self.change_timer += 1
        if self.change_timer >= self.change_interval:
            self.current_bg = (self.current_bg + 1) % len(self.backgrounds)
            self.change_timer = 0
    
    def get_current_background(self):
        """获取当前背景"""
        return self.backgrounds[self.current_bg]

class RandomKillEffect:
    """随机击杀效果"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.effects = []
        self.life_timer = 60  # 1秒生命周期
        
        # 随机选择效果类型
        effect_type = random.choice(['explosion', 'sparkle', 'rainbow', 'firework', 'magic'])
        if effect_type == 'explosion':
            self._create_explosion_effect()
        elif effect_type == 'sparkle':
            self._create_sparkle_effect()
        elif effect_type == 'rainbow':
            self._create_rainbow_effect()
        elif effect_type == 'firework':
            self._create_firework_effect()
        elif effect_type == 'magic':
            self._create_magic_effect()
    
    def _create_explosion_effect(self):
        """创建爆炸效果"""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            size = random.randint(3, 8)
            color = (random.randint(200, 255), random.randint(100, 150), random.randint(0, 50))
            
            self.effects.append({
                'type': 'particle',
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'life': 30
            })
    
    def _create_sparkle_effect(self):
        """创建闪烁效果"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, 60)
            x = self.x + math.cos(angle) * distance
            y = self.y + math.sin(angle) * distance
            size = random.randint(2, 6)
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(100, 200))
            
            self.effects.append({
                'type': 'sparkle',
                'x': x,
                'y': y,
                'size': size,
                'color': color,
                'life': 45,
                'alpha': 255
            })
    
    def _create_rainbow_effect(self):
        """创建彩虹效果"""
        for i in range(12):
            angle = i * (2 * math.pi / 12)
            distance = 40
            x = self.x + math.cos(angle) * distance
            y = self.y + math.sin(angle) * distance
            
            # 彩虹颜色
            hue = i / 12
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            self.effects.append({
                'type': 'rainbow',
                'x': x,
                'y': y,
                'size': 8,
                'color': color,
                'life': 60,
                'angle': angle
            })
    
    def _create_firework_effect(self):
        """创建烟花效果"""
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10)
            size = random.randint(4, 10)
            color = (random.randint(150, 255), random.randint(100, 200), random.randint(50, 150))
            
            self.effects.append({
                'type': 'firework',
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'life': 50,
                'gravity': 0.2
            })
    
    def _create_magic_effect(self):
        """创建魔法效果"""
        for _ in range(18):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(15, 45)
            x = self.x + math.cos(angle) * distance
            y = self.y + math.sin(angle) * distance
            size = random.randint(3, 7)
            color = (random.randint(100, 200), random.randint(100, 200), random.randint(200, 255))
            
            self.effects.append({
                'type': 'magic',
                'x': x,
                'y': y,
                'size': size,
                'color': color,
                'life': 40,
                'rotation': random.uniform(0, 2 * math.pi)
            })
    
    def update(self):
        """更新效果"""
        self.life_timer -= 1
        
        # 更新所有子效果
        for effect in self.effects[:]:
            effect['life'] -= 1
            
            if effect['type'] == 'particle':
                effect['x'] += effect['dx']
                effect['y'] += effect['dy']
            elif effect['type'] == 'firework':
                effect['x'] += effect['dx']
                effect['y'] += effect['dy']
                effect['dy'] += effect['gravity']
            elif effect['type'] == 'magic':
                effect['rotation'] += 0.1
            
            # 移除过期的效果
            if effect['life'] <= 0:
                self.effects.remove(effect)
    
    def draw(self, screen):
        """绘制效果"""
        for effect in self.effects:
            if effect['type'] == 'particle':
                pygame.draw.circle(screen, effect['color'], 
                                 (int(effect['x']), int(effect['y'])), effect['size'])
            elif effect['type'] == 'sparkle':
                alpha = int(255 * (effect['life'] / 45))
                color = (*effect['color'], alpha)
                pygame.draw.circle(screen, effect['color'], 
                                 (int(effect['x']), int(effect['y'])), effect['size'])
            elif effect['type'] == 'rainbow':
                pygame.draw.circle(screen, effect['color'], 
                                 (int(effect['x']), int(effect['y'])), effect['size'])
            elif effect['type'] == 'firework':
                pygame.draw.circle(screen, effect['color'], 
                                 (int(effect['x']), int(effect['y'])), effect['size'])
            elif effect['type'] == 'magic':
                pygame.draw.circle(screen, effect['color'], 
                                 (int(effect['x']), int(effect['y'])), effect['size'])
    
    def is_alive(self):
        """检查效果是否还活着"""
        return self.life_timer > 0

class RandomItem:
    """Random item - now more precious and rare"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
        
        # Item rarity system - more balanced distribution
        item_weights = {
            'health': 0.4,      # 40% - Health restore (common)
            'shield': 0.25,     # 25% - Shield (uncommon)
            'speed': 0.2,       # 20% - Speed boost (rare)
            'firepower': 0.1,   # 10% - Firepower (epic)
            'bomb': 0.05        # 5%  - Bomb (legendary)
        }
        
        # 根据权重随机选择道具类型
        self.item_type = random.choices(
            list(item_weights.keys()), 
            weights=list(item_weights.values())
        )[0]
        
        self.life_timer = 300  # 5秒生命周期
        self.animation_timer = 0
        self.rarity_level = self._get_rarity_level()
        
        # 根据道具类型和稀有度设置颜色和效果
        self._set_item_properties()
    
    def _get_rarity_level(self):
        """Get item rarity level"""
        rarity_map = {
            'health': 'common',      # Common
            'shield': 'uncommon',    # Uncommon
            'speed': 'rare',         # Rare
            'firepower': 'epic',     # Epic
            'bomb': 'legendary'      # Legendary
        }
        return rarity_map.get(self.item_type, 'common')
    
    def _set_item_properties(self):
        """Set properties based on item type and rarity"""
        rarity_colors = {
            'common': (255, 255, 255),      # White - Common
            'uncommon': (0, 255, 0),        # Green - Uncommon
            'rare': (0, 150, 255),          # Blue - Rare
            'epic': (255, 0, 255),          # Purple - Epic
            'legendary': (255, 215, 0)      # Gold - Legendary
        }
        
        # Base colors
        base_colors = {
            'health': (255, 100, 100),      # Red
            'shield': (100, 100, 255),      # Blue
            'speed': (100, 255, 100),       # Green
            'firepower': (255, 255, 100),   # Yellow
            'bomb': (255, 50, 50)           # Dark Red
        }
        
        # Mix rarity colors with base colors
        rarity_color = rarity_colors[self.rarity_level]
        base_color = base_colors[self.item_type]
        self.color = tuple((r + b) // 2 for r, b in zip(rarity_color, base_color))
        
        # Item symbols
        symbols = {
            'health': '+',
            'shield': 'S',
            'speed': 'SPD',
            'firepower': 'FIRE',
            'bomb': 'BOMB'
        }
        self.symbol = symbols[self.item_type]
        
        # Rarity border color
        self.border_color = rarity_colors[self.rarity_level]
    
    def update(self):
        """Update item"""
        self.life_timer -= 1
        self.animation_timer += 1
        
        # Flash effect - adjust flash frequency based on rarity
        if self.life_timer < 60:  # Flash in last 1 second
            flash_speed = {
                'common': 10,
                'uncommon': 8,
                'rare': 6,
                'epic': 4,
                'legendary': 2
            }
            speed = flash_speed.get(self.rarity_level, 10)
            if self.animation_timer % speed < speed // 2:
                self.color = self.border_color  # Rarity color flash
            else:
                self._set_item_properties()  # Restore original color
    
    def _reset_color(self):
        """Reset color"""
        self._set_item_properties()
    
    def draw(self, screen):
        """Draw item - enhanced visual effects"""
        # Draw rarity glow
        if self.rarity_level in ['rare', 'epic', 'legendary']:
            glow_radius = 20
            glow_alpha = 128
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.border_color, glow_alpha), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))
        
        # Draw item background
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)
        
        # Draw rarity border
        border_width = 3 if self.rarity_level in ['epic', 'legendary'] else 2
        pygame.draw.circle(screen, self.border_color, (self.x, self.y), 15, border_width)
        
        # Draw item symbol
        font = pygame.font.Font(None, 24)
        text = font.render(self.symbol, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
        
        # Draw rarity indicator
        if self.rarity_level in ['epic', 'legendary']:
            rarity_text = font.render('*', True, self.border_color)
            rarity_rect = rarity_text.get_rect(center=(self.x, self.y - 25))
            screen.blit(rarity_text, rarity_rect)
    
    def is_alive(self):
        """检查道具是否还活着"""
        return self.life_timer > 0

class ItemCollectEffect:
    """道具收集效果"""
    
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.effects = []
        self.life_timer = 90  # 1.5秒生命周期
        
        # 根据道具类型创建不同的收集效果
        if item_type == 'health':
            self._create_health_collect_effect()
        elif item_type == 'shield':
            self._create_shield_collect_effect()
        elif item_type == 'speed':
            self._create_speed_collect_effect()
        elif item_type == 'firepower':
            self._create_firepower_collect_effect()
        elif item_type == 'bomb':
            self._create_bomb_collect_effect()
    
    def _create_health_collect_effect(self):
        """创建生命道具收集效果"""
        # 心形粒子效果
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            size = random.randint(4, 8)
            
            self.effects.append({
                'type': 'heart',
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': (255, 100, 100),
                'life': 60,
                'rotation': 0
            })
        
        # 中心心形
        self.effects.append({
            'type': 'center_heart',
            'x': self.x,
            'y': self.y,
            'size': 20,
            'color': (255, 50, 50),
            'life': 90,
            'scale': 1.0
        })
    
    def _create_shield_collect_effect(self):
        """创建护盾道具收集效果"""
        # 护盾光环效果
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            distance = 30
            x = self.x + math.cos(angle) * distance
            y = self.y + math.sin(angle) * distance
            
            self.effects.append({
                'type': 'shield_ring',
                'x': x,
                'y': y,
                'size': 6,
                'color': (100, 100, 255),
                'life': 75,
                'angle': angle
            })
        
        # 中心护盾
        self.effects.append({
            'type': 'center_shield',
            'x': self.x,
            'y': self.y,
            'size': 25,
            'color': (50, 50, 255),
            'life': 90,
            'rotation': 0
        })
    
    def _create_speed_collect_effect(self):
        """创建速度道具收集效果"""
        # 闪电粒子效果
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4, 10)
            size = random.randint(3, 6)
            
            self.effects.append({
                'type': 'lightning',
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': (100, 255, 100),
                'life': 50,
                'trail_length': 5
            })
        
        # 中心闪电
        self.effects.append({
            'type': 'center_lightning',
            'x': self.x,
            'y': self.y,
            'size': 18,
            'color': (50, 255, 50),
            'life': 90,
            'rotation': 0
        })
    
    def _create_firepower_collect_effect(self):
        """创建火力道具收集效果"""
        # 火焰粒子效果
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            size = random.randint(4, 10)
            
            self.effects.append({
                'type': 'fire',
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': (255, 255, 100),
                'life': 70,
                'gravity': 0.1
            })
        
        # 中心火焰
        self.effects.append({
            'type': 'center_fire',
            'x': self.x,
            'y': self.y,
            'size': 22,
            'color': (255, 200, 50),
            'life': 90,
            'scale': 1.0
        })
    
    def _create_bomb_collect_effect(self):
        """创建炸弹道具收集效果"""
        # 爆炸粒子效果
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 12)
            size = random.randint(5, 12)
            
            self.effects.append({
                'type': 'explosion',
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': (255, 50, 50),
                'life': 80,
                'fade_speed': 0.8
            })
        
        # 中心爆炸
        self.effects.append({
            'type': 'center_explosion',
            'x': self.x,
            'y': self.y,
            'size': 30,
            'color': (255, 100, 100),
            'life': 90,
            'scale': 1.0
        })
    
    def update(self):
        """更新道具收集效果"""
        self.life_timer -= 1
        
        # 更新所有子效果
        for effect in self.effects[:]:
            effect['life'] -= 1
            
            # 根据效果类型更新
            if effect['type'] in ['heart', 'lightning', 'fire', 'explosion']:
                effect['x'] += effect['dx']
                effect['y'] += effect['dy']
                
                # 特殊效果
                if effect['type'] == 'fire' and 'gravity' in effect:
                    effect['dy'] += effect['gravity']
                elif effect['type'] == 'explosion' and 'fade_speed' in effect:
                    effect['size'] *= effect['fade_speed']
                elif effect['type'] == 'lightning' and 'trail_length' in effect:
                    effect['trail_length'] = max(0, effect['trail_length'] - 0.2)
            
            elif effect['type'] in ['center_heart', 'center_shield', 'center_lightning', 'center_fire', 'center_explosion']:
                if 'rotation' in effect:
                    effect['rotation'] += 0.1
                if 'scale' in effect:
                    effect['scale'] = 1.0 + math.sin(self.life_timer * 0.2) * 0.3
            
            elif effect['type'] == 'shield_ring':
                effect['angle'] += 0.05
            
            # 移除过期的效果
            if effect['life'] <= 0:
                self.effects.remove(effect)
    
    def draw(self, screen):
        """绘制道具收集效果"""
        for effect in self.effects:
            if effect['type'] == 'heart':
                # 绘制心形粒子
                self._draw_heart(screen, effect)
            elif effect['type'] == 'center_heart':
                # 绘制中心心形
                self._draw_center_heart(screen, effect)
            elif effect['type'] == 'shield_ring':
                # 绘制护盾环
                pygame.draw.circle(screen, effect['color'], 
                                 (int(effect['x']), int(effect['y'])), effect['size'])
            elif effect['type'] == 'center_shield':
                # 绘制中心护盾
                self._draw_center_shield(screen, effect)
            elif effect['type'] == 'lightning':
                # 绘制闪电粒子
                pygame.draw.circle(screen, effect['color'], 
                                 (int(effect['x']), int(effect['y'])), effect['size'])
            elif effect['type'] == 'center_lightning':
                # 绘制中心闪电
                self._draw_center_lightning(screen, effect)
            elif effect['type'] == 'fire':
                # 绘制火焰粒子
                pygame.draw.circle(screen, effect['color'], 
                                 (int(effect['x']), int(effect['y'])), effect['size'])
            elif effect['type'] == 'center_fire':
                # 绘制中心火焰
                self._draw_center_fire(screen, effect)
            elif effect['type'] == 'explosion':
                # 绘制爆炸粒子
                pygame.draw.circle(screen, effect['color'], 
                                 (int(effect['x']), int(effect['y'])), effect['size'])
            elif effect['type'] == 'center_explosion':
                # 绘制中心爆炸
                self._draw_center_explosion(screen, effect)
    
    def _draw_heart(self, screen, effect):
        """绘制心形"""
        x, y = int(effect['x']), int(effect['y'])
        size = effect['size']
        color = effect['color']
        
        # 简化的心形绘制
        points = [
            (x, y - size//2),
            (x - size//2, y - size//2),
            (x - size//2, y),
            (x, y + size//2),
            (x + size//2, y),
            (x + size//2, y - size//2)
        ]
        pygame.draw.polygon(screen, color, points)
    
    def _draw_center_heart(self, screen, effect):
        """绘制中心心形"""
        x, y = int(effect['x']), int(effect['y'])
        size = int(effect['size'] * effect['scale'])
        color = effect['color']
        
        # 绘制大心形
        points = [
            (x, y - size//2),
            (x - size//2, y - size//2),
            (x - size//2, y),
            (x, y + size//2),
            (x + size//2, y),
            (x + size//2, y - size//2)
        ]
        pygame.draw.polygon(screen, color, points)
    
    def _draw_center_shield(self, screen, effect):
        """绘制中心护盾"""
        x, y = int(effect['x']), int(effect['y'])
        size = effect['size']
        color = effect['color']
        
        # 绘制护盾形状
        points = [
            (x, y - size//2),
            (x - size//2, y),
            (x - size//3, y + size//2),
            (x + size//3, y + size//2),
            (x + size//2, y)
        ]
        pygame.draw.polygon(screen, color, points)
    
    def _draw_center_lightning(self, screen, effect):
        """绘制中心闪电"""
        x, y = int(effect['x']), int(effect['y'])
        size = effect['size']
        color = effect['color']
        
        # 绘制闪电形状
        points = [
            (x, y - size//2),
            (x - size//3, y - size//4),
            (x + size//4, y),
            (x - size//4, y + size//4),
            (x, y + size//2)
        ]
        pygame.draw.polygon(screen, color, points)
    
    def _draw_center_fire(self, screen, effect):
        """绘制中心火焰"""
        x, y = int(effect['x']), int(effect['y'])
        size = int(effect['size'] * effect['scale'])
        color = effect['color']
        
        # 绘制火焰形状
        points = [
            (x, y - size//2),
            (x - size//3, y - size//4),
            (x - size//4, y),
            (x - size//3, y + size//4),
            (x, y + size//2),
            (x + size//3, y + size//4),
            (x + size//4, y),
            (x + size//3, y - size//4)
        ]
        pygame.draw.polygon(screen, color, points)
    
    def _draw_center_explosion(self, screen, effect):
        """绘制中心爆炸"""
        x, y = int(effect['x']), int(effect['y'])
        size = int(effect['size'] * effect['scale'])
        color = effect['color']
        
        # 绘制爆炸形状
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            end_x = x + math.cos(angle) * size
            end_y = y + math.sin(angle) * size
            pygame.draw.line(screen, color, (x, y), (end_x, end_y), 3)
    
    def is_alive(self):
        """检查效果是否还活着"""
        return self.life_timer > 0

class RandomBulletEffect:
    """随机子弹效果"""
    
    def __init__(self, bullet):
        self.bullet = bullet
        self.effect_type = random.choice(['trail', 'glow', 'sparkle', 'rainbow'])
        self.trail_particles = []
        self.max_trail_length = 8
        
        if self.effect_type == 'trail':
            self._create_trail_effect()
        elif self.effect_type == 'glow':
            self._create_glow_effect()
        elif self.effect_type == 'sparkle':
            self._create_sparkle_effect()
        elif self.effect_type == 'rainbow':
            self._create_rainbow_effect()
    
    def _create_trail_effect(self):
        """创建拖尾效果"""
        pass  # 在update中实现
    
    def _create_glow_effect(self):
        """创建发光效果"""
        pass  # 在draw中实现
    
    def _create_sparkle_effect(self):
        """创建闪烁效果"""
        pass  # 在update中实现
    
    def _create_rainbow_effect(self):
        """创建彩虹效果"""
        pass  # 在draw中实现
    
    def update(self):
        """更新子弹效果"""
        if self.effect_type == 'trail':
            # 添加拖尾粒子
            self.trail_particles.append({
                'x': self.bullet.rect.centerx,
                'y': self.bullet.rect.centery,
                'life': 20
            })
            
            # 限制拖尾长度
            if len(self.trail_particles) > self.max_trail_length:
                self.trail_particles.pop(0)
            
            # 更新拖尾粒子
            for particle in self.trail_particles:
                particle['life'] -= 1
    
    def draw(self, screen):
        """绘制子弹效果"""
        if self.effect_type == 'trail':
            # 绘制拖尾
            for i, particle in enumerate(self.trail_particles):
                alpha = int(255 * (particle['life'] / 20))
                size = max(1, int(3 * (particle['life'] / 20)))
                color = (255, 255, 255, alpha)
                pygame.draw.circle(screen, color, 
                                 (int(particle['x']), int(particle['y'])), size)
        
        elif self.effect_type == 'glow':
            # 绘制发光效果
            glow_surface = pygame.Surface((self.bullet.rect.width + 10, self.bullet.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 255, 50), 
                             (glow_surface.get_width()//2, glow_surface.get_height()//2), 8)
            screen.blit(glow_surface, (self.bullet.rect.x - 5, self.bullet.rect.y - 5))
        
        elif self.effect_type == 'sparkle':
            # 绘制闪烁效果
            if random.random() < 0.3:  # 30%概率闪烁
                sparkle_size = random.randint(2, 4)
                sparkle_x = self.bullet.rect.centerx + random.randint(-10, 10)
                sparkle_y = self.bullet.rect.centery + random.randint(-10, 10)
                pygame.draw.circle(screen, (255, 255, 255), (sparkle_x, sparkle_y), sparkle_size)
        
        elif self.effect_type == 'rainbow':
            # 绘制彩虹效果
            rainbow_colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), 
                             (0, 255, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]
            color_index = int(pygame.time.get_ticks() / 100) % len(rainbow_colors)
            color = rainbow_colors[color_index]
            
            # 绘制彩虹光环
            pygame.draw.circle(screen, color, self.bullet.rect.center, self.bullet.rect.width//2 + 2, 2)

class OptimizedAIController:
    """优化的AI控制器 - 减少卡顿，提高流畅度"""
    
    def __init__(self, hero, enemy_group, screen_width, screen_height, is_player1=True):
        self.hero = hero
        self.enemy_group = enemy_group
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_player1 = is_player1
        
        # 优化参数 - 减少抖动
        self.decision_timer = 0
        self.decision_interval = 60  # 每60帧做一次决策，减少抖动
        self.movement_pattern = 'patrol'
        self.last_move_time = 0
        self.move_duration = 120  # 每次移动持续120帧，让移动更稳定
        
        # 移动目标
        self.target_x = 0
        self.target_y = 0
        self.moving = False
        
        # 添加移动平滑参数
        self.last_position = None
        self.position_change_threshold = 15  # 位置变化阈值，避免微小抖动
        self.stable_time = 0  # 稳定时间计数器
        
        # 根据是玩家1还是玩家2设置不同的行为模式
        if is_player1:
            self.patrol_center_x = self.screen_width * 0.25
            self.patrol_center_y = self.screen_height * 0.5
        else:
            # AI飞机现在在左下角，巡逻中心也调整到左侧
            self.patrol_center_x = self.screen_width * 0.25
            self.patrol_center_y = self.screen_height * 0.75
        
        # 初始化目标位置
        self.target_x = self.patrol_center_x
        self.target_y = self.patrol_center_y
        
    def update(self, game_started=True, game_paused=False):
        """更新AI决策和移动"""
        # 如果游戏未开始或已暂停，不执行AI逻辑
        if not game_started or game_paused:
            return
            
        self.decision_timer += 1
        
        # 减少决策频率，但保持移动流畅
        if self.decision_timer >= self.decision_interval:
            self.make_decision()
            self.decision_timer = 0
            self.last_move_time = 0
        
        # 持续执行移动，让移动更流畅
        if self.moving and self.last_move_time < self.move_duration:
            self.execute_movement()
            self.last_move_time += 1
        elif self.last_move_time >= self.move_duration:
            self.moving = False
    
    def make_decision(self):
        """AI决策逻辑 - 优化减少抖动"""
        # 寻找最近的敌人
        nearest_enemy = self.find_nearest_enemy()
        
        if nearest_enemy:
            # 计算与敌人的距离
            distance = self.calculate_distance(self.hero.rect.center, nearest_enemy.rect.center)
            
            # 根据距离决定行为，增加稳定性判断
            if distance < 80:  # 敌人太近时躲避
                if self.movement_pattern != 'evade' or self.stable_time > 30:
                    self.movement_pattern = 'evade'
                    self.set_evade_target(nearest_enemy)
                    self.stable_time = 0
            elif distance < 150:  # 中等距离时追击
                if self.movement_pattern != 'chase' or self.stable_time > 40:
                    self.movement_pattern = 'chase'
                    self.set_chase_target(nearest_enemy)
                    self.stable_time = 0
            else:  # 远距离时巡逻
                if self.movement_pattern != 'patrol' or self.stable_time > 50:
                    self.movement_pattern = 'patrol'
                    self.set_patrol_target()
                    self.stable_time = 0
            
            # 自动射击
            self.auto_shoot(nearest_enemy)
        else:
            # 没有敌人时巡逻，增加稳定性
            if self.movement_pattern != 'patrol' or self.stable_time > 60:
                self.set_patrol_target()
                self.stable_time = 0
        
        # 增加稳定时间
        self.stable_time += 1
    
    def set_chase_target(self, enemy):
        """设置追击目标"""
        # 计算追击位置（稍微偏移，避免直接碰撞）
        dx = enemy.rect.centerx - self.hero.rect.centerx
        dy = enemy.rect.centery - self.hero.rect.centery
        
        # 标准化向量
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            # 追击位置在敌人前方一点
            offset = 30
            self.target_x = enemy.rect.centerx - (dx / length) * offset
            self.target_y = enemy.rect.centery - (dy / length) * offset
            
            # 边界检查
            if self.is_player1:
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            else:
                # AI飞机现在在左下角，限制在左侧区域
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            
            self.target_y = max(50, min(self.screen_height - 50, self.target_y))
            self.moving = True
    
    def set_evade_target(self, enemy):
        """设置躲避目标"""
        # 计算远离方向
        dx = self.hero.rect.centerx - enemy.rect.centerx
        dy = self.hero.rect.centery - enemy.rect.centery
        
        # 标准化向量
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            # 躲避位置在远离敌人的方向
            evade_distance = 100
            self.target_x = self.hero.rect.centerx + (dx / length) * evade_distance
            self.target_y = self.hero.rect.centery + (dy / length) * evade_distance
            
            # 边界检查
            if self.is_player1:
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            else:
                # AI飞机现在在左下角，限制在左侧区域
                self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
            
            self.target_y = max(50, min(self.screen_height - 50, self.target_y))
            self.moving = True
    
    def set_patrol_target(self):
        """设置巡逻目标 - 优化减少抖动"""
        patrol_radius = 80
        
        # 降低巡逻目标变化频率，减少抖动
        if random.random() < 0.1:  # 从30%降低到10%概率改变巡逻目标
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, patrol_radius)
            
            new_target_x = self.patrol_center_x + math.cos(angle) * distance
            new_target_y = self.patrol_center_y + math.sin(angle) * distance
            
            # 检查新目标是否与当前位置差异足够大，避免微小移动
            current_pos = (self.hero.rect.centerx, self.hero.rect.centery)
            new_pos = (new_target_x, new_target_y)
            distance_to_new_target = self.calculate_distance(current_pos, new_pos)
            
            if distance_to_new_target > self.position_change_threshold:
                self.target_x = new_target_x
                self.target_y = new_target_y
                
                # 边界检查
                if self.is_player1:
                    self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
                else:
                    # AI飞机现在在左下角，限制在左侧区域
                    self.target_x = max(50, min(self.screen_width * 0.4, self.target_x))
                
                self.target_y = max(50, min(self.screen_height - 50, self.target_y))
                self.moving = True
    
    def execute_movement(self):
        """执行移动 - 优化减少抖动"""
        if not self.moving:
            return
        
        # 计算到目标的距离
        dx = self.target_x - self.hero.rect.centerx
        dy = self.target_y - self.hero.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        # 如果已经接近目标，停止移动
        if distance < 8:  # 增加停止距离，减少抖动
            self.moving = False
            return
        
        # 动态调整移动速度，距离越近速度越慢
        base_speed = 2
        if distance < 20:
            move_speed = base_speed * 0.5  # 接近目标时减速
        elif distance < 50:
            move_speed = base_speed * 0.8  # 中等距离时中速
        else:
            move_speed = base_speed  # 远距离时全速
        
        if distance > 0:
            dx = (dx / distance) * move_speed
            dy = (dy / distance) * move_speed
        
        # 更新位置
        new_x = self.hero.rect.centerx + dx
        new_y = self.hero.rect.centery + dy
        
        # 边界检查
        if self.is_player1:
            new_x = max(50, min(self.screen_width * 0.4, new_x))
        else:
            # AI飞机现在在左下角，限制在左侧区域
            new_x = max(50, min(self.screen_width * 0.4, new_x))
        
        new_y = max(50, min(self.screen_height - 50, new_y))
        
        # 检查位置变化是否足够大，避免微小抖动
        if self.last_position:
            current_pos = (self.hero.rect.centerx, self.hero.rect.centery)
            new_pos = (new_x, new_y)
            position_change = self.calculate_distance(current_pos, new_pos)
            
            if position_change > 1:  # 只有位置变化大于1像素时才更新
                self.hero.rect.centerx = new_x
                self.hero.rect.centery = new_y
                self.last_position = (new_x, new_y)
        else:
            # 第一次移动，直接更新
            self.hero.rect.centerx = new_x
            self.hero.rect.centery = new_y
            self.last_position = (new_x, new_y)
    
    def find_nearest_enemy(self):
        """找到最近的敌人"""
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in self.enemy_group:
            distance = self.calculate_distance(self.hero.rect.center, enemy.rect.center)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        
        return nearest_enemy
    
    def calculate_distance(self, pos1, pos2):
        """计算两点间距离"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def auto_shoot(self, enemy):
        """自动射击 - 现在由事件系统处理，这里保留方法但不执行射击"""
        # 射击现在由AI_FIRE_EVENT事件自动处理
        pass

class AIGamePage:
    """AI模式游戏页面类 - 玩家1 + AI控制的玩家2"""
    
    def __init__(self, screen):
        # 创建游戏屏幕
        self.screen = screen
        
        # 获取屏幕尺寸
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # 设置窗口的标题
        pygame.display.set_caption('LightPlane Fighter - Player + AI Mode 🤖 + 🎲 随机模式')
        # 创建游戏时钟
        self.clock = pygame.time.Clock()
        
        # 设置AI飞机自动射击事件
        self.AI_FIRE_EVENT = pygame.USEREVENT + 10
        pygame.time.set_timer(self.AI_FIRE_EVENT, 400)  # 每400毫秒发射一次
        
        # 生命数量
        self.life1 = 3
        self.life2 = 3
        # 分数
        self.score1 = 0
        self.score2 = 0
        # AI性能统计
        self.ai_kills = 0
        self.ai_deaths = 0
        
        # 🎲 随机功能系统
        self.random_background = RandomBackgroundGenerator(self.screen_width, self.screen_height)
        self.kill_effects = []  # 击杀效果列表
        self.items = []         # 道具列表
        self.bullet_effects = {}  # 子弹效果字典
        # 🎲 移除道具生成计时器相关变量 - 道具只在击杀敌机后掉落
        # self.item_spawn_timer = 0
        # self.item_spawn_interval = 300  # 每5秒生成一个道具
        
        # 🤖 AI规则和策略系统
        self.rule_generator = AIGameRuleGenerator()
        self.strategy_generator = AIGameStrategyGenerator()
        self.game_rules = self.rule_generator.generate_game_session()
        self.ai_strategy = self.strategy_generator.generate_initial_strategy()
        
        # AI系统状态
        self.ai_difficulty = 1.0
        self.frame_count = 0
        self.game_start_time = time.time()
        self.ai_performance_stats = {
            'survival_time': 0.0,
            'enemies_killed': 0,
            'damage_taken': 0.0,
            'power_ups_collected': 0,
            'accuracy_rate': 0.0
        }
        
        # 特殊事件系统
        self.active_events = {}
        self.event_effects = []
        
        # 设置背景音乐
        self.BGM = Music('./music/bgm.mp3')
        # 创建按钮对象
        self.button = GameButton()

        # 调用私有方法创建精灵组
        self.__creat_sprites()
        
        # 创建玩家2的AI控制器 - 尝试使用训练好的模型
        try:
            from ai_controllers import create_ai_controller
            print("[AI] Trying to use trained AI model...")
            self.ai_controller2 = create_ai_controller(
                self.hero2, self.enemy_group, 
                self.screen_width, self.screen_height, 
                controller_type="hybrid"  # Hybrid mode: prioritize trained model, fallback to simple AI
            )
        except Exception as e:
            print(f"[AI] Trained model loading failed: {e}")
            print("[AI] Using optimized simple AI controller")
            from ai_controllers import OptimizedAIController
            self.ai_controller2 = OptimizedAIController(self.hero2, self.enemy_group, self.screen_width, self.screen_height, False)

    def start_game(self):
        '''开始游戏'''
        while True:
            pygame.init()

            # 判断是否有音乐在播放，如果没有，就播放
            if not pygame.mixer.music.get_busy():
                self.BGM.play_music()
            # 1. 设置刷新帧率
            self.clock.tick(60)
            # 2. 事件监听
            should_quit = self.__check_event()
            if should_quit:
                return "quit"

            # 3. 更新AI（只更新玩家2的AI）
            # 检查游戏是否开始和是否暂停
            game_started = self.button.count_mouse % 2 != 0  # 游戏开始标志（点击后为奇数）
            game_paused = self.button.pause_game % 2 != 0    # 游戏暂停标志
            self.ai_controller2.update(game_started, game_paused)

            # 4. 碰撞检测
            game_over = self.__check_collide()
            if game_over:
                return "game_over"

            # 5. 更新精灵组
            self.__update_sprites()

            # 6. 显示生命和分数
            self.show_life()

            # 7. 更新屏幕显示
            pygame.display.update()
    
    def run_one_frame(self):
        '''运行一帧游戏 - 用于与启动器集成'''
        # 判断是否有音乐在播放，如果没有，就播放
        if not pygame.mixer.music.get_busy():
            self.BGM.play_music()
        
        # 事件监听
        should_quit = self.__check_event()
        if should_quit:
            return "quit"

        # 更新AI（只更新玩家2的AI）
        # 检查游戏是否开始和是否暂停
        game_started = self.button.count_mouse % 2 != 0  # 游戏开始标志（点击后为奇数）
        game_paused = self.button.pause_game % 2 != 0    # 游戏暂停标志
        self.ai_controller2.update(game_started, game_paused)
        
        # 🤖 更新AI规则和策略系统
        if game_started and not game_paused:
            self._update_ai_systems()

        # 碰撞检测
        game_over = self.__check_collide()
        if game_over:
            return "game_over"

        # 更新精灵组
        self.__update_sprites()

        # 显示生命和分数
        self.show_life()
        
        # 🤖 显示AI系统信息
        self._show_ai_info()

        return "running"

    def __check_event(self):
        """事件监听 - 处理玩家1控制和退出暂停"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # 重新生成AI规则
                self._regenerate_ai_rules()
                
            # 处理玩家1的键盘控制
            # 创建虚拟的hero3对象，避免None错误
            dummy_hero3 = type('DummyHero', (), {
                'fire': lambda *args: None, 
                'moving_right': False, 
                'moving_left': False, 
                'moving_up': False, 
                'moving_down': False,
                'time_count': 1
            })()
            # 创建虚拟的hero2对象，防止玩家控制AI飞机
            dummy_hero2 = type('DummyHero', (), {
                'fire': lambda *args: None, 
                'moving_right': False, 
                'moving_left': False, 
                'moving_up': False, 
                'moving_down': False,
                'time_count': 1
            })()
            
            # 只让玩家1响应键盘控制，AI飞机不受玩家控制
            check_KEY(self.hero1, dummy_hero2, dummy_hero3, self.enemy,
                      event, self.enemy_group, self.BGM, self.button)
            
            # 🎲 为玩家1子弹添加随机效果
            if event.type == HERO_FIRE_EVENT and self.hero1.time_count > 0:
                self.hero1.fire()
                # 为刚发射的子弹添加随机效果
                for bullet in self.hero1.bullets:
                    bullet_id = id(bullet)
                    if bullet_id not in self.bullet_effects:
                        effect = RandomBulletEffect(bullet)
                        self.bullet_effects[bullet_id] = effect
            
            # 处理AI飞机自动射击事件
            if event.type == self.AI_FIRE_EVENT:
                # 只有在游戏开始且未暂停时才允许AI射击
                game_started = self.button.count_mouse % 2 != 0
                game_paused = self.button.pause_game % 2 != 0
                if (game_started and not game_paused and 
                    self.life2 > 0 and hasattr(self.hero2, 'time_count') and self.hero2.time_count > 0):
                    self.hero2.fire()
                    
                    # 🎲 为AI子弹添加随机效果
                    for bullet in self.hero2.bullets:
                        bullet_id = id(bullet)
                        if bullet_id not in self.bullet_effects:
                            effect = RandomBulletEffect(bullet)
                            self.bullet_effects[bullet_id] = effect
            
            # 处理鼠标事件（暂停按钮和玩家1移动）
            check_mouse(event, self.button)
            
            # 游戏开始时候，玩家1跟随鼠标移动
            if self.button.pause_game % 2 == 0 and self.button.count_mouse % 2 == 0:
                if event.type == pygame.MOUSEMOTION and self.life1 > 0:
                    (x,y) = pygame.mouse.get_pos()
                    self.hero1.rect.centerx = x
                    self.hero1.rect.centery = y
        
        return False

    def __check_collide(self):
        '''碰撞检测'''
        # 子弹碰撞敌人
        hit_enemies = pygame.sprite.groupcollide(self.hero1.bullets, self.enemy_group, True, True)
        if hit_enemies:
            self.score1 += 1
            # 敌人死亡时，将其子弹转移到全局子弹组，让子弹继续存在
            # hit_enemies的键是子弹，值是敌人列表
            for player_bullet, enemies in hit_enemies.items():
                for enemy in enemies:
                    # 🎲 创建随机击杀效果
                    kill_effect = RandomKillEffect(enemy.rect.centerx, enemy.rect.centery)
                    self.kill_effects.append(kill_effect)
                    print(f"[KILL] Player1 killed enemy at position: ({enemy.rect.centerx}, {enemy.rect.centery})")
                    
                    # 🎲 随机道具掉落（10%概率 - 降低道具产出）
                    if random.random() < 0.1:
                        # 🎯 根据击杀难度增加道具掉落概率
                        # 如果敌机有特殊属性，增加掉落概率
                        bonus_chance = 0.0
                        if hasattr(enemy, 'health') and enemy.health > 1:
                            bonus_chance += 0.05  # 高生命值敌机额外5%概率
                        if hasattr(enemy, 'behavior') and enemy.behavior in ['chase', 'evade']:
                            bonus_chance += 0.03  # 特殊行为敌机额外3%概率
                        
                        # 最终掉落概率
                        final_chance = 0.1 + bonus_chance
                        if random.random() < final_chance:
                            item = RandomItem(enemy.rect.centerx, enemy.rect.centery)
                            self.items.append(item)
                            print(f"[ITEM] Item dropped: {item.item_type} (Kill difficulty bonus: +{bonus_chance:.2f})")
                    
                    # 将敌机的所有子弹复制到全局子弹组，并设置子弹的独立属性
                    for enemy_bullet in enemy.bullets:
                        # 创建新的子弹实例，避免引用问题
                        new_bullet = Bullet_Enemy()
                        new_bullet.rect = enemy_bullet.rect.copy()
                        new_bullet.speed = enemy_bullet.speed
                        self.global_enemy_bullets.add(new_bullet)
                    # 清空敌机的子弹组
                    enemy.bullets.empty()
        
        hit_enemies2 = pygame.sprite.groupcollide(self.hero2.bullets, self.enemy_group, True, True)
        if hit_enemies2:
            self.score2 += 1
            self.ai_kills += 1
            # 敌人死亡时，将其子弹转移到全局子弹组，让子弹继续存在
            # hit_enemies2的键是子弹，值是敌人列表
            for player_bullet, enemies in hit_enemies2.items():
                for enemy in enemies:
                    # 🎲 创建随机击杀效果
                    kill_effect = RandomKillEffect(enemy.rect.centerx, enemy.rect.centery)
                    self.kill_effects.append(kill_effect)
                    print(f"[KILL] AI killed enemy at position: ({enemy.rect.centerx}, {enemy.rect.centery})")
                    
                    # 🎲 随机道具掉落（10%概率 - 降低道具产出）
                    if random.random() < 0.1:
                        # 🎯 根据击杀难度增加道具掉落概率
                        # 如果敌机有特殊属性，增加掉落概率
                        bonus_chance = 0.0
                        if hasattr(enemy, 'health') and enemy.health > 1:
                            bonus_chance += 0.05  # 高生命值敌机额外5%概率
                        if hasattr(enemy, 'behavior') and enemy.behavior in ['chase', 'evade']:
                            bonus_chance += 0.03  # 特殊行为敌机额外3%概率
                        
                        # 最终掉落概率
                        final_chance = 0.1 + bonus_chance
                        if random.random() < final_chance:
                            item = RandomItem(enemy.rect.centerx, enemy.rect.centery)
                            self.items.append(item)
                            print(f"[ITEM] Item dropped: {item.item_type} (Kill difficulty bonus: +{bonus_chance:.2f})")
                    
                    # 将敌机的所有子弹复制到全局子弹组，并设置子弹的独立属性
                    for enemy_bullet in enemy.bullets:
                        # 创建新的子弹实例，避免引用问题
                        new_bullet = Bullet_Enemy()
                        new_bullet.rect = enemy_bullet.rect.copy()
                        new_bullet.speed = enemy_bullet.speed
                        self.global_enemy_bullets.add(new_bullet)
                    # 清空敌机的子弹组
                    enemy.bullets.empty()

        # 敌人碰撞英雄1 (玩家)
        enemys1 = pygame.sprite.spritecollide(
            self.hero1, self.enemy_group, True)
        if len(enemys1) > 0 and self.life1 > 0:
            self.life1 -= 1
            if self.life1 == 0:
                # 英雄死亡后，移除屏幕
                self.hero1.rect.bottom = 0
                self.hero1.rect.x = self.screen_width
                self.hero1.kill()

        # 敌人碰撞英雄2 (AI)
        enemys2 = pygame.sprite.spritecollide(
            self.hero2, self.enemy_group, True)
        if len(enemys2) > 0 and self.life2 > 0:
            self.life2 -= 1
            self.ai_deaths += 1
            if self.life2 == 0:
                self.hero2.rect.bottom = 0
                self.hero2.rect.x = self.screen_width
                self.hero2.kill()
        
        # 敌人子弹碰撞英雄1 (玩家) - 使用全局子弹组
        bullets1 = pygame.sprite.spritecollide(
            self.hero1, self.global_enemy_bullets, True)
        if len(bullets1) > 0 and self.life1 > 0:
            self.life1 -= 1
            if self.life1 == 0:
                # 英雄死亡后，移除屏幕
                self.hero1.rect.bottom = 0
                self.hero1.rect.x = self.screen_width
                self.hero1.kill()

        # 敌人子弹碰撞英雄2 (AI) - 使用全局子弹组
        bullets2 = pygame.sprite.spritecollide(
            self.hero2, self.global_enemy_bullets, True)
        if len(bullets2) > 0 and self.life2 > 0:
            self.life2 -= 1
            self.ai_deaths += 1
            if self.life2 == 0:
                self.hero2.rect.bottom = 0
                self.hero2.rect.x = self.screen_width
                self.hero2.kill()

        # 当两个玩家都死亡，游戏结束
        if self.life1 == 0 and self.life2 == 0:
            # 游戏结束时进化AI策略
            self._evolve_ai_strategy()
            return True
        
        return False
    
    def _update_random_features(self):
        """🎲 更新随机功能"""
        # 更新随机背景
        self.random_background.update()
        
        # 更新击杀效果
        for effect in self.kill_effects[:]:
            effect.update()
            if not effect.is_alive():
                self.kill_effects.remove(effect)
        
        # 更新道具
        for item in self.items[:]:
            item.update()
            if not item.is_alive():
                self.items.remove(item)
        
        # Remove random item spawn timer - items only drop after killing enemies
        # Item spawn timer
        # self.item_spawn_timer += 1
        # if self.item_spawn_timer >= self.item_spawn_interval:
        #     # Random item generation
        #     if random.random() < 0.3:  # 30% chance
        #         x = random.randint(100, self.screen_width - 100)
        #         y = random.randint(100, self.screen_height - 100)
        #         item = RandomItem(x, y)
        #         self.items.append(item)
        #         print(f"[ITEM] Random item generated: {item.item_type} at position: ({x}, {y})")
        #     self.item_spawn_timer = 0
        
        # Check item collection
        self._check_item_collection()
        
        # Update bullet effects
        self._update_bullet_effects()
    
    def _draw_random_features(self):
        """Draw random features"""
        # Draw kill effects
        for effect in self.kill_effects:
            effect.draw(self.screen)
        
        # Draw items
        for item in self.items:
            item.draw(self.screen)
        
        # Draw bullet effects
        for bullet_id, effect in self.bullet_effects.items():
            if hasattr(effect, 'draw'):
                effect.draw(self.screen)
    
    def _check_item_collection(self):
        """Check item collection"""
        for item in self.items[:]:
            # Check if player1 collects item
            if self.hero1.rect.colliderect(item.rect):
                self._apply_item_effect(item, 1)
                self.items.remove(item)
                print(f"[ITEM] Player1 collected item: {item.item_type}")
            
            # Check if player2 collects item
            elif self.hero2.rect.colliderect(item.rect):
                self._apply_item_effect(item, 2)
                self.items.remove(item)
                print(f"[ITEM] AI collected item: {item.item_type}")
    
    def _apply_item_effect(self, item, player_id):
        """Apply item effects"""
        # Create item collection effect
        if player_id == 1:
            effect_pos = (self.hero1.rect.centerx, self.hero1.rect.centery)
        else:
            effect_pos = (self.hero2.rect.centerx, self.hero2.rect.centery)
        
        collect_effect = ItemCollectEffect(effect_pos[0], effect_pos[1], item.item_type)
        self.kill_effects.append(collect_effect)
        
        if item.item_type == 'health':
            if player_id == 1 and self.life1 < 5:
                self.life1 = min(5, self.life1 + 1)
                print(f"[HEALTH] Player1 health restored: {self.life1}")
            elif player_id == 2 and self.life2 < 5:
                self.life2 = min(5, self.life2 + 1)
                print(f"[HEALTH] AI health restored: {self.life2}")
        
        elif item.item_type == 'shield':
            print(f"[SHIELD] Player{player_id} gained shield protection")
            # Add shield logic here
        
        elif item.item_type == 'speed':
            print(f"[SPEED] Player{player_id} speed increased")
            # Add speed boost logic here
        
        elif item.item_type == 'firepower':
            print(f"[FIREPOWER] Player{player_id} firepower enhanced")
            # Add firepower boost logic here
        
        elif item.item_type == 'bomb':
            print(f"[BOMB] Player{player_id} gained bomb")
            # Add bomb logic here
    
    def _update_bullet_effects(self):
        """Update bullet effects"""
        # Clean up destroyed bullet effects
        for bullet_id in list(self.bullet_effects.keys()):
            bullet_exists = False
            
            # Check if bullet still exists
            for hero in [self.hero1, self.hero2]:
                for bullet in hero.bullets:
                    if id(bullet) == bullet_id:
                        bullet_exists = True
                        # Update bullet effect
                        if bullet_id in self.bullet_effects:
                            self.bullet_effects[bullet_id].update()
                        break
                if bullet_exists:
                    break
            
            # 如果子弹不存在了，移除对应的效果
            if not bullet_exists:
                del self.bullet_effects[bullet_id]

    def __update_sprites(self):
        '''更新精灵组'''

        if self.button.pause_game % 2 != 0:
            # 🎲 绘制随机背景
            self.screen.blit(self.random_background.get_current_background(), (0, 0))
            
            # 绘制所有精灵组
            for group in [self.hero_group1, self.hero_group2, self.hero1.bullets, self.hero2.bullets, self.enemy_group, self.global_enemy_bullets]: 
                group.draw(self.screen)
            
            # 🎲 绘制随机功能
            self._draw_random_features()
            
            self.button.update()
            # 重新设置按钮位置到左下角
            self.button.rect.x = 20
            self.button.rect.bottom = self.screen_height - 20
            self.screen.blit(self.button.image,(self.button.rect.x,self.button.rect.y))

        elif self.button.pause_game % 2 == 0:
            # 🎲 绘制随机背景
            self.screen.blit(self.random_background.get_current_background(), (0, 0))
            
            # 绘制和更新所有精灵组
            for group in [self.hero_group1, self.hero_group2, self.hero1.bullets, self.hero2.bullets, self.enemy_group]:
                group.draw(self.screen)
                group.update()
            # 绘制和更新全局敌人子弹组
            self.global_enemy_bullets.draw(self.screen)
            self.global_enemy_bullets.update()
            
            # 🎲 更新和绘制随机功能
            self._update_random_features()
            self._draw_random_features()
            
            self.button.update()
            # 重新设置按钮位置到左下角
            self.button.rect.x = 20
            self.button.rect.bottom = self.screen_height - 20
            self.screen.blit(self.button.image,(self.button.rect.x,self.button.rect.y))
        
        # 手动更新背景位置以适应新的屏幕尺寸
        for bg in self.back_group:
            if bg.rect.x <= -self.screen_width:
                bg.rect.x = self.screen_width

    def show_life(self):
        '''显示字体'''
        pygame.font.init()
        pos1 = (0, 0)
        pos2 = (0, 20)
        pos3 = (self.screen_width // 2, 0)
        pos4 = (self.screen_width // 2, 20)
        pos5 = (self.screen_width // 2, 40)
        pos6 = (self.screen_width // 2, 60)
        
        color = (0, 0, 0)
        text1 = f'PLAYER1 LIFE: {self.life1}'
        text2 = f'PLAYER1 SCORE: {self.score1}'
        text3 = f'AI2 LIFE: {self.life2}'
        text4 = f'AI2 SCORE: {self.score2}'
        text5 = f'AI2 KILLS: {self.ai_kills}'
        text6 = f'AI2 DEATHS: {self.ai_deaths}'
        
        try:
            cur_font = pygame.font.SysFont(None, 20)
        except:
            cur_font = pygame.font.Font(None, 20)
            
        text_fmt1 = cur_font.render(text1, 1, color)
        text_fmt2 = cur_font.render(text2, 1, color)
        text_fmt3 = cur_font.render(text3, 1, color)
        text_fmt4 = cur_font.render(text4, 1, color)
        text_fmt5 = cur_font.render(text5, 1, color)
        text_fmt6 = cur_font.render(text6, 1, color)
        
        self.screen.blit(text_fmt1, pos1)
        self.screen.blit(text_fmt2, pos2)
        self.screen.blit(text_fmt3, pos3)
        self.screen.blit(text_fmt4, pos4)
        self.screen.blit(text_fmt5, pos5)
        self.screen.blit(text_fmt6, pos6)

    def __creat_sprites(self):
        '''创建精灵组'''
        # 背景组 - 创建适应屏幕尺寸的背景
        bg1 = Background()
        bg2 = Background(True)
        
        # 调整背景图片大小以适应屏幕
        bg1.image = pygame.transform.scale(bg1.image, (self.screen_width, self.screen_height))
        bg2.image = pygame.transform.scale(bg2.image, (self.screen_width, self.screen_height))
        
        # 重新设置背景位置
        bg1.rect = bg1.image.get_rect()
        bg2.rect = bg2.image.get_rect()
        bg2.rect.x = self.screen_width
        
        self.back_group = pygame.sprite.Group(bg1, bg2)
        # 敌机组
        self.enemy = Enemy()
        self.enemy_group = pygame.sprite.Group()
        # 添加敌人到敌机组
        self.enemy_group.add(self.enemy)
        
        # 全局敌人子弹组 - 管理所有敌人的子弹，即使敌人死亡子弹也继续存在
        self.global_enemy_bullets = pygame.sprite.Group()

        # 英雄组 - 玩家1在左上，AI玩家2在左下
        self.hero1 = Hero('./images/life.png')
        # 设置英雄1在左上角
        self.hero1.rect.x = 50
        self.hero1.rect.y = 50
        self.hero_group1 = pygame.sprite.Group(self.hero1)
        
        self.hero2 = Hero('./images/life.png', wing=2)
        # 设置英雄2在左下角
        self.hero2.rect.x = 50
        self.hero2.rect.y = self.screen_height - 100
        # 确保AI飞机有射击能力
        self.hero2.time_count = 1
        self.hero_group2 = pygame.sprite.Group(self.hero2)
    
    def _update_ai_systems(self):
        """更新AI规则和策略系统"""
        self.frame_count += 1
        
        # 更新AI性能统计
        self.ai_performance_stats['survival_time'] = time.time() - self.game_start_time
        self.ai_performance_stats['enemies_killed'] = self.ai_kills
        # 统计已收集的道具（通过检查道具是否还活着来估算）
        collected_count = len([item for item in self.items if not item.is_alive()])
        self.ai_performance_stats['power_ups_collected'] = collected_count
        
        # 根据AI规则生成敌机
        new_enemies = self.rule_generator.get_dynamic_enemy_spawn(
            self.frame_count, 
            len(self.enemy_group)
        )
        
        for enemy_data in new_enemies:
            # 创建新的敌机
            new_enemy = Enemy()
            new_enemy.rect.x = enemy_data['x']
            new_enemy.rect.y = enemy_data['y']
            new_enemy.speed = enemy_data['speed']
            # 添加自定义属性
            new_enemy.health = enemy_data.get('health', 1)
            new_enemy.behavior = enemy_data.get('behavior', 'straight')
            new_enemy.ai_behavior = enemy_data.get('behavior', 'straight')  # 用于AI控制的属性
            self.enemy_group.add(new_enemy)
        
        # 应用特殊事件
        events = self.rule_generator.apply_special_event(
            self.frame_count,
            self.score1 + self.score2,
            len(self.enemy_group)
        )
        
        self.active_events = events
        
        # 更新AI难度
        player_performance = self._calculate_player_performance()
        self.ai_difficulty = self.rule_generator.get_ai_difficulty_adjustment(
            player_performance
        )
        
        # 应用AI策略到AI控制器
        self._apply_ai_strategy()
    
    def _calculate_player_performance(self) -> float:
        """计算玩家表现"""
        # 计算准确率（简化处理）
        total_shots = self.score1 + self.ai_kills
        if total_shots == 0:
            accuracy = 0.0
        else:
            accuracy = (self.score1 + self.ai_kills) / total_shots
        
        # 综合性能评分 (0-1)
        survival_score = min(1.0, self.ai_performance_stats['survival_time'] / 60.0)
        kill_score = min(1.0, self.ai_performance_stats['enemies_killed'] / 20.0)
        accuracy_score = accuracy
        health_score = (self.life1 + self.life2) / 6.0  # 总生命值比例
        
        performance = (survival_score * 0.3 + kill_score * 0.3 + 
                      accuracy_score * 0.2 + health_score * 0.2)
        
        return performance
    
    def _apply_ai_strategy(self):
        """应用AI策略到AI控制器"""
        if hasattr(self, 'ai_controller2') and hasattr(self.ai_controller2, 'apply_strategy'):
            # 如果AI控制器支持策略应用
            self.ai_controller2.apply_strategy(self.ai_strategy)
        else:
            # 否则通过调整参数来应用策略
            if hasattr(self.ai_controller2, 'aggression'):
                self.ai_controller2.aggression = self.ai_strategy['aggression']
            if hasattr(self.ai_controller2, 'defense'):
                self.ai_controller2.defense = self.ai_strategy['defense']
            if hasattr(self.ai_controller2, 'speed'):
                self.ai_controller2.speed = self.ai_strategy['speed']
    
    def _regenerate_ai_rules(self):
        """Regenerate AI rules and strategies"""
        print("\n[SYSTEM] Regenerating AI game rules...")
        self.game_rules = self.rule_generator.generate_game_session()
        self.ai_strategy = self.strategy_generator.generate_initial_strategy()
        
        # Reset AI system state
        self.frame_count = 0
        self.game_start_time = time.time()
        self.ai_performance_stats = {
            'survival_time': 0.0,
            'enemies_killed': 0,
            'damage_taken': 0.0,
            'power_ups_collected': 0,
            'accuracy_rate': 0.0
        }
        
        # Clear special events
        self.active_events.clear()
        self.event_effects.clear()
        
        print("[SYSTEM] AI rules regeneration completed!")
    
    def _show_ai_info(self):
        """显示AI系统信息"""
        # 在屏幕右上角显示AI信息
        ai_info_text = [
            f"AI难度: {self.ai_difficulty:.2f}",
            f"策略: {self.ai_strategy.get('behavior_patterns', {}).get('combat_style', 'Unknown')}",
            f"攻击性: {self.ai_strategy.get('aggression', 0):.2f}",
            f"防御性: {self.ai_strategy.get('defense', 0):.2f}"
        ]
        
        try:
            font = pygame.font.Font(None, 18)
            for i, text in enumerate(ai_info_text):
                text_surface = font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, (self.screen_width - 200, 10 + i * 20))
        except:
            pass
        
        # 显示特殊事件
        if self.active_events:
            event_text = f"特殊事件: {', '.join(self.active_events.keys())}"
            try:
                event_surface = font.render(event_text, True, (255, 255, 0))
                self.screen.blit(event_surface, (self.screen_width - 300, 80))
            except:
                pass
    
    def _evolve_ai_strategy(self):
        """Evolve AI strategy when game ends"""
        try:
            print("\n[GAME] Game Over!")
            
            # Calculate final performance score
            final_performance = self._calculate_player_performance()
            print(f"[GAME] Final performance score: {final_performance:.3f}")
            
            # Evolve AI strategy
            if hasattr(self, 'strategy_generator'):
                print("[SYSTEM] AI strategy evolving...")
                new_strategy = self.strategy_generator.evolve_strategy(
                    self.ai_strategy, final_performance
                )
                self.ai_strategy = new_strategy
                print("[SYSTEM] AI strategy evolution completed!")
                print(f"[SYSTEM] New strategy ID: {new_strategy.get('strategy_id', 'Unknown')}")
                print(f"[SYSTEM] Generation: {new_strategy.get('generation', 1)}")
                print(f"[SYSTEM] Fitness score: {new_strategy.get('fitness_score', 0):.3f}")
        except Exception as e:
            print(f"[ERROR] AI strategy evolution failed: {e}")

