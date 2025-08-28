#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI决策系统训练脚本
训练AI控制器进行智能决策，替代规则AI
"""

import os
import sys
import time
import numpy as np
from typing import Dict, List, Any
import argparse

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from stable_baselines3 import PPO, DQN, A2C
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
    from stable_baselines3.common.monitor import Monitor
    SB3_AVAILABLE = True
    print("✅ Stable Baselines3 可用")
except ImportError as e:
    SB3_AVAILABLE = False
    print(f"❌ Stable Baselines3 未安装: {e}")
    print("请运行: pip install stable-baselines3")

from ai_game_env import AIGameEnvironment

class AIDecisionTrainer:
    """AI决策训练器"""
    
    def __init__(self, algorithm="PPO", total_timesteps=1000000):
        self.algorithm = algorithm
        self.total_timesteps = total_timesteps
        self.model = None
        self.env = None
        
        # 训练参数
        self.training_params = {
            'PPO': {
                'learning_rate': 3e-4,
                'n_steps': 2048,
                'batch_size': 64,
                'n_epochs': 10,
                'gamma': 0.99,
                'gae_lambda': 0.95,
                'clip_range': 0.2,
                'ent_coef': 0.01,
                'vf_coef': 0.5,
                'max_grad_norm': 0.5
            },
            'DQN': {
                'learning_rate': 1e-4,
                'buffer_size': 100000,
                'learning_starts': 1000,
                'batch_size': 32,
                'gamma': 0.99,
                'train_freq': 4,
                'gradient_steps': 1,
                'target_update_interval': 1000,
                'exploration_fraction': 0.1,
                'exploration_initial_eps': 1.0,
                'exploration_final_eps': 0.05
            },
            'A2C': {
                'learning_rate': 7e-4,
                'n_steps': 5,
                'gamma': 0.99,
                'gae_lambda': 1.0,
                'ent_coef': 0.01,
                'vf_coef': 0.5,
                'max_grad_norm': 0.5
            }
        }
        
        # 创建输出目录
        self.output_dir = f"models/ai_decision_{algorithm.lower()}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"🤖 AI决策训练器初始化完成")
        print(f"   算法: {algorithm}")
        print(f"   训练步数: {total_timesteps:,}")
        print(f"   输出目录: {self.output_dir}")
    
    def create_environment(self, num_envs=4):
        """创建训练环境"""
        print(f"🌍 创建{num_envs}个训练环境...")
        
        def make_env():
            env = AIGameEnvironment()
            env = Monitor(env)
            return env
        
        # 创建向量化环境
        self.env = DummyVecEnv([make_env for _ in range(num_envs)])
        
        # 标准化观察
        self.env = VecNormalize(
            self.env, 
            norm_obs=True, 
            norm_reward=True,
            clip_obs=10.0,
            clip_reward=10.0
        )
        
        print("✅ 训练环境创建完成")
        return self.env
    
    def create_model(self):
        """创建AI模型"""
        if not SB3_AVAILABLE:
            raise ImportError("Stable Baselines3 未安装")
        
        print(f"🧠 创建{self.algorithm}模型...")
        
        # 获取算法参数
        params = self.training_params[self.algorithm]
        
        if self.algorithm == "PPO":
            self.model = PPO(
                "MlpPolicy",
                self.env,
                verbose=1,
                tensorboard_log=f"logs/ai_decision_{self.algorithm.lower()}",
                **params
            )
        elif self.algorithm == "DQN":
            self.model = DQN(
                "MlpPolicy",
                self.env,
                verbose=1,
                tensorboard_log=f"logs/ai_decision_{self.algorithm.lower()}",
                **params
            )
        elif self.algorithm == "A2C":
            self.model = A2C(
                "MlpPolicy",
                self.env,
                verbose=1,
                tensorboard_log=f"logs/ai_decision_{self.algorithm.lower()}",
                **params
            )
        else:
            raise ValueError(f"不支持的算法: {self.algorithm}")
        
        print(f"✅ {self.algorithm}模型创建完成")
        return self.model
    
    def setup_callbacks(self):
        """设置训练回调"""
        print("📋 设置训练回调...")
        
        callbacks = []
        
        # 评估回调
        eval_env = DummyVecEnv([lambda: AIGameEnvironment()])
        eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=False)
        
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=f"{self.output_dir}/best_model",
            log_path=f"{self.output_dir}/logs",
            eval_freq=max(10000 // 4, 1),  # 每10k步评估一次
            n_eval_episodes=10,
            deterministic=True,
            render=False
        )
        callbacks.append(eval_callback)
        
        # 检查点回调
        checkpoint_callback = CheckpointCallback(
            save_freq=max(50000 // 4, 1),  # 每50k步保存一次
            save_path=f"{self.output_dir}/checkpoints",
            name_prefix=f"ai_decision_{self.algorithm.lower()}"
        )
        callbacks.append(checkpoint_callback)
        
        print("✅ 训练回调设置完成")
        return callbacks
    
    def train(self):
        """开始训练"""
        if not self.model:
            raise ValueError("模型未创建，请先调用create_model()")
        
        print(f"🚀 开始训练{self.algorithm}模型...")
        print(f"   总训练步数: {self.total_timesteps:,}")
        print(f"   开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 设置回调
        callbacks = self.setup_callbacks()
        
        # 开始训练
        start_time = time.time()
        
        try:
            self.model.learn(
                total_timesteps=self.total_timesteps,
                callback=callbacks,
                progress_bar=True
            )
            
            training_time = time.time() - start_time
            print(f"✅ 训练完成！")
            print(f"   训练时间: {training_time:.2f}秒")
            print(f"   平均速度: {self.total_timesteps / training_time:.0f} 步/秒")
            
        except Exception as e:
            print(f"❌ 训练失败: {e}")
            raise
        
        return self.model
    
    def save_model(self, model_name="final"):
        """保存训练好的模型"""
        if not self.model:
            raise ValueError("模型未创建")
        
        model_path = f"{self.output_dir}/{model_name}"
        print(f"💾 保存模型到: {model_path}")
        
        try:
            self.model.save(model_path)
            print(f"✅ 模型保存成功: {model_path}")
            
            # 保存环境标准化参数
            env_path = f"{self.output_dir}/env_normalize"
            self.env.save(env_path)
            print(f"✅ 环境标准化参数保存成功: {env_path}")
            
        except Exception as e:
            print(f"❌ 模型保存失败: {e}")
            raise
        
        return model_path
    
    def evaluate_model(self, num_episodes=100):
        """评估模型性能"""
        if not self.model:
            raise ValueError("模型未创建")
        
        print(f"📊 评估模型性能 ({num_episodes} 局)...")
        
        # 创建评估环境
        eval_env = AIGameEnvironment()
        
        # 性能统计
        episode_rewards = []
        episode_lengths = []
        survival_times = []
        enemies_killed = []
        power_ups_collected = []
        damage_taken = []
        accuracy_rates = []
        
        for episode in range(num_episodes):
            obs, _ = eval_env.reset()
            episode_reward = 0
            step_count = 0
            
            while not eval_env._is_done():
                # 使用模型预测动作
                action, _ = self.model.predict(obs, deterministic=True)
                
                # 执行动作
                obs, reward, done, truncated, info = eval_env.step(action)
                episode_reward += reward
                step_count += 1
            
            # 记录统计信息
            episode_rewards.append(episode_reward)
            episode_lengths.append(step_count)
            survival_times.append(eval_env.stats['survival_time'])
            enemies_killed.append(eval_env.stats['enemies_killed'])
            power_ups_collected.append(eval_env.stats['power_ups_collected'])
            damage_taken.append(eval_env.stats['damage_taken'])
            
            accuracy = eval_env.stats['shots_hit'] / max(1, eval_env.stats['shots_fired'])
            accuracy_rates.append(accuracy)
            
            if (episode + 1) % 10 == 0:
                print(f"   完成 {episode + 1}/{num_episodes} 局")
        
        # 计算统计结果
        results = {
            'episode_rewards': {
                'mean': np.mean(episode_rewards),
                'std': np.std(episode_rewards),
                'min': np.min(episode_rewards),
                'max': np.max(episode_rewards)
            },
            'episode_lengths': {
                'mean': np.mean(episode_lengths),
                'std': np.std(episode_lengths)
            },
            'survival_times': {
                'mean': np.mean(survival_times),
                'std': np.std(survival_times)
            },
            'enemies_killed': {
                'mean': np.mean(enemies_killed),
                'std': np.std(enemies_killed)
            },
            'power_ups_collected': {
                'mean': np.mean(power_ups_collected),
                'std': np.std(power_ups_collected)
            },
            'damage_taken': {
                'mean': np.mean(damage_taken),
                'std': np.std(damage_taken)
            },
            'accuracy_rates': {
                'mean': np.mean(accuracy_rates),
                'std': np.std(accuracy_rates)
            }
        }
        
        # 打印评估结果
        print("\n📊 模型评估结果:")
        print(f"   平均奖励: {results['episode_rewards']['mean']:.2f} ± {results['episode_rewards']['std']:.2f}")
        print(f"   平均生存时间: {results['survival_times']['mean']:.1f} ± {results['survival_times']['std']:.1f} 步")
        print(f"   平均击杀数: {results['enemies_killed']['mean']:.1f} ± {results['enemies_killed']['std']:.1f}")
        print(f"   平均道具收集: {results['power_ups_collected']['mean']:.1f} ± {results['power_ups_collected']['std']:.1f}")
        print(f"   平均伤害: {results['damage_taken']['mean']:.1f} ± {results['damage_taken']['std']:.1f}")
        print(f"   平均命中率: {results['accuracy_rates']['mean']:.3f} ± {results['accuracy_rates']['std']:.3f}")
        
        return results
    
    def test_model(self, num_episodes=5):
        """测试模型（可视化）"""
        if not self.model:
            raise ValueError("模型未创建")
        
        print(f"🎮 测试模型 ({num_episodes} 局)...")
        
        for episode in range(num_episodes):
            print(f"\n--- 第 {episode + 1} 局测试 ---")
            
            obs, _ = self.env.reset()
            episode_reward = 0
            step_count = 0
            
            while not self.env._is_done():
                # 使用模型预测动作
                action, _ = self.model.predict(obs, deterministic=True)
                
                # 执行动作
                obs, reward, done, truncated, info = self.env.step(action)
                episode_reward += reward
                step_count += 1
                
                # 每100步打印一次状态
                if step_count % 100 == 0:
                    print(f"   步数: {step_count}, 奖励: {episode_reward:.2f}, 生命: {self.env.life}")
            
            print(f"   第 {episode + 1} 局完成:")
            print(f"     总步数: {step_count}")
            print(f"     总奖励: {episode_reward:.2f}")
            print(f"     最终生命: {self.env.life}")
            print(f"     击杀数: {self.env.stats['enemies_killed']}")
            print(f"     道具收集: {self.env.stats['power_ups_collected']}")
            print(f"     命中率: {self.env.stats['shots_hit'] / max(1, self.env.stats['shots_fired']):.3f}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI决策系统训练")
    parser.add_argument("--algorithm", type=str, default="PPO", 
                       choices=["PPO", "DQN", "A2C"], help="训练算法")
    parser.add_argument("--timesteps", type=int, default=1000000, 
                       help="训练步数")
    parser.add_argument("--envs", type=int, default=4, 
                       help="并行环境数量")
    parser.add_argument("--eval", action="store_true", 
                       help="训练后评估模型")
    parser.add_argument("--test", action="store_true", 
                       help="训练后测试模型")
    
    args = parser.parse_args()
    
    if not SB3_AVAILABLE:
        print("❌ 无法继续：Stable Baselines3 未安装")
        print("请运行: pip install stable-baselines3")
        return
    
    try:
        # 创建训练器
        trainer = AIDecisionTrainer(
            algorithm=args.algorithm,
            total_timesteps=args.timesteps
        )
        
        # 创建环境
        trainer.create_environment(num_envs=args.envs)
        
        # 创建模型
        trainer.create_model()
        
        # 开始训练
        trainer.train()
        
        # 保存模型
        model_path = trainer.save_model()
        
        # 评估模型
        if args.eval:
            trainer.evaluate_model()
        
        # 测试模型
        if args.test:
            trainer.test_model()
        
        print(f"\n🎉 AI决策训练完成！")
        print(f"   模型保存位置: {model_path}")
        print(f"   可以在游戏中使用这个模型了！")
        
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
