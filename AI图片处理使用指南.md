# AI图片识别和背景去除使用指南

## 🚀 功能概述

这个项目集成了多种AI模型，可以自动识别图片中的主题（如飞机）并去除背景，生成透明背景的PNG图片，完美适合飞机大战游戏使用。

## 📦 支持的AI模型

### 1. **RemBG** (推荐)
- **特点**: 基于深度学习的背景去除，效果最好
- **优点**: 自动识别前景物体，无需手动标注
- **适用场景**: 飞机、人物、物体等复杂形状
- **安装**: `pip install rembg`

### 2. **OpenCV**
- **特点**: 基于颜色阈值的背景去除
- **优点**: 速度快，资源占用少
- **适用场景**: 背景颜色单一的图片（如蓝天背景的飞机）
- **安装**: `pip install opencv-python`

### 3. **Segment Anything Model (SAM)**
- **特点**: Meta的先进分割模型，精度最高
- **优点**: 可以精确分割任何物体
- **适用场景**: 需要最高精度的场景
- **安装**: `pip install segment-anything`
- **注意**: 需要下载预训练模型文件

## 🛠️ 快速安装

### 方法1: 使用安装脚本（推荐）
```bash
python install_ai_dependencies.py
```

### 方法2: 手动安装
```bash
# 基础依赖
pip install Pillow numpy

# AI模型
pip install rembg
pip install opencv-python
pip install torch torchvision

# 可选高级功能
pip install git+https://github.com/facebookresearch/segment-anything.git
pip install scikit-image
```

## 💻 使用方法

### 基础使用

```python
from background_remover import BackgroundRemover

# 创建背景去除器
remover = BackgroundRemover()

# 检查可用模型
print("可用模型:", remover.get_available_models())

# 去除背景
result = remover.remove_background('airplane.png', 'airplane_no_bg.png')
```

### 高级使用

```python
from ai_image_processor import AIImageProcessor

# 创建AI图片处理器
processor = AIImageProcessor()

# 设置AI模型
processor.set_model('rembg')  # 或 'opencv', 'sam'

# 处理图片
def on_complete(result):
    if result['status'] == 'success':
        print(f"处理完成: {result['type']}")
        # 获取处理后的Pygame surface
        pygame_surface = result['pygame_surface']
    else:
        print(f"处理失败: {result['error']}")

processor.process_image('airplane.png', 'player_plane', callback=on_complete)
```

## 🎮 集成到游戏系统

### 在custom_config_page.py中使用

```python
from ai_image_processor import AIImageProcessor

class CustomConfigPage:
    def __init__(self, screen, width=None, height=None):
        # ... 现有代码 ...
        
        # 初始化AI图片处理器
        self.ai_processor = AIImageProcessor()
        
        # 添加背景去除按钮
        self.add_background_removal_buttons()
    
    def add_background_removal_buttons(self):
        """添加背景去除按钮"""
        # 为每个图片类型添加背景去除按钮
        for image_type in ['player_plane', 'enemy_plane']:
            button = {
                'rect': pygame.Rect(x, y, 100, 35),
                'text': 'Remove BG',
                'type': f'remove_bg_{image_type}'
            }
            self.buttons[f'remove_bg_{image_type}'] = button
    
    def handle_button_click(self, button_type):
        """处理按钮点击"""
        if button_type.startswith('remove_bg_'):
            image_type = button_type.replace('remove_bg_', '')
            self.start_background_removal(image_type)
        # ... 现有代码 ...
    
    def start_background_removal(self, image_type):
        """开始背景去除"""
        if image_type in self.config_cache and self.config_cache[image_type]:
            # 获取当前图片
            current_image = self.config_cache[image_type]
            
            def on_complete(result):
                if result['status'] == 'success':
                    # 更新预览和缓存
                    self.config_cache[image_type] = result['pygame_surface']
                    self.update_preview(image_type, result['pygame_surface'])
                    self.show_status(f"{image_type} 背景去除完成!", self.GREEN)
                else:
                    self.show_status(f"{image_type} 背景去除失败: {result['error']}", self.RED)
            
            # 开始处理
            self.ai_processor.process_pygame_surface(
                current_image, 
                image_type, 
                callback=on_complete
            )
            
            self.show_status(f"正在处理 {image_type}...", self.BLUE)
```

## 🔧 配置和优化

### 模型选择建议

1. **RemBG**: 适合大多数场景，效果稳定
2. **OpenCV**: 适合背景简单的图片，速度快
3. **SAM**: 适合需要最高精度的场景，但需要更多资源

### 性能优化

```python
# 设置处理队列大小
processor.max_queue_size = 5

# 设置并发处理
processor.max_workers = 2

# 设置图片质量
processor.quality = 'high'  # 'low', 'medium', 'high'
```

## 📁 文件结构

```
LightPlane_AI/
├── background_remover.py      # 核心背景去除类
├── ai_image_processor.py      # AI图片处理器
├── install_ai_dependencies.py # 依赖安装脚本
├── processed_images/          # 处理后的图片输出目录
└── AI图片处理使用指南.md      # 本文件
```

## 🎯 使用场景

### 1. **AI生成的飞机图片**
- 使用AI生成飞机图片
- 自动去除背景
- 生成透明背景的PNG
- 直接用于游戏

### 2. **上传的真实飞机图片**
- 上传真实飞机照片
- AI识别飞机主体
- 去除天空、云朵等背景
- 生成游戏可用的素材

### 3. **批量处理**
- 处理多张图片
- 自动分类（玩家飞机、敌机、背景）
- 批量生成游戏素材

## 🚨 注意事项

1. **首次使用**: 某些AI模型需要下载预训练文件，首次运行可能较慢
2. **图片格式**: 建议使用PNG格式，支持透明通道
3. **图片质量**: 输入图片质量越高，处理效果越好
4. **资源占用**: SAM模型需要较多内存和GPU资源
5. **处理时间**: 复杂图片可能需要几秒到几十秒

## 🔍 故障排除

### 常见问题

1. **模型不可用**
   - 检查是否正确安装了依赖包
   - 运行 `python install_ai_dependencies.py`

2. **处理失败**
   - 检查图片文件是否存在
   - 确认图片格式是否支持
   - 查看错误日志

3. **效果不理想**
   - 尝试不同的AI模型
   - 调整图片质量
   - 检查输入图片是否合适

### 获取帮助

如果遇到问题，可以：
1. 查看控制台错误信息
2. 检查依赖包是否正确安装
3. 尝试使用不同的AI模型
4. 参考示例代码

## 🎉 开始使用

现在你可以：
1. 运行安装脚本安装依赖
2. 在游戏中使用AI背景去除功能
3. 生成完美的透明背景飞机图片
4. 享受AI带来的便利！

祝你使用愉快！🚀✈️
