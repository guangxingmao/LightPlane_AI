#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成AI战机训练脚本
训练AI战机以适应动态游戏策略，实现真正的三重AI协同
"""

import os
import sys
import argparse
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from stable_baselines3 import PPO, DQN, A2C
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
    from stable_baselines3.common.utils import set_random_seed
    SB3_AVAILABLE = True
    print("✅ Stable Baselines3 导入成功")
except ImportError as e:
    print(f"❌ Stable Baselines3 导入失败: {e}")
    print("💡 请安装: pip install stable-baselines3")
    SB3_AVAILABLE = False

try:
    from integrated_plane_env import IntegratedPlaneFighterEnv
    print("✅ 集成训练环境导入成功")
except ImportError as e:
    print(f"❌ 集成训练环境导入失败: {e}")
    print("💡 检查文件路径和导入")
    sys.exit(1)

class IntegratedPlaneTrainer:
    """集成AI战机训练器"""
    
    def __init__(self, algorithm="PPO", total_timesteps=2000000):
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
                    "net_arch": [dict(pi=[256, 256], vf=[256, 256])]  # 更大的网络
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
                    "net_arch": [256, 256]
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
                    "net_arch": [dict(pi=[256, 256], vf=[256, 256])]
                }
            }
        }
        
        # 输出目录
        self.output_dir = f"models/integrated_plane_{algorithm.lower()}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置随机种子
        set_random_seed(42)
        
        print(f"🎯 集成AI战机训练器初始化完成")
        print(f"   算法: {algorithm}")
        print(f"   训练步数: {total_timesteps:,}")
        print(f"   输出目录: {self.output_dir}")
        print(f"   环境类型: 集成训练环境（支持动态策略）")
    
    def create_environment(self, num_envs=8):
        """创建训练环境"""
        print(f"🌍 创建 {num_envs} 个集成训练环境...")
        
        def make_env():
            env = IntegratedPlaneFighterEnv()
            return env
        
        # 创建向量化环境
        env = DummyVecEnv([make_env for _ in range(num_envs)])
        
        # 添加环境标准化
        env = VecNormalize(
            env,
            norm_obs=True,
            norm_reward=True,
            clip_obs=10.0,
            clip_reward=10.0
        )
        
        print(f"✅ 集成训练环境创建成功")
        print(f"   环境数量: {num_envs}")
        print(f"   观察空间: {env.observation_space}")
        print(f"   动作空间: {env.action_space}")
        print(f"   环境标准化: 已启用")
        
        return env
    
    def create_eval_environment(self):
        """创建评估环境"""
        print(f"🌍 创建评估环境...")
        
        def make_eval_env():
            env = IntegratedPlaneFighterEnv(render_mode=None)
            return env
        
        eval_env = DummyVecEnv([make_eval_env])
        
        # 使用训练环境的标准化参数
        eval_env = VecNormalize(
            eval_env,
            norm_obs=True,
            norm_reward=False,  # 评估时不标准化奖励
            clip_obs=10.0
        )
        
        print(f"✅ 评估环境创建成功")
        return eval_env
    
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
        
        print(f"✅ {self.algorithm} 模型创建成功")
        print(f"   策略网络: MLP策略")
        print(f"   网络架构: {self.training_params[self.algorithm]['policy_kwargs']}")
        
        return model
    
    def setup_callbacks(self, eval_env):
        """设置训练回调"""
        print(f"🔧 设置训练回调...")
        
        # 评估回调
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=f"{self.output_dir}/best_model",
            log_path=f"{self.output_dir}/eval_logs",
            eval_freq=max(10000 // 8, 1),  # 每10000步评估一次
            deterministic=True,
            render=False
        )
        
        # 检查点回调
        checkpoint_callback = CheckpointCallback(
            save_freq=max(50000 // 8, 1),  # 每50000步保存一次
            save_path=f"{self.output_dir}/checkpoints",
            name_prefix="integrated_plane_model"
        )
        
        callbacks = [eval_callback, checkpoint_callback]
        
        print(f"✅ 训练回调设置完成")
        print(f"   评估频率: 每10000步")
        print(f"   检查点频率: 每50000步")
        print(f"   最佳模型保存: 已启用")
        
        return callbacks
    
    def train(self, model, env, eval_env):
        """开始训练"""
        print(f"🚀 开始训练集成AI战机...")
        print(f"   算法: {self.algorithm}")
        print(f"   总步数: {self.total_timesteps:,}")
        print(f"   环境数量: {env.num_envs}")
        print(f"   训练环境: 集成训练环境（动态策略）")
        
        start_time = time.time()
        
        # 训练模型
        model.learn(
            total_timesteps=self.total_timesteps,
            callback=self.setup_callbacks(eval_env),
            progress_bar=True
        )
        
        training_time = time.time() - start_time
        
        print(f"✅ 训练完成!")
        print(f"   训练时间: {training_time:.2f} 秒")
        print(f"   平均速度: {self.total_timesteps / training_time:.0f} 步/秒")
        
        return model
    
    def save_model(self, model, env, model_name="final"):
        """保存模型"""
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
        print(f"📊 开始模型评估...")
        print(f"   评估回合数: {num_episodes}")
        
        # 重置环境标准化参数
        eval_env.norm_reward = False
        
        episode_rewards = []
        episode_lengths = []
        
        for episode in range(num_episodes):
            obs, _ = eval_env.reset()
            episode_reward = 0
            episode_length = 0
            
            while True:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, _ = eval_env.step(action)
                episode_reward += reward[0]
                episode_length += 1
                
                if terminated[0] or truncated[0]:
                    break
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            
            if (episode + 1) % 10 == 0:
                print(f"   评估进度: {episode + 1}/{num_episodes}")
        
        # 计算统计信息
        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards)
        mean_length = np.mean(episode_lengths)
        max_reward = np.max(episode_rewards)
        min_reward = np.min(episode_rewards)
        
        print(f"📈 评估结果:")
        print(f"   平均奖励: {mean_reward:.2f} ± {std_reward:.2f}")
        print(f"   平均长度: {mean_length:.1f} 步")
        print(f"   最高奖励: {max_reward:.2f}")
        print(f"   最低奖励: {min_reward:.2f}")
        
        # 保存评估结果
        eval_results = {
            'episode_rewards': episode_rewards,
            'episode_lengths': episode_lengths,
            'mean_reward': mean_reward,
            'std_reward': std_reward,
            'mean_length': mean_length,
            'max_reward': max_reward,
            'min_reward': min_reward
        }
        
        eval_path = f"{self.output_dir}/evaluation_results.npz"
        np.savez(eval_path, **eval_results)
        print(f"✅ 评估结果保存到: {eval_path}")
        
        return eval_results
    
    def test_model(self, model, test_env, num_episodes=5):
        """测试模型（可视化）"""
        print(f"🧪 测试模型...")
        print(f"   测试回合数: {num_episodes}")
        print(f"   注意: 这是可视化测试，会显示游戏窗口")
        
        # 创建可视化测试环境
        test_env = IntegratedPlaneFighterEnv(render_mode="human")
        
        for episode in range(num_episodes):
            print(f"   测试回合 {episode + 1}/{num_episodes}")
            obs, _ = test_env.reset()
            episode_reward = 0
            episode_length = 0
            
            while True:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = test_env.step(action)
                episode_reward += reward
                episode_length += 1
                
                # 显示信息
                if episode_length % 100 == 0:
                    print(f"     步数: {episode_length}, 奖励: {episode_reward:.2f}, 分数: {info['score']}")
                
                if terminated or truncated:
                    break
            
            print(f"   回合 {episode + 1} 完成: 奖励={episode_reward:.2f}, 长度={episode_length}")
        
        test_env.close()
        print(f"✅ 模型测试完成")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="集成AI战机训练")
    parser.add_argument("--algorithm", type=str, default="PPO", 
                       choices=["PPO", "DQN", "A2C"], help="训练算法")
    parser.add_argument("--timesteps", type=int, default=2000000, 
                       help="训练总步数")
    parser.add_argument("--envs", type=int, default=8, 
                       help="并行环境数量")
    parser.add_argument("--eval", action="store_true", 
                       help="训练后评估模型")
    parser.add_argument("--test", action="store_true", 
                       help="训练后测试模型")
    
    args = parser.parse_args()
    
    print("🎯 集成AI战机训练系统")
    print("=" * 50)
    print(f"算法: {args.algorithm}")
    print(f"训练步数: {args.timesteps:,}")
    print(f"并行环境: {args.envs}")
    print(f"训练后评估: {args.eval}")
    print(f"训练后测试: {args.test}")
    print("=" * 50)
    
    if not SB3_AVAILABLE:
        print("❌ 无法训练，Stable Baselines3 未安装")
        return
    
    try:
        # 创建训练器
        trainer = IntegratedPlaneTrainer(args.algorithm, args.timesteps)
        
        # 创建训练环境
        train_env = trainer.create_environment(args.envs)
        
        # 创建评估环境
        eval_env = trainer.create_eval_environment()
        
        # 创建模型
        model = trainer.create_model(train_env)
        
        # 开始训练
        trainer.train(model, train_env, eval_env)
        
        # 保存模型
        model_path, env_normalize_path = trainer.save_model(model, train_env)
        
        # 评估模型
        if args.eval:
            trainer.evaluate_model(model, eval_env)
        
        # 测试模型
        if args.test:
            trainer.test_model(model, None)
        
        print(f"\n🎉 集成AI战机训练完成!")
        print(f"模型路径: {model_path}")
        print(f"环境标准化: {env_normalize_path}")
        print(f"下一步: 将新模型集成到游戏中，实现真正的三重AI协同")
        
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

