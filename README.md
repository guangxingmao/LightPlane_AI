# LightPlane AI - 飞机大战游戏

一个基于Pygame的飞机大战游戏，集成了多种AI控制器、强化学习功能、AI图片生成和处理功能。

## 🚀 最新功能

### ✨ AI图片生成与处理
- **AI图片生成**: 使用Stable Diffusion生成高质量飞机和背景图片
- **智能背景去除**: 支持RemBG、SAM、OpenCV等多种AI模型
- **边框去除与裁剪**: 自动检测主体边界，智能裁剪边框
- **批量图片处理**: 支持队列处理，实时进度显示

### 🎨 自定义配置系统
- **自定义配置页面**: 支持AI生成和上传自定义图片
- **智能图片优化**: 自动调整图片尺寸和格式
- **多图片类型支持**: 玩家飞机、敌机、背景图片
- **实时预览**: 即时查看处理结果

### 🎮 智能背景控制
- **AI生成背景**: 静态背景，不移动
- **上传背景**: 保持传统移动效果
- **默认背景**: 经典滚动效果

## 项目结构

```
LightPlane_AI/
├── README.md                      # 项目说明文档
├── launcher.py                    # 游戏启动器（主入口）
├── custom_config_page.py          # 自定义配置页面
├── ai_game_page.py               # AI模式游戏页面
├── dual_game_page.py             # 双人模式游戏页面
├── traditional_game_page.py      # 传统模式游戏页面
├── custom_game_page.py           # 自定义模式游戏页面
├── easter_egg_page.py            # 彩蛋模式游戏页面
├── plane_sprites.py              # 游戏精灵类定义
├── game_function.py              # 游戏功能函数
├── Tools.py                      # 工具类
├── ai_image_processor.py         # AI图片处理器
├── background_remover.py         # AI背景去除器
├── local_image_generator.py      # 本地AI图片生成器
├── rl_ai_controller.py          # 强化学习AI控制器（旧版本）
├── ai_controllers/               # AI控制器包
│   ├── __init__.py              # AI包初始化文件
│   ├── README.md                # AI包说明文档
│   ├── trained_ai_controller.py # 训练好的AI控制器
│   ├── plane_fighter_env.py     # Gymnasium环境定义
│   ├── train_ai.py              # AI训练脚本
│   ├── check_training.py        # 训练状态检查脚本
│   ├── AI训练文档.md            # AI训练详细文档
│   └── 训练命令速查表.md        # 训练命令快速参考
├── models/                       # 训练好的AI模型
├── logs/                         # 训练日志
├── images/                       # 游戏图片资源
├── music/                        # 游戏音乐资源
├── processed_images/             # AI处理后的图片
├── lora_output/                  # LoRA训练输出
└── airplane_dataset/             # 飞机图片数据集
```

## 游戏模式

### 1. 传统模式 (Traditional Mode)
- 单人游戏，只有玩家1
- 无僚机，玩家位置在左侧居中
- 使用默认游戏资源

### 2. 双人模式 (Dual Player Mode)
- 双人游戏，玩家1和玩家2
- 无僚机，玩家1在左上，玩家2在左下
- 支持键盘和鼠标控制

### 3. AI模式 (AI Mode)
- 玩家1 + AI控制的玩家2
- 支持训练好的强化学习模型
- 自动躲避、追击和射击
- 优化的AI控制器，减少卡顿

### 4. 自定义模式 (Custom Mode) 🆕
- 支持AI生成和上传自定义图片
- 智能背景去除和边框裁剪
- 自定义玩家飞机、敌机、背景
- 实时预览和配置管理

### 5. 彩蛋模式 (Easter Egg Mode)
- 特殊游戏模式和有趣玩法

## 🎯 快速开始

### 运行游戏
```bash
python3 launcher.py
```

### 使用自定义配置
1. 启动游戏，选择"自定义模式"
2. 使用AI生成图片或上传自定义图片
3. 自动背景去除和边框裁剪
4. 开始游戏，享受个性化体验

