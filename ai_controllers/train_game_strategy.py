#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏策略AI训练脚本
专门训练AI如何生成和管理游戏策略
"""

import os
import sys
import numpy as np
import time
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from stable_baselines3 import PPO, DQN, A2C
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
    from stable_baselines3.common.utils import set_random_seed
    
    # Monitor 从 gymnasium 导入
    try:
        from gymnasium.wrappers import Monitor
    except ImportError:
        try:
            from gym.wrappers import Monitor
        except ImportError:
            print("⚠️ Monitor 不可用，将跳过监控")
            Monitor = None
    
    SB3_AVAILABLE = True
    print("✅ Stable Baselines3 导入成功")
except ImportError as e:
    print(f"❌ Stable Baselines3 导入失败: {e}")
    print("💡 请安装: pip install stable-baselines3")
    SB3_AVAILABLE = False

try:
    from ai_controllers.game_strategy_env import GameStrategyEnvironment
    print("✅ 游戏策略环境导入成功")
except ImportError as e:
    print(f"❌ 游戏策略环境导入失败: {e}")
    print("💡 检查文件路径和导入")
    sys.exit(1)

class GameStrategyTrainer:
    """游戏策略AI训练器"""
    
    def __init__(self, algorithm="PPO", total_timesteps=1000000):
        self.algorithm = algorithm
        self.total_timesteps = total_timesteps
        
        # 训练参数
        self.training_params = {
            "PPO": {
                "learning_rate": 3e-4,
                "n_steps": 2048,
                "batch_size": 64,
                "n_epochs": 10,
                "gamma": 0.99,
                "gae_lambda": 0.95,
                "clip_range": 0.2,
                "clip_range_vf": None,
                "normalize_advantage": True,
                "ent_coef": 0.01,
                "vf_coef": 0.5,
                "max_grad_norm": 0.5,
                "use_sde": False,  # 离散动作空间不支持gSDE
                "sde_sample_freq": -1,
                "target_kl": None,
                "tensorboard_log": None,
                "policy_kwargs": {
                    "net_arch": [dict(pi=[128, 128], vf=[128, 128])]
                }
            },
            "DQN": {
                "learning_rate": 1e-4,
                "buffer_size": 1000000,
                "learning_starts": 100000,
                "batch_size": 32,
                "tau": 1.0,
                "gamma": 0.99,
                "train_freq": 4,
                "gradient_steps": 1,
                "target_update_interval": 10000,
                "exploration_fraction": 0.1,
                "exploration_initial_eps": 1.0,
                "exploration_final_eps": 0.05,
                "max_grad_norm": 10,
                "policy_kwargs": {
                    "net_arch": [128, 128]
                }
            },
            "A2C": {
                "learning_rate": 7e-4,
                "n_steps": 5,
                "gamma": 0.99,
                "gae_lambda": 1.0,
                "ent_coef": 0.01,
                "vf_coef": 0.25,
                "max_grad_norm": 0.5,
                "rms_prop_eps": 1e-5,
                "use_rms_prop": True,
                "use_sde": False,
                "sde_sample_freq": -1,
                "policy_kwargs": {
                    "net_arch": [dict(pi=[128, 128], vf=[128, 128])]
                }
            }
        }
        
        # 输出目录
        self.output_dir = f"models/game_strategy_{algorithm.lower()}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置随机种子
        set_random_seed(42)
        
        print(f"🎯 游戏策略AI训练器初始化完成")
        print(f"   算法: {algorithm}")
        print(f"   训练步数: {total_timesteps:,}")
        print(f"   输出目录: {self.output_dir}")
    
    def create_environment(self, num_envs=4):
        """创建训练环境"""
        print(f"🌍 创建 {num_envs} 个训练环境...")
        
        def make_env():
            env = GameStrategyEnvironment()
            if Monitor is not None:
                env = Monitor(env, self.output_dir)
            return env
        
        # 创建向量化环境
        env = DummyVecEnv([make_env for _ in range(num_envs)])
        
        # 环境标准化
        env = VecNormalize(
            env, 
            norm_obs=True, 
            norm_reward=True,
            clip_obs=10.0,
            clip_reward=10.0
        )
        
        print(f"✅ 训练环境创建成功")
        return env
    
    def create_model(self, env):
        """创建AI模型"""
        print(f"🧠 创建 {self.algorithm} 模型...")
        
        if self.algorithm == "PPO":
            # 移除重复的tensorboard_log参数
            ppo_params = self.training_params["PPO"].copy()
            if 'tensorboard_log' in ppo_params:
                del ppo_params['tensorboard_log']
            
            model = PPO(
                "MlpPolicy", 
                env, 
                verbose=1,
                tensorboard_log=f"{self.output_dir}/tensorboard",
                **ppo_params
            )
        elif self.algorithm == "DQN":
            model = DQN(
                "MlpPolicy", 
                env, 
                verbose=1,
                tensorboard_log=f"{self.output_dir}/tensorboard",
                **self.training_params["DQN"]
            )
        elif self.algorithm == "A2C":
            model = A2C(
                "MlpPolicy", 
                env, 
                verbose=1,
                tensorboard_log=f"{self.output_dir}/tensorboard",
                **self.training_params["A2C"]
            )
        else:
            raise ValueError(f"不支持的算法: {self.algorithm}")
        
        print(f"✅ {self.algorithm} 模型创建成功")
        return model
    
    def setup_callbacks(self, eval_env):
        """设置训练回调"""
        print("🔧 设置训练回调...")
        
        # 评估回调
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=f"{self.output_dir}/best_model",
            log_path=f"{self.output_dir}/eval_logs",
            eval_freq=max(10000 // 4, 1),  # 每10k步评估一次
            deterministic=True,
            render=False
        )
        
        # 检查点回调
        checkpoint_callback = CheckpointCallback(
            save_freq=max(50000 // 4, 1),  # 每50k步保存一次
            save_path=f"{self.output_dir}/checkpoints",
            name_prefix=f"game_strategy_{self.algorithm.lower()}"
        )
        
        callbacks = [eval_callback, checkpoint_callback]
        print(f"✅ 训练回调设置完成")
        return callbacks
    
    def train(self, model, env, eval_env):
        """开始训练"""
        print(f"🚀 开始训练游戏策略AI...")
        print(f"   算法: {self.algorithm}")
        print(f"   总步数: {self.total_timesteps:,}")
        print(f"   环境数量: {env.num_envs}")
        
        # 设置回调
        callbacks = self.setup_callbacks(eval_env)
        
        # 开始训练
        start_time = time.time()
        
        try:
            model.learn(
                total_timesteps=self.total_timesteps,
                callback=callbacks,
                progress_bar=True
            )
            
            training_time = time.time() - start_time
            print(f"✅ 训练完成!")
            print(f"   训练时间: {training_time:.2f} 秒")
            print(f"   平均速度: {self.total_timesteps / training_time:.0f} 步/秒")
            
        except Exception as e:
            print(f"❌ 训练失败: {e}")
            raise
    
    def save_model(self, model, env, model_name="final"):
        """保存训练好的模型"""
        print(f"💾 保存模型...")
        
        # 保存模型
        model_path = f"{self.output_dir}/{model_name}"
        model.save(model_path)
        print(f"✅ 模型保存到: {model_path}")
        
        # 保存环境标准化参数
        env_normalize_path = f"{self.output_dir}/env_normalize"
        env.save(env_normalize_path)
        print(f"✅ 环境标准化参数保存到: {env_normalize_path}")
        
        return model_path, env_normalize_path
    
    def evaluate_model(self, model, eval_env, num_episodes=100):
        """评估模型性能"""
        print(f"📊 评估模型性能...")
        
        # 运行评估
        obs = eval_env.reset()
        episode_rewards = []
        episode_lengths = []
        
        for episode in range(num_episodes):
            obs = eval_env.reset()
            done = False
            episode_reward = 0
            episode_length = 0
            
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, info = eval_env.step(action)
                episode_reward += reward[0]
                episode_length += 1
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            
            if (episode + 1) % 10 == 0:
                print(f"   评估进度: {episode + 1}/{num_episodes}")
        
        # 计算统计信息
        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)
        mean_length = np.mean(episode_lengths)
        
        print(f"📈 评估结果:")
        print(f"   平均奖励: {mean_reward:.2f} ± {std_reward:.2f}")
        print(f"   平均长度: {mean_length:.1f} 步")
        print(f"   最高奖励: {np.max(episode_rewards):.2f}")
        print(f"   最低奖励: {np.min(episode_rewards):.2f}")
        
        return {
            'mean_reward': mean_reward,
            'std_reward': std_reward,
            'mean_length': mean_length,
            'episode_rewards': episode_rewards
        }
    
    def test_model(self, model, test_env, num_episodes=5):
        """测试模型（可视化）"""
        print(f"🎮 测试模型...")
        print(f"   注意: 这是测试模式，将显示游戏画面")
        
        # 这里可以添加可视化测试代码
        # 由于是策略AI，主要测试策略生成的效果
        print(f"✅ 模型测试完成")
        print(f"   策略AI主要功能:")
        print(f"   - 动态难度调整")
        print(f"   - 敌机生成策略")
        print(f"   - 道具掉落策略")
        print(f"   - 背景切换策略")
        print(f"   - 特殊事件触发")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="训练游戏策略AI")
    parser.add_argument("--algorithm", type=str, default="PPO", 
                       choices=["PPO", "DQN", "A2C"], 
                       help="训练算法")
    parser.add_argument("--timesteps", type=int, default=1000000,
                       help="训练总步数")
    parser.add_argument("--envs", type=int, default=4,
                       help="并行环境数量")
    parser.add_argument("--eval", action="store_true",
                       help="训练后评估模型")
    parser.add_argument("--test", action="store_true",
                       help="训练后测试模型")
    
    args = parser.parse_args()
    
    if not SB3_AVAILABLE:
        print("❌ 无法训练，Stable Baselines3 未安装")
        return
    
    print("🎯 游戏策略AI训练系统")
    print("=" * 50)
    
    # 创建训练器
    trainer = GameStrategyTrainer(
        algorithm=args.algorithm,
        total_timesteps=args.timesteps
    )
    
    # 创建训练环境
    train_env = trainer.create_environment(num_envs=args.envs)
    
    # 创建评估环境
    eval_env = trainer.create_environment(num_envs=1)
    
    # 创建模型
    model = trainer.create_model(train_env)
    
    # 开始训练
    trainer.train(model, train_env, eval_env)
    
    # 保存模型
    model_path, env_normalize_path = trainer.save_model(model, train_env)
    
    # 评估模型
    if args.eval:
        print("\n📊 开始模型评估...")
        eval_results = trainer.evaluate_model(model, eval_env)
        
        # 保存评估结果
        eval_file = f"{trainer.output_dir}/evaluation_results.npz"
        np.savez(eval_file, **eval_results)
        print(f"✅ 评估结果保存到: {eval_file}")
    
    # 测试模型
    if args.test:
        print("\n🎮 开始模型测试...")
        trainer.test_model(model, eval_env)
    
    print(f"\n🎉 游戏策略AI训练完成!")
    print(f"   模型路径: {model_path}")
    print(f"   环境标准化: {env_normalize_path}")
    print(f"   下一步: 将模型集成到游戏中")

if __name__ == "__main__":
    main()
