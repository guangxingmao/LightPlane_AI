# LightPlane AI - 飞机大战游戏

一个基于Pygame的飞机大战游戏，集成了多种AI控制器和强化学习功能。

## 项目结构

```
LightPlane_AI/
├── README.md                      # 项目说明文档
├── launcher.py                    # 游戏启动器（主入口）
├── ai_game_page.py               # AI模式游戏页面
├── dual_game_page.py             # 双人模式游戏页面
├── traditional_game_page.py      # 传统模式游戏页面
├── easter_egg_page.py            # 彩蛋模式游戏页面
├── plane_sprites.py              # 游戏精灵类定义
├── game_function.py              # 游戏功能函数
├── Tools.py                      # 工具类
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
└── music/                        # 游戏音乐资源
```

## 游戏模式

### 1. 传统模式 (Traditional Mode)
- 单人游戏，只有玩家1
- 无僚机，玩家位置在左侧居中

### 2. 双人模式 (Dual Player Mode)
- 双人游戏，玩家1和玩家2
- 无僚机，玩家1在左上，玩家2在左下

### 3. AI模式 (AI Mode)
- 玩家1 + AI控制的玩家2
- 支持训练好的强化学习模型
- 自动躲避、追击和射击

### 4. 彩蛋模式 (Easter Egg Mode)
- 特殊游戏模式

## 快速开始

### 运行游戏
```bash
python3 launcher.py
```

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

## 控制说明

### 玩家1控制
- **鼠标移动**: 控制飞机位置
- **空格键**: 发射子弹
- **ESC键**: 返回主菜单

### 游戏控制
- **开始按钮**: 开始/暂停游戏
- **暂停按钮**: 暂停/继续游戏

## AI特性

- **混合AI控制器**: 结合训练模型和规则AI
- **智能行为**: 自动躲避、追击、巡逻
- **平滑移动**: 优化的移动算法，减少抖动
- **自适应射击**: 根据敌人位置自动射击

## 技术栈

- **游戏引擎**: Pygame
- **AI框架**: Stable Baselines3
- **强化学习**: Gymnasium
- **深度学习**: PyTorch
- **编程语言**: Python 3.7+

## 系统要求

- Python 3.7+
- 操作系统: Windows/macOS/Linux
- 内存: 4GB+
- 存储: 2GB+

## 开发团队

- **项目名称**: LightPlane AI
- **版本**: 1.0.0
- **最后更新**: 2024年

## 许可证

本项目仅供学习和研究使用。
