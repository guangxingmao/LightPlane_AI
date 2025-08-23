# AI控制器包 (ai_controllers)

这个文件夹包含了LightPlane游戏的所有AI相关模块和控制器。

## 文件结构

```
ai_controllers/
├── __init__.py                    # 包初始化文件
├── README.md                      # 本说明文档
├── optimized_ai_controller.py    # 优化的简单AI控制器
├── trained_ai_controller.py      # 训练好的AI控制器
├── plane_fighter_env.py          # Gymnasium环境定义
├── train_ai.py                   # AI训练脚本
├── check_training.py             # 训练状态检查脚本
├── AI训练文档.md                 # AI训练详细文档
└── 训练命令速查表.md             # 训练命令快速参考
```

## 主要模块说明

### 1. optimized_ai_controller.py
- **OptimizedAIController**: 优化的简单AI控制器，减少抖动，提高流畅度
- 支持躲避、追击、巡逻等智能行为
- 动态速度调整和位置变化阈值

### 2. trained_ai_controller.py
- **TrainedAIController**: 基于Stable Baselines3训练的PPO模型控制器
- **HybridAIController**: 混合AI控制器，结合训练模型和规则AI
- **create_ai_controller()**: 工厂函数，创建不同类型的AI控制器

### 2. plane_fighter_env.py
- **PlaneFighterEnv**: Gymnasium环境类，用于强化学习训练
- 定义了观察空间、动作空间和奖励函数
- 支持虚拟显示，适合无头环境训练

### 3. train_ai.py
- AI训练的主要脚本
- 支持PPO算法训练
- 可配置训练参数和步数

### 4. check_training.py
- 训练状态监控脚本
- 检查训练进程、模型文件和系统资源

## 使用方法

### 导入AI控制器
```python
from ai_controllers import create_ai_controller, OptimizedAIController

# 创建混合AI控制器
ai_controller = create_ai_controller(
    hero, enemy_group, screen_width, screen_height, 
    controller_type="hybrid"
)

# 或者直接使用优化的简单AI控制器
simple_ai = OptimizedAIController(
    hero, enemy_group, screen_width, screen_height, 
    is_player1=False
)
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

## 依赖要求

- Python 3.7+
- Pygame
- Stable Baselines3
- Gymnasium
- PyTorch
- NumPy

## 版本信息

- 版本: 1.0.0
- 作者: LightPlane AI Team
- 最后更新: 2024年
