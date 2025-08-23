import pygame
from plane_sprites import *

class Music(object):
	'''音乐类'''	

	
	def __init__(self, path):
		self.path = path
		pygame.mixer.init()
		pygame.mixer.music.load(self.path)

	def play_music(self):
		pygame.mixer.music.play()

	def pause_music(self):
		pygame.mixer.music.pause()

	def unpause_music(self):
		pygame.mixer.music.unpause()


class Button(object):
	'''按钮类'''
	def __init__(self):

		# 控制鼠标显示
		self.count_mouse = 1
		# 控制游戏开始暂停
		self.pause_game = 1
		# 控制音乐开始暂停
		self.count_music = 1


	def update(self):
		# 开始游戏
		if self.pause_game % 2 == 0:
			self.image = pygame.image.load('./images/pause_pressed.png')
			self.rect = self.image.get_rect()
			self.rect.x = 20
			self.rect.bottom = SCREEN_RECT.bottom
		# 暂停游戏
		else:
			self.image = pygame.image.load('./images/resume_pressed.png')
			self.rect = self.image.get_rect()
			self.rect.x = 20
			self.rect.bottom = SCREEN_RECT.bottom


