import pygame
from plane_sprites import *

def check_KEYDOWN(hero1, hero2, hero3,enemy, event, enemy_group, BGM, button):


    # 按下`键显示或隐藏鼠标
    if event.key == 96:
        button.count_mouse += 1
        if button.count_mouse % 2 == 0:
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)
    # 按下空格键暂停或继续音乐
    if event.key == pygame.K_SPACE:
        button.count_music += 1
        if button.count_music %2 == 0:
            BGM.pause_music()
        else:
            BGM.unpause_music()
        
    # 主玩家的移动监测
    if event.key == pygame.K_RIGHT :
        hero1.moving_right = True
        hero3.moving_right = True

    elif event.key == pygame.K_LEFT:
        hero1.moving_left = True
        hero3.moving_left = True

    elif event.key == pygame.K_UP :
        hero1.moving_up = True
        hero3.moving_up = True

    elif event.key == pygame.K_DOWN:
        hero1.moving_down = True
        hero3.moving_down = True


    # 副玩家的移动监测
    if event.key == pygame.K_d:
        hero2.moving_right = True

    elif event.key == pygame.K_a:
        hero2.moving_left = True

    elif event.key == pygame.K_w:
        hero2.moving_up = True

    elif event.key == pygame.K_s:
        hero2.moving_down = True


    elif event.key == pygame.K_q:
        exit()


def check_KEYUP(hero1, hero2, hero3, event):
    if event.key == pygame.K_RIGHT:
        hero1.moving_right = False
        hero3.moving_right = False
    elif event.key == pygame.K_LEFT:
        hero1.moving_left = False
        hero3.moving_left = False
    elif event.key == pygame.K_UP:
        hero1.moving_up = False
        hero3.moving_up = False
    elif event.key == pygame.K_DOWN:
        hero1.moving_down = False
        hero3.moving_down = False

    if event.key == pygame.K_d:
        hero2.moving_right = False

    elif event.key == pygame.K_a:
        hero2.moving_left = False

    elif event.key == pygame.K_w:
        hero2.moving_up = False

    elif event.key == pygame.K_s:
        hero2.moving_down = False



def check_KEY(hero1, hero2, hero3, enemy, event, enemy_group, BGM, button):
    if event.type == pygame.QUIT:
        exit()

    if event.type == pygame.KEYDOWN:
        check_KEYDOWN(hero1, hero2, hero3, enemy, event, enemy_group, BGM, button)

    elif event.type == pygame.KEYUP:
        check_KEYUP(hero1, hero2, hero3, event)

    # 创造敌机事件
    elif event.type == CREAT_ENEMY_EVENT and button.pause_game % 2 == 0:
        new_enemy = Enemy()
        enemy_group.add(new_enemy)

    elif event.type == HERO_FIRE_EVENT:
        if hero1.time_count > 0:
            hero1.fire()
            hero2.fire()
            
    elif event.type == WING_FIRE_EVENT:
        if hero3.time_count > 0:
            hero3.fire()


def check_mouse(event, button):
    if event.type == pygame.MOUSEBUTTONDOWN:
    # 检测鼠标点击
        mouse_x,mouse_y = pygame.mouse.get_pos()
        # 鼠标点击到按钮
        if button.rect.collidepoint(mouse_x,mouse_y):
            button.pause_game += 1
