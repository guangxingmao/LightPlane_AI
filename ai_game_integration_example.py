#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI游戏集成示例
展示如何将AI库集成到现有游戏中，增加随机性和智能性
"""

import pygame
import random
import math
import time
from typing import Dict, List, Any
import sys
import os

# 导入AI库
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_game_rule_generator import AIGameRuleGenerator
from ai_strategy_generator import AIGameStrategyGenerator

class AIGameIntegration:
    """AI游戏集成示例"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("AI游戏集成示例")
        self.clock = pygame.time.Clock()
        
        # 初始化AI系统
        self.rule_generator = AIGameRuleGenerator()
        self.strategy_generator = AIGameStrategyGenerator()
        
        # 生成AI游戏规则和策略
        self.game_rules = self.rule_generator.generate_game_session()
        self.ai_strategy = self.strategy_generator.generate_initial_strategy()
        
        # 游戏状态
        self.game_state = {
            'frame_count': 0,
            'player_health': 100,
            'player_score': 0,
            'enemies_killed': 0,
            'power_ups_collected': 0,
            'start_time': time.time(),
            'current_enemies': 0,
            'active_events': {},
            'ai_difficulty': 1.0
        }
        
        # 游戏对象
        self.player = {'x': 400, 'y': 500, 'speed': 5, 'size': 20}
        self.enemies = []
        self.bullets = []
        self.power_ups = []
        self.effects = []
        
        # 性能统计
        self.performance_stats = {
            'shots_fired': 0,
            'shots_hit': 0,
            'damage_taken': 0,
            'survival_time': 0
        }
        
        # 字体
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # 颜色
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'purple': (128, 0, 128),
            'orange': (255, 165, 0)
        }
        
        print("🎮 AI游戏集成示例启动完成！")
        print("📋 游戏规则摘要:")
        print(self.rule_generator.get_session_summary())
        print("\n🧠 AI策略摘要:")
        print(self.strategy_generator.get_strategy_summary())
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self._fire_bullet()
                    elif event.key == pygame.K_r:
                        self._regenerate_ai_rules()
            
            # 更新游戏状态
            self._update_game_state()
            
            # AI决策和行动
            self._ai_decision_making()
            
            # 更新游戏对象
            self._update_game_objects()
            
            # 碰撞检测
            self._check_collisions()
            
            # 渲染
            self._render()
            
            # 帧率控制
            self.clock.tick(60)
            
            # 检查游戏结束条件
            if self.game_state['player_health'] <= 0:
                self._game_over()
                break
        
        pygame.quit()
    
    def _update_game_state(self):
        """更新游戏状态"""
        self.game_state['frame_count'] += 1
        self.game_state['survival_time'] = time.time() - self.game_state['start_time']
        self.game_state['current_enemies'] = len(self.enemies)
        
        # 根据AI规则生成敌机
        new_enemies = self.rule_generator.get_dynamic_enemy_spawn(
            self.game_state['frame_count'], 
            self.game_state['current_enemies']
        )
        
        for enemy_data in new_enemies:
            self.enemies.append({
                'x': enemy_data['x'],
                'y': enemy_data['y'],
                'speed': enemy_data['speed'],
                'health': enemy_data['health'],
                'behavior': enemy_data['behavior'],
                'size': 15
            })
        
        # 根据AI规则生成道具
        power_up = self.rule_generator.get_dynamic_power_up(
            self.game_state['frame_count'],
            self.game_state['player_score']
        )
        
        if power_up:
            self.power_ups.append({
                'x': power_up['x'],
                'y': power_up['y'],
                'type': power_up['type'],
                'effect': power_up['effect'],
                'duration': power_up['duration'],
                'value': power_up['value'],
                'size': 12
            })
        
        # 应用特殊事件
        events = self.rule_generator.apply_special_event(
            self.game_state['frame_count'],
            self.game_state['player_score'],
            self.game_state['current_enemies']
        )
        
        self.game_state['active_events'] = events
        
        # 更新AI难度
        player_performance = self._calculate_player_performance()
        self.game_state['ai_difficulty'] = self.strategy_generator.get_ai_difficulty_adjustment(
            player_performance
        )
    
    def _ai_decision_making(self):
        """AI决策和行动"""
        # 获取当前游戏状态
        current_game_state = {
            'player_health': self.game_state['player_health'],
            'nearby_enemies': len([e for e in self.enemies if abs(e['x'] - self.player['x']) < 200]),
            'power_ups_available': len(self.power_ups),
            'enemies': [{'position': {'x': e['x'], 'y': e['y']}, 
                        'distance': math.sqrt((e['x'] - self.player['x'])**2 + (e['y'] - self.player['y'])**2),
                        'threat_level': 1.0 / (e['health'] + 1)} for e in self.enemies],
            'player_position': {'x': self.player['x'], 'y': self.player['y']},
            'player_ammo': 100,  # 简化处理
            'available_power_ups': [p['type'] for p in self.power_ups]
        }
        
        # 获取AI决策
        ai_decision = self.strategy_generator.get_ai_decision(current_game_state)
        
        # 执行AI决策
        self._execute_ai_decision(ai_decision)
    
    def _execute_ai_decision(self, decision: Dict[str, Any]):
        """执行AI决策"""
        if not decision:
            return
        
        # 执行移动决策
        if 'movement' in decision:
            movement = decision['movement']
            dx = movement.get('dx', 0)
            dy = movement.get('dy', 0)
            
            # 应用AI移动策略（这里只是示例，实际游戏中可能需要更复杂的逻辑）
            if abs(dx) > 0.1 or abs(dy) > 0.1:
                self.player['x'] += dx
                self.player['y'] += dy
                
                # 边界检查
                self.player['x'] = max(20, min(780, self.player['x']))
                self.player['y'] = max(20, min(580, self.player['y']))
        
        # 执行行动决策
        if decision.get('action') == 'attack':
            # AI决定攻击，自动发射子弹
            if self.game_state['frame_count'] % 10 == 0:  # 控制射击频率
                self._fire_bullet()
        
        # 执行资源使用决策
        resource_usage = decision.get('resource_usage', {})
        if resource_usage.get('use_health_pack') and self.game_state['player_health'] < 50:
            self.game_state['player_health'] = min(100, self.game_state['player_health'] + 30)
        if resource_usage.get('use_speed_boost'):
            self.player['speed'] = min(10, self.player['speed'] + 2)
    
    def _fire_bullet(self):
        """发射子弹"""
        bullet = {
            'x': self.player['x'],
            'y': self.player['y'] - 10,
            'speed': 10,
            'size': 5
        }
        self.bullets.append(bullet)
        self.performance_stats['shots_fired'] += 1
    
    def _update_game_objects(self):
        """更新游戏对象"""
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet['y'] -= bullet['speed']
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
        
        # 更新敌机
        for enemy in self.enemies[:]:
            # 根据AI规则调整敌机行为
            if enemy['behavior'] == 'straight':
                enemy['y'] += enemy['speed'] * self.game_state['ai_difficulty']
            elif enemy['behavior'] == 'zigzag':
                enemy['y'] += enemy['speed'] * self.game_state['ai_difficulty']
                enemy['x'] += math.sin(self.game_state['frame_count'] * 0.1) * 2
            elif enemy['behavior'] == 'chase':
                # 追踪玩家
                dx = self.player['x'] - enemy['x']
                dy = self.player['y'] - enemy['y']
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    enemy['x'] += (dx / distance) * enemy['speed'] * 0.5
                    enemy['y'] += (dy / distance) * enemy['speed'] * 0.5
            
            # 移除超出屏幕的敌机
            if enemy['y'] > 600:
                self.enemies.remove(enemy)
        
        # 更新道具
        for power_up in self.power_ups[:]:
            power_up['y'] += 2
            if power_up['y'] > 600:
                self.power_ups.remove(power_up)
        
        # 更新特效
        for effect in self.effects[:]:
            if 'life' in effect:
                effect['life'] -= 1
                if effect['life'] <= 0:
                    self.effects.remove(effect)
    
    def _check_collisions(self):
        """碰撞检测"""
        # 子弹与敌机碰撞
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if (abs(bullet['x'] - enemy['x']) < enemy['size'] and 
                    abs(bullet['y'] - enemy['y']) < enemy['size']):
                    
                    # 敌机受伤
                    enemy['health'] -= 1
                    if enemy['health'] <= 0:
                        self.enemies.remove(enemy)
                        self.game_state['enemies_killed'] += 1
                        self.game_state['player_score'] += 100
                        
                        # 创建击杀特效
                        self.effects.append({
                            'x': enemy['x'],
                            'y': enemy['y'],
                            'type': 'explosion',
                            'life': 30
                        })
                    
                    # 移除子弹
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.performance_stats['shots_hit'] += 1
                    break
        
        # 玩家与敌机碰撞
        for enemy in self.enemies[:]:
            if (abs(self.player['x'] - enemy['x']) < (self.player['size'] + enemy['size']) and
                abs(self.player['y'] - enemy['y']) < (self.player['size'] + enemy['size'])):
                
                self.game_state['player_health'] -= 20
                self.performance_stats['damage_taken'] += 20
                self.enemies.remove(enemy)
                
                # 创建受伤特效
                self.effects.append({
                    'x': self.player['x'],
                    'y': self.player['y'],
                    'type': 'damage',
                    'life': 20
                })
        
        # 玩家与道具碰撞
        for power_up in self.power_ups[:]:
            if (abs(self.player['x'] - power_up['x']) < (self.player['size'] + power_up['size']) and
                abs(self.player['y'] - power_up['y']) < (self.player['size'] + power_up['size'])):
                
                self._apply_power_up(power_up)
                self.power_ups.remove(power_up)
                self.game_state['power_ups_collected'] += 1
    
    def _apply_power_up(self, power_up: Dict[str, Any]):
        """应用道具效果"""
        if power_up['type'] == 'health':
            self.game_state['player_health'] = min(100, self.game_state['player_health'] + 30)
        elif power_up['type'] == 'speed':
            self.player['speed'] = min(10, self.player['speed'] + 2)
        elif power_up['type'] == 'firepower':
            # 增加射击频率
            pass
        elif power_up['type'] == 'shield':
            # 临时护盾效果
            pass
        
        # 创建道具收集特效
        self.effects.append({
            'x': power_up['x'],
            'y': power_up['y'],
            'type': 'power_up_collect',
            'life': 25
        })
    
    def _calculate_player_performance(self) -> float:
        """计算玩家表现"""
        if self.performance_stats['shots_fired'] == 0:
            accuracy = 0.0
        else:
            accuracy = self.performance_stats['shots_hit'] / self.performance_stats['shots_fired']
        
        # 综合性能评分 (0-1)
        survival_score = min(1.0, self.game_state['survival_time'] / 60.0)  # 1分钟为满分
        kill_score = min(1.0, self.game_state['enemies_killed'] / 20.0)     # 20个击杀为满分
        accuracy_score = accuracy
        health_score = self.game_state['player_health'] / 100.0
        
        performance = (survival_score * 0.3 + kill_score * 0.3 + 
                      accuracy_score * 0.2 + health_score * 0.2)
        
        return performance
    
    def _regenerate_ai_rules(self):
        """重新生成AI规则"""
        print("\n🔄 重新生成AI游戏规则...")
        self.game_rules = self.rule_generator.generate_game_session()
        self.ai_strategy = self.strategy_generator.generate_initial_strategy()
        
        # 重置游戏状态
        self.game_state['frame_count'] = 0
        self.game_state['player_score'] = 0
        self.game_state['enemies_killed'] = 0
        self.game_state['power_ups_collected'] = 0
        self.game_state['start_time'] = time.time()
        
        # 清空游戏对象
        self.enemies.clear()
        self.bullets.clear()
        self.power_ups.clear()
        self.effects.clear()
        
        print("✅ AI规则重新生成完成！")
    
    def _render(self):
        """渲染游戏画面"""
        self.screen.fill(self.colors['black'])
        
        # 绘制背景
        self._draw_background()
        
        # 绘制游戏对象
        self._draw_game_objects()
        
        # 绘制UI
        self._draw_ui()
        
        # 绘制特效
        self._draw_effects()
        
        pygame.display.flip()
    
    def _draw_background(self):
        """绘制背景"""
        # 根据AI规则绘制背景
        if self.game_rules['level_design_rules']['background'] == 'space':
            # 星空背景
            for i in range(50):
                x = (i * 17) % 800
                y = (i * 23) % 600
                brightness = (math.sin(self.game_state['frame_count'] * 0.01 + i) + 1) * 127
                color = (brightness, brightness, brightness)
                pygame.draw.circle(self.screen, color, (x, y), 1)
        
        # 绘制视差层
        parallax_layers = self.game_rules['level_design_rules']['parallax_layers']
        for layer in range(parallax_layers):
            offset = (self.game_state['frame_count'] * (layer + 1) * 0.1) % 800
            pygame.draw.line(self.screen, (50, 50, 50), 
                           (offset, 0), (offset, 600), 2)
    
    def _draw_game_objects(self):
        """绘制游戏对象"""
        # 绘制玩家
        pygame.draw.circle(self.screen, self.colors['green'], 
                          (int(self.player['x']), int(self.player['y'])), 
                          self.player['size'])
        
        # 绘制敌机
        for enemy in self.enemies:
            color = self.colors['red']
            if enemy['health'] > 3:
                color = self.colors['purple']
            elif enemy['health'] > 1:
                color = self.colors['orange']
            
            pygame.draw.circle(self.screen, color, 
                              (int(enemy['x']), int(enemy['y'])), 
                              enemy['size'])
        
        # 绘制子弹
        for bullet in self.bullets:
            pygame.draw.circle(self.screen, self.colors['yellow'], 
                              (int(bullet['x']), int(bullet['y'])), 
                              bullet['size'])
        
        # 绘制道具
        for power_up in self.power_ups:
            color = self.colors['blue']
            if power_up['type'] == 'health':
                color = self.colors['green']
            elif power_up['type'] == 'speed':
                color = self.colors['yellow']
            
            pygame.draw.circle(self.screen, color, 
                              (int(power_up['x']), int(power_up['y'])), 
                              power_up['size'])
    
    def _draw_ui(self):
        """绘制UI界面"""
        # 游戏信息
        info_text = [
            f"生命值: {self.game_state['player_health']}",
            f"分数: {self.game_state['player_score']}",
            f"击杀: {self.game_state['enemies_killed']}",
            f"生存时间: {self.game_state['survival_time']:.1f}s",
            f"AI难度: {self.game_state['ai_difficulty']:.2f}"
        ]
        
        for i, text in enumerate(info_text):
            surface = self.font.render(text, True, self.colors['white'])
            self.screen.blit(surface, (10, 10 + i * 25))
        
        # 性能统计
        stats_text = [
            f"射击: {self.performance_stats['shots_fired']}",
            f"命中: {self.performance_stats['shots_hit']}",
            f"准确率: {self.performance_stats['shots_hit']/max(1, self.performance_stats['shots_fired'])*100:.1f}%"
        ]
        
        for i, text in enumerate(stats_text):
            surface = self.small_font.render(text, True, self.colors['white'])
            self.screen.blit(surface, (10, 550 + i * 18))
        
        # 控制说明
        controls = [
            "控制: WASD移动, 空格射击, R重新生成AI规则, ESC退出"
        ]
        
        for i, text in enumerate(controls):
            surface = self.small_font.render(text, True, self.colors['white'])
            self.screen.blit(surface, (400, 550 + i * 18))
        
        # 特殊事件显示
        if self.game_state['active_events']:
            event_text = f"特殊事件: {', '.join(self.game_state['active_events'].keys())}"
            surface = self.font.render(event_text, True, self.colors['yellow'])
            self.screen.blit(surface, (400, 10))
    
    def _draw_effects(self):
        """绘制特效"""
        for effect in self.effects:
            if effect['type'] == 'explosion':
                # 爆炸特效
                size = (30 - effect['life']) * 2
                color = (255, 255 - effect['life'] * 8, 0)
                pygame.draw.circle(self.screen, color, 
                                  (int(effect['x']), int(effect['y'])), 
                                  int(size))
            elif effect['type'] == 'damage':
                # 受伤特效
                size = 20 - effect['life']
                color = (255, 0, 0)
                pygame.draw.circle(self.screen, color, 
                                  (int(effect['x']), int(effect['y'])), 
                                  int(size))
            elif effect['type'] == 'power_up_collect':
                # 道具收集特效
                size = 15 - effect['life'] * 0.6
                color = (0, 255, 255)
                pygame.draw.circle(self.screen, color, 
                                  (int(effect['x']), int(effect['y'])), 
                                  int(size))
    
    def _game_over(self):
        """游戏结束"""
        print("\n🎮 游戏结束！")
        
        # 计算最终性能
        final_performance = self._calculate_player_performance()
        print(f"最终性能评分: {final_performance:.3f}")
        
        # 进化AI策略
        performance_data = {
            'survival_time': self.game_state['survival_time'],
            'enemies_killed': self.game_state['enemies_killed'],
            'damage_taken': self.performance_stats['damage_taken'],
            'power_ups_collected': self.game_state['power_ups_collected'],
            'accuracy_rate': self.performance_stats['shots_hit'] / max(1, self.performance_stats['shots_fired'])
        }
        
        print("🔄 AI策略正在进化...")
        new_strategy = self.strategy_generator.evolve_strategy(performance_data)
        
        print("✅ AI策略进化完成！")
        print("\n🧠 新策略摘要:")
        print(self.strategy_generator.get_strategy_summary())
        
        # 等待几秒后退出
        time.sleep(3)

# 主函数
if __name__ == "__main__":
    try:
        # 创建并运行AI游戏集成示例
        game = AIGameIntegration()
        game.run()
    except Exception as e:
        print(f"❌ 游戏运行出错: {e}")
        import traceback
        traceback.print_exc()
