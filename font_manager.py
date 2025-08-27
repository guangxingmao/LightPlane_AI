import pygame
import os
import sys

class FontManager:
    """字体管理器 - 支持中文显示"""
    
    def __init__(self):
        self.fonts = {}
        self.default_font_size = 20
        self._init_fonts()
    
    def _init_fonts(self):
        """初始化字体"""
        # 延迟初始化字体，等待pygame.font模块初始化
        self.chinese_font_path = None
        self.fonts_initialized = False
    
    def _ensure_fonts_initialized(self):
        """确保字体已初始化"""
        if self.fonts_initialized:
            return
            
        # 尝试加载系统中文字体
        chinese_fonts = [
            # macOS 系统字体
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            # Windows 系统字体
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            # Linux 系统字体
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
        
        # 尝试加载中文字体
        for font_path in chinese_fonts:
            if os.path.exists(font_path):
                try:
                    # 测试字体是否可用
                    test_font = pygame.font.Font(font_path, self.default_font_size)
                    # 测试中文字符渲染
                    test_surface = test_font.render("测试", True, (0, 0, 0))
                    self.chinese_font_path = font_path
                    print(f"成功加载中文字体: {font_path}")
                    break
                except Exception as e:
                    print(f"字体加载失败 {font_path}: {e}")
                    continue
        else:
            # 如果没有找到中文字体，使用系统默认字体
            self.chinese_font_path = None
            print("警告: 未找到中文字体，将使用系统默认字体")
        
        self.fonts_initialized = True
    
    def get_font(self, size=None):
        """获取字体对象"""
        if size is None:
            size = self.default_font_size
        
        # 确保字体已初始化
        self._ensure_fonts_initialized()
        
        # 如果缓存中已有该尺寸的字体，直接返回
        if size in self.fonts:
            return self.fonts[size]
        
        try:
            if self.chinese_font_path:
                # 使用中文字体
                font = pygame.font.Font(self.chinese_font_path, size)
            else:
                # 回退到系统字体
                font = pygame.font.SysFont(None, size)
            
            # 缓存字体
            self.fonts[size] = font
            return font
            
        except Exception as e:
            print(f"字体创建失败: {e}")
            # 最后的备用方案
            try:
                return pygame.font.Font(None, size)
            except:
                return None
    
    def render_text(self, text, size=None, color=(0, 0, 0), antialias=True):
        """渲染文本"""
        font = self.get_font(size)
        if font is None:
            # 如果字体创建失败，返回一个简单的矩形
            surface = pygame.Surface((len(text) * 10, size or self.default_font_size))
            surface.fill(color)
            return surface
        
        try:
            return font.render(text, antialias, color)
        except Exception as e:
            print(f"文本渲染失败: {e}")
            # 返回一个简单的矩形作为备用
            surface = pygame.Surface((len(text) * 10, size or self.default_font_size))
            surface.fill(color)
            return surface
    
    def get_text_size(self, text, size=None):
        """获取文本尺寸"""
        font = self.get_font(size)
        if font is None:
            return (len(text) * 10, size or self.default_font_size)
        
        try:
            return font.size(text)
        except:
            return (len(text) * 10, size or self.default_font_size)

# 创建全局字体管理器实例
font_manager = FontManager()

def get_chinese_font(size=None):
    """获取支持中文的字体"""
    return font_manager.get_font(size)

def render_chinese_text(text, size=None, color=(0, 0, 0), antialias=True):
    """渲染中文文本"""
    return font_manager.render_text(text, size, color, antialias)

def get_chinese_text_size(text, size=None):
    """获取中文文本尺寸"""
    return font_manager.get_text_size(text, size)