### 训练AI模型
```bash
cd ai_controllers
python3 train_ai.py --mode train --timesteps 2000000
```

### 检查训练状态
```bash
cd ai_controllers
python3 check_training.py
```

## 🎮 控制说明

### 玩家1控制
- **鼠标移动**: 控制飞机位置
- **空格键**: 发射子弹
- **ESC键**: 返回主菜单

### 玩家2控制（双人模式）
- **WASD键**: 控制飞机移动
- **空格键**: 发射子弹

### 游戏控制
- **开始按钮**: 开始/暂停游戏
- **暂停按钮**: 暂停/继续游戏

### 自定义配置页面
- **上传按钮**: 选择本地图片文件
- **AI生成按钮**: 使用AI生成图片
- **去边框按钮**: 去除图片边框
- **自动处理按钮**: 背景去除+边框裁剪

## 🤖 AI特性

### 游戏AI
- **混合AI控制器**: 结合训练模型和规则AI
- **智能行为**: 自动躲避、追击、巡逻
- **平滑移动**: 优化的移动算法，减少抖动
- **自适应射击**: 根据敌人位置自动射击

### 图片AI 🆕
- **Stable Diffusion**: 高质量AI图片生成
- **智能背景去除**: 多种AI模型支持
- **轮廓检测**: OpenCV智能边界识别
- **自适应裁剪**: 智能padding和尺寸调整

## 🛠️ 技术栈

- **游戏引擎**: Pygame
- **AI框架**: Stable Baselines3
- **强化学习**: Gymnasium
- **深度学习**: PyTorch
- **图片处理**: OpenCV, PIL, RemBG
- **AI生成**: Stable Diffusion
- **编程语言**: Python 3.7+

## 📋 系统要求

- Python 3.7+
- 操作系统: Windows/macOS/Linux
- 内存: 8GB+ (推荐16GB用于AI图片生成)
- 存储: 5GB+ (包含AI模型和图片资源)
- GPU: 推荐NVIDIA GPU用于AI图片生成

## 🔧 安装依赖

### 基础依赖
```bash
pip install pygame numpy pillow
```

### AI图片处理依赖
```bash
pip install opencv-python rembg torch torchvision
pip install diffusers transformers accelerate
```

### 强化学习依赖
```bash
pip install stable-baselines3 gymnasium
```

## 📚 使用指南

### AI图片生成
1. 在自定义配置页面输入描述
2. 选择图片类型（玩家飞机/敌机/背景）
3. 点击"AI生成"按钮
4. 等待生成完成，自动背景去除

### 自定义图片上传
1. 准备PNG/JPG格式图片
2. 在自定义配置页面上传
3. 自动调整尺寸和格式
4. 可选择背景去除和边框裁剪

### 智能背景控制
- **AI生成背景**: 自动设置为静态，不移动
- **上传背景**: 保持传统滚动效果
- **默认背景**: 经典移动效果

## 🐛 故障排除

### 常见问题
1. **AI图片生成失败**: 检查GPU内存和模型文件
2. **背景去除效果差**: 尝试不同的AI模型
3. **游戏卡顿**: 降低图片分辨率或使用默认资源

### 性能优化
1. 使用较小的图片尺寸
2. 启用GPU加速（如果可用）
3. 关闭不必要的AI功能

## 🔄 更新日志

### v2.0.0 (当前版本)
- ✨ 新增AI图片生成功能
- ✨ 新增智能背景去除
- ✨ 新增边框去除和裁剪
- ✨ 新增自定义配置页面
- ✨ 新增智能背景移动控制
- ✨ 优化AI控制器性能
- ✨ 支持批量图片处理

### v1.0.0
- 🎮 基础飞机大战游戏
- 🤖 强化学习AI控制器
- 🎯 多种游戏模式

## 👥 开发团队

- **项目名称**: LightPlane AI
- **版本**: 2.0.0
- **最后更新**: 2024年12月
- **主要功能**: 飞机大战 + AI图片生成 + 智能处理

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

---

**享受AI驱动的个性化飞机大战游戏！** 🚀✈️
