import pygame
import sys
import os
import random

# 导入游戏相关模块
from plane_sprites import *
from game_function import check_KEY, check_mouse
from Tools import Music, Button as GameButton

class CustomGamePage:
    """传统模式游戏页面类 - 只有玩家1"""
    
    def __init__(self, screen, screen_width=None, screen_height=None, custom_config=None):
        # 创建游戏屏幕
        self.screen = screen
        
        # 获取屏幕尺寸
        if screen_width and screen_height:
            self.screen_width = screen_width
            self.screen_height = screen_height
        else:
            self.screen_width = screen.get_width()
            self.screen_height = screen.get_height()

        # 保存自定义配置
        self.custom_config = custom_config or {}

        # 设置窗口的标题
        if custom_config:
            pygame.display.set_caption('战机大战 - 自定义模式')
        else:
            pygame.display.set_caption('战机大战 - 传统模式')
            
        # 创建游戏时钟
        self.clock = pygame.time.Clock()
        # 生命数量
        self.life1 = 3
        # 分数
        self.score1 = 0
        # 设置背景音乐
        self.BGM = Music('./music/bgm1.mp3')
        #创建按钮对象
        # 可以控制鼠标显示和控制游戏开始暂停
        self.button = GameButton()

        # 调用私有方法创建精灵组
        self.__creat_sprites()
        
        # 如果是自定义模式，自动开始游戏
        if self.custom_config:
            print("🎮 自定义模式：自动开始游戏")
            self.button.count_mouse = 1  # 启用鼠标控制
            self.button.pause_game = 0   # 开始游戏
    
    def reset_game(self):
        """重置游戏状态"""
        # 重置生命和分数
        self.life1 = 3
        self.score1 = 0
        # 重新创建精灵组
        self.__creat_sprites()
    
    def clear_game_cache(self):
        """清除游戏缓存"""
        print("🧹 清除游戏缓存...")
        
        # 清除自定义配置
        if hasattr(self, 'custom_config'):
            self.custom_config = {}
            print("✅ 游戏配置缓存已清除")
        
        # 清除精灵组引用
        if hasattr(self, 'back_group'):
            self.back_group.empty()
        if hasattr(self, 'enemy_group'):
            self.enemy_group.empty()
        if hasattr(self, 'hero_group1'):
            self.hero_group1.empty()
        if hasattr(self, 'global_enemy_bullets'):
            self.global_enemy_bullets.empty()
        
        print("✅ 游戏精灵组缓存已清除")
    
    def reinitialize_game(self, new_config):
        """重新初始化游戏（用于重新进入时）"""
        print("🔄 重新初始化游戏...")
        
        # 清除旧的精灵组
        self.clear_game_cache()
        
        # 更新配置
        self.custom_config = new_config or {}
        
        # 重置游戏状态
        self.life1 = 3
        self.score1 = 0
        
        # 重新创建精灵组
        self.__creat_sprites()
        
        # 重新设置游戏状态
        if self.custom_config:
            print("🎮 自定义模式：重新开始游戏")
            self.button.count_mouse = 1  # 启用鼠标控制
            self.button.pause_game = 0   # 开始游戏
        else:
            print("🎮 传统模式：重新开始游戏")
            self.button.count_mouse = 0  # 禁用鼠标控制
            self.button.pause_game = 1   # 暂停游戏
        
        print("✅ 游戏重新初始化完成")

    def start_game(self):
        '''开始游戏'''
        while True:
            pygame.init()

            # 判断是否有音乐在播放，如果没有，就播放
            # 也就是循环播放背景音乐
            if not pygame.mixer.music.get_busy():
                self.BGM.play_music()
            # 1. 设置刷新帧率
            self.clock.tick(60)
            # 2. 事件监听
            should_quit = self.__check_event()
            if should_quit:
                return "quit"

            # 3. 碰撞检测
            game_over = self.__check_collide()
            if game_over:
                return "game_over"

            # 4. 更新精灵组
            self.__update_sprites()

            # 5. 显示生命和分数
            self.show_life()

            # 5. 更新屏幕显示
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

        # 碰撞检测
        game_over = self.__check_collide()
        if game_over:
            return "game_over"

        # 更新精灵组
        self.__update_sprites()

        # 显示生命和分数
        self.show_life()

        return "running"

    def run(self):
        """运行游戏页面 - 用于与启动器集成"""
        print("自定义游戏页面开始运行")
        
        while True:
            # 1. 设置刷新帧率
            self.clock.tick(60)
            
            # 2. 事件监听
            event_result = self.__check_event()
            if event_result:
                return event_result

            # 3. 碰撞检测
            game_over = self.__check_collide()
            if game_over:
                return "game_over"

            # 4. 更新精灵组
            self.__update_sprites()

            # 5. 显示生命和分数
            self.show_life()

            # 6. 更新屏幕显示
            pygame.display.update()

    def __check_event(self):
        """事件监听"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # 按ESC返回config页面，但不清除配置缓存
                return "back"
                
            print(event)
            # 创建虚拟的hero2和hero3对象，避免None错误（传统模式不需要僚机）
            dummy_hero2 = type('DummyHero', (), {
                'fire': lambda *args: None, 
                'moving_right': False, 
                'moving_left': False, 
                'moving_up': False, 
                'moving_down': False,
                'time_count': 1
            })()
            dummy_hero3 = type('DummyHero', (), {
                'fire': lambda *args: None, 
                'moving_right': False, 
                'moving_left': False, 
                'moving_up': False, 
                'moving_down': False,
                'time_count': 1
            })()
            # 处理敌机创建事件
            if event.type == CREAT_ENEMY_EVENT and self.button.pause_game % 2 == 0:
                # 使用自定义敌机类或默认敌机类
                if self.custom_config.get('images', {}).get('enemy_plane'):
                    new_enemy = CustomEnemy(self.custom_config['images']['enemy_plane'])
                    print("✅ 创建新的自定义敌机")
                else:
                    new_enemy = Enemy()
                    print("✅ 创建新的默认敌机")
                
                # 设置敌机位置 - 从屏幕最右边出现
                new_enemy.rect.x = self.screen_width
                new_enemy.rect.y = random.randint(0, self.screen_height - new_enemy.rect.height)
                
                # 添加到敌机组
                self.enemy_group.add(new_enemy)
            elif event.type == HERO_FIRE_EVENT:
                if self.hero1.time_count > 0:
                    self.hero1.fire()
            elif event.type == WING_FIRE_EVENT:
                # 传统模式没有僚机，忽略此事件
                pass
            else:
                # 处理其他事件
                check_KEY(self.hero1, dummy_hero2, dummy_hero3, self.enemy,
                          event, self.enemy_group, self.BGM, self.button)
            check_mouse(event, self.button)

            # 游戏开始时候，主战机跟随鼠标移动
            if self.button.pause_game % 2 == 0 and self.button.count_mouse % 2 == 0:
                if event.type == pygame.MOUSEMOTION and self.life1 > 0:
                    (x,y) = pygame.mouse.get_pos()
                    self.hero1.rect.centerx = x
                    self.hero1.rect.centery = y
        
        return False

    def __check_collide(self):
        '''碰撞检测'''
        # 子弹碰撞敌人（只检测主英雄的子弹）
        hit_enemies = pygame.sprite.groupcollide(self.hero1.bullets, self.enemy_group, True, True)
        if hit_enemies:
            self.score1 += 1
            # 敌人死亡时，将其子弹转移到全局子弹组，让子弹继续存在
            # hit_enemies的键是子弹，值是敌人列表
            for player_bullet, enemies in hit_enemies.items():
                for enemy in enemies:
                    # 将敌机的所有子弹复制到全局子弹组，并设置子弹的独立属性
                    for enemy_bullet in enemy.bullets:
                        # 创建新的子弹实例，避免引用问题
                        new_bullet = Bullet_Enemy()
                        new_bullet.rect = enemy_bullet.rect.copy()
                        new_bullet.speed = enemy_bullet.speed
                        self.global_enemy_bullets.add(new_bullet)
                    # 清空敌机的子弹组
                    enemy.bullets.empty()

        # 敌人碰撞英雄
        enemys1 = pygame.sprite.spritecollide(
            self.hero1, self.enemy_group, True)
        if len(enemys1) > 0 and self.life1 > 0:
            self.life1 -= 1
            if self.life1 == 0:
                # 英雄死亡后，移除屏幕
                self.hero1.rect.bottom = 0
                self.hero1.rect.x = self.screen_width
                self.hero1.kill()

        # 敌人子弹碰撞英雄1 - 使用全局子弹组
        bullets1 = pygame.sprite.spritecollide(
            self.hero1, self.global_enemy_bullets, True)
        if len(bullets1) > 0 and self.life1 > 0:
            self.life1 -= 1
            if self.life1 == 0:
                # 英雄死亡后，移除屏幕
                self.hero1.rect.bottom = 0
                self.hero1.rect.x = self.screen_width
                self.hero1.kill()

        # 当玩家死亡，游戏结束
        if self.life1 == 0:
            return True
        
        return False

    def __update_sprites(self):
        '''更新精灵组'''

        if self.button.pause_game % 2 != 0:
            # 绘制所有精灵组
            for group in [self.back_group, self.hero_group1, self.hero1.bullets, self.enemy_group, self.global_enemy_bullets]: 
                group.draw(self.screen)
            
            self.button.update()
            # 重新设置按钮位置到左下角
            self.button.rect.x = 20
            self.button.rect.bottom = self.screen_height - 20
            self.screen.blit(self.button.image,(self.button.rect.x,self.button.rect.y))

        elif self.button.pause_game % 2 == 0:
            # 绘制和更新所有精灵组
            for group in [self.back_group, self.hero_group1, self.hero1.bullets, self.enemy_group]:
                group.draw(self.screen)
                group.update()
            # 绘制和更新全局敌人子弹组
            self.global_enemy_bullets.draw(self.screen)
            self.global_enemy_bullets.update()
            
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
        color = (0, 0, 0)
        text1 = 'LIFE: ' + str(self.life1)
        text2 = 'SCORE: ' + str(self.score1)
        try:
            cur_font = pygame.font.SysFont(None, 20)
        except:
            cur_font = pygame.font.Font(None, 20)
        text_fmt1 = cur_font.render(text1, 1, color)
        text_fmt2 = cur_font.render(text2, 1, color)
        self.screen.blit(text_fmt1, pos1)
        self.screen.blit(text_fmt2, pos2)

    def __creat_sprites(self):
        '''创建精灵组'''
        # 背景组 - 根据配置选择使用自定义背景或默认背景
        if self.custom_config.get('images', {}).get('background'):
            # 使用自定义背景
            background_image = self.custom_config['images']['background']
            background_source = self.custom_config.get('sources', {}).get('background', 'uploaded')
            is_ai_generated = (background_source == 'ai_generated')
            
            bg1 = CustomBackground(background_image, self.screen_width, self.screen_height, False, is_ai_generated)
            bg2 = CustomBackground(background_image, self.screen_width, self.screen_height, True, is_ai_generated)
            print(f"✅ 使用自定义背景图片，来源: {background_source}")
            if is_ai_generated:
                print("🎨 AI生成的背景将保持静态（不移动）")
            else:
                print("📁 上传的背景将保持移动效果")
        else:
            # 使用默认背景
            bg1 = Background()
            bg2 = Background(True)
            # 调整背景图片大小以适应屏幕
            bg1.image = pygame.transform.scale(bg1.image, (self.screen_width, self.screen_height))
            bg2.image = pygame.transform.scale(bg2.image, (self.screen_width, self.screen_height))
            print("✅ 使用默认背景图片，保持移动效果")
        
        # 重新设置背景位置
        bg1.rect = bg1.image.get_rect()
        bg2.rect = bg2.image.get_rect()
        bg2.rect.x = self.screen_width
        
        self.back_group = pygame.sprite.Group(bg1, bg2)
        
        # 敌机组 - 根据配置选择使用自定义敌机或默认敌机
        self.enemy_group = pygame.sprite.Group()
        
        # 创建多个敌机实例
        for i in range(5):  # 创建5个敌机
            if self.custom_config.get('images', {}).get('enemy_plane'):
                # 使用自定义敌机
                enemy = CustomEnemy(self.custom_config['images']['enemy_plane'])
                print(f"✅ 创建自定义敌机 {i+1}")
            else:
                # 使用默认敌机
                enemy = Enemy()
                print(f"✅ 创建默认敌机 {i+1}")
            
            # 设置敌机位置 - 从屏幕最右边开始，水平间隔分布
            enemy.rect.x = self.screen_width + i * 100  # 从屏幕右边开始，水平间隔
            enemy.rect.y = random.randint(0, self.screen_height - enemy.rect.height)
            
            # 添加到敌机组
            self.enemy_group.add(enemy)
            
            # 保存第一个敌机作为 self.enemy（为了兼容性）
            if i == 0:
                self.enemy = enemy
        
        # 全局敌人子弹组 - 管理所有敌人的子弹，即使敌人死亡子弹也继续存在
        self.global_enemy_bullets = pygame.sprite.Group()

        # 英雄组 - 根据配置选择使用自定义玩家飞机或默认玩家飞机
        if self.custom_config.get('images', {}).get('player_plane'):
            # 使用自定义玩家飞机
            self.hero1 = CustomHero(self.custom_config['images']['player_plane'])
            print(f"✅ 使用自定义玩家飞机图片，尺寸: {self.custom_config['images']['player_plane'].get_size()}")
        else:
            # 使用默认玩家飞机
            self.hero1 = Hero('./images/life.png')
            print("✅ 使用默认玩家飞机图片")
            
        # 设置英雄1在左侧居中
        self.hero1.rect.x = 50
        self.hero1.rect.centery = self.screen_height // 2
        self.hero_group1 = pygame.sprite.Group(self.hero1)


class CustomBackground(Background):
    """自定义背景类"""
    def __init__(self, custom_image, screen_width, screen_height, is_second=False, is_ai_generated=False):
        super().__init__(is_second)
        # 替换背景图片
        self.image = custom_image
        # 调整大小以适应屏幕
        self.image = pygame.transform.scale(custom_image, (screen_width, screen_height))
        # 重新设置位置
        self.rect = self.image.get_rect()
        if is_second:
            self.rect.x = screen_width
        
        # 标记是否为AI生成的背景
        self.is_ai_generated = is_ai_generated
    
    def update(self):
        """重写update方法，AI生成的背景不移动"""
        if self.is_ai_generated:
            # AI生成的背景不移动，保持静态
            pass
        else:
            # 默认背景保持移动效果
            self.rect.x -= 2
            if self.rect.x <= -self.rect.width:
                self.rect.x = self.rect.width

class CustomHero(Hero):
    """自定义英雄类"""
    def __init__(self, custom_image):
        super().__init__('./images/life.png')  # 先调用父类初始化
        
        # 使用更小的缩放尺寸，让飞机看起来更接近传统模式
        # 传统模式中飞机看起来比较小，所以使用更小的尺寸
        target_size = (45, 56)  # 比 60x75 更小，更接近传统模式
        print(f"自定义模式玩家飞机目标尺寸: {target_size}")
        
        # 缩放图片到目标尺寸
        scaled_image = pygame.transform.scale(custom_image, target_size)
        
        # 旋转图片，让飞机朝向右边（传统模式的朝向）
        # 如果图片是朝上的，需要顺时针旋转90度
        rotated_image = pygame.transform.rotate(scaled_image, -90)  # 负值表示顺时针旋转
        
        self.image = rotated_image
        # 重新设置碰撞检测矩形
        self.rect = self.image.get_rect()

class CustomEnemy(Enemy):
    """自定义敌机类"""
    def __init__(self, custom_image):
        super().__init__()  # 先调用父类初始化
        # 替换敌机图片，但保持传统模式的大小
        # 缩放图片到传统模式的大小 (43x57)
        scaled_image = pygame.transform.scale(custom_image, (43, 57))
        self.image = scaled_image
        # 重新设置碰撞检测矩形
        self.rect = self.image.get_rect()
        # 注意：不在这里设置位置，位置由调用者设置
