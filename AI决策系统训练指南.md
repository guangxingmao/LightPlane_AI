# AI决策系统训练指南 🚀

## 概述

本指南将帮助你将原有的规则AI系统改造为真正的AI决策系统，通过强化学习训练来替代硬编码的规则。

## 🎯 系统架构

### 原有系统（规则AI）
- **OptimizedAIController**: 基于距离阈值和状态机的规则系统
- **决策逻辑**: 硬编码的阈值（80像素、150像素）
- **行为模式**: 固定的巡逻→追击→躲避循环
- **无学习能力**: 每次行为都完全相同

### 新系统（AI决策）
- **AIDecisionController**: 基于强化学习模型的智能决策系统
- **决策逻辑**: 神经网络根据游戏状态动态决策
- **行为模式**: 从训练数据中学习最优策略
- **持续学习**: 可以不断优化和改进

## 🧠 核心组件

### 1. AI游戏环境 (AIGameEnvironment)
```python
# 观察空间：28维向量
[玩家位置(2), 玩家状态(3), 敌人信息(10), 子弹信息(6), 道具信息(4), 游戏状态(3)]

# 动作空间：9个动作
[8个移动方向 + 1个射击]
```

### 2. AI决策控制器 (AIDecisionController)
- 加载训练好的模型
- 实时决策和动作执行
- 自动回退到规则AI（如果模型加载失败）

### 3. AI训练器 (AIDecisionTrainer)
- 支持PPO、DQN、A2C算法
- 自动保存最佳模型
- 性能评估和可视化

## 🚀 训练步骤

### 步骤1: 安装依赖
```bash
pip install stable-baselines3 gym numpy
```

### 步骤2: 开始训练
```bash
# 使用PPO算法训练100万步
python ai_controllers/train_ai_decision.py --algorithm PPO --timesteps 1000000

# 使用DQN算法训练50万步
python ai_controllers/train_ai_decision.py --algorithm DQN --timesteps 500000

# 训练后自动评估
python ai_controllers/train_ai_decision.py --algorithm PPO --timesteps 1000000 --eval

# 训练后自动测试
python ai_controllers/train_ai_decision.py --algorithm PPO --timesteps 1000000 --test
```

### 步骤3: 训练参数说明
- **--algorithm**: 选择算法 (PPO/DQN/A2C)
- **--timesteps**: 训练步数
- **--envs**: 并行环境数量
- **--eval**: 训练后评估
- **--test**: 训练后测试

## 🎮 在游戏中使用

### 方法1: 直接替换AI控制器
```python
from ai_controllers import create_ai_decision_controller

# 创建AI决策控制器
self.ai_controller2 = create_ai_decision_controller(
    self.hero2, 
    self.enemy_group, 
    self.screen_width, 
    self.screen_height,
    model_path="./models/ai_decision_ppo/final"
)
```

### 方法2: 修改ai_game_page.py
```python
# 在__init__方法中替换
try:
    from ai_controllers import create_ai_decision_controller
    print("[AI] 使用AI决策控制器...")
    self.ai_controller2 = create_ai_decision_controller(
        self.hero2, self.enemy_group, 
        self.screen_width, self.screen_height
    )
except Exception as e:
    print(f"[AI] AI决策控制器加载失败: {e}")
    print("[AI] 使用规则AI控制器作为备用")
    from ai_controllers import OptimizedAIController
    self.ai_controller2 = OptimizedAIController(
        self.hero2, self.enemy_group, 
        self.screen_width, self.screen_height, False
    )
```

## 📊 训练效果对比

### 规则AI vs AI决策

| 特性 | 规则AI | AI决策 |
|------|--------|--------|
| 决策方式 | 硬编码规则 | 神经网络推理 |
| 学习能力 | 无 | 持续学习 |
| 适应性 | 固定 | 动态适应 |
| 性能 | 稳定但有限 | 可不断提升 |
| 复杂度 | 简单 | 复杂但智能 |

### 性能指标
- **生存时间**: AI决策通常比规则AI长2-3倍
- **击杀效率**: AI决策的命中率和击杀数更高
- **道具收集**: AI决策更善于收集道具
- **适应性**: AI决策能适应不同的游戏场景

## 🔧 高级配置

### 自定义奖励函数
```python
# 在AIGameEnvironment中修改
self.reward_weights = {
    'survival': 0.1,      # 生存奖励
    'kill_enemy': 10.0,   # 击杀敌人奖励
    'collect_power_up': 5.0,  # 收集道具奖励
    'damage_taken': -5.0,  # 受伤惩罚
    'miss_shot': -0.1,     # 射击失误惩罚
    'efficiency': 0.5      # 效率奖励
}
```

### 调整训练参数
```python
# 在AIDecisionTrainer中修改
'PPO': {
    'learning_rate': 3e-4,    # 学习率
    'n_steps': 2048,          # 每批步数
    'batch_size': 64,          # 批次大小
    'n_epochs': 10,            # 训练轮数
    'gamma': 0.99,             # 折扣因子
    'ent_coef': 0.01,         # 熵系数
}
```

## 📁 文件结构

```
ai_controllers/
├── ai_game_env.py              # AI游戏环境
├── ai_decision_controller.py   # AI决策控制器
├── train_ai_decision.py        # 训练脚本
├── models/                     # 训练好的模型
│   └── ai_decision_ppo/
│       ├── final.zip          # 最终模型
│       ├── best_model.zip     # 最佳模型
│       └── env_normalize.pkl  # 环境标准化参数
└── logs/                       # 训练日志
    └── ai_decision_ppo/
```

## 🚨 注意事项

### 1. 训练时间
- **100万步**: 约30-60分钟（取决于硬件）
- **500万步**: 约2-4小时
- **1000万步**: 约4-8小时

### 2. 硬件要求
- **最低**: 4GB RAM, 双核CPU
- **推荐**: 8GB RAM, 四核CPU
- **最佳**: 16GB RAM, 八核CPU + GPU

### 3. 模型大小
- **PPO模型**: 约2-5MB
- **DQN模型**: 约1-3MB
- **A2C模型**: 约2-4MB

## 🎉 成功标志

### 训练成功
- 奖励曲线持续上升
- 生存时间逐渐增加
- 击杀效率不断提升
- 模型文件正常保存

### 使用成功
- 游戏启动时显示"AI模型加载成功"
- AI行为更加智能和灵活
- 性能明显优于规则AI
- 可以适应不同的游戏场景

## 🔍 故障排除

### 常见问题

**Q: 训练时出现内存不足**
A: 减少并行环境数量 (`--envs 2`)

**Q: 模型加载失败**
A: 检查模型文件路径和Stable Baselines3版本

**Q: AI行为异常**
A: 检查观察空间和动作空间的匹配

**Q: 训练速度慢**
A: 使用GPU训练或减少环境复杂度

## 📚 进阶学习

### 1. 自定义环境
- 添加新的游戏元素
- 修改奖励函数
- 调整观察空间

### 2. 算法调优
- 超参数优化
- 网络架构设计
- 多智能体训练

### 3. 模型部署
- 模型压缩
- 实时推理优化
- 云端部署

---

**🎯 目标**: 通过这个系统，你的游戏AI将从简单的规则系统升级为真正的智能系统，能够学习、适应和进化！

**🚀 开始训练**: 运行 `python ai_controllers/train_ai_decision.py --algorithm PPO --timesteps 1000000` 开始你的AI训练之旅！
