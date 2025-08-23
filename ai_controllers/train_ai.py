"""
使用Stable Baselines3训练飞机大战AI
使用PPO算法进行强化学习训练
"""

import os
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from stable_baselines3.common.logger import configure
import numpy as np

# 导入我们的环境
from plane_fighter_env import PlaneFighterEnv


def create_training_env():
    """创建训练环境"""
    def _init():
        return PlaneFighterEnv(
            screen_width=1280,
            screen_height=720,
            render_mode=None  # 训练时不渲染，提高速度
        )
    return _init


def create_eval_env():
    """创建评估环境"""
    def _init():
        return PlaneFighterEnv(
            screen_width=1280,
            screen_height=720,
            render_mode=None
        )
    return _init


def train_ppo_agent(
    total_timesteps=500000,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.01,
    vf_coef=0.5,
    max_grad_norm=0.5,
    save_path="./models/",
    log_path="./logs/",
    continue_from=None
):
    """
    训练PPO智能体
    
    Args:
        total_timesteps: 总训练步数
        learning_rate: 学习率
        n_steps: 每次更新的步数
        batch_size: 批大小
        n_epochs: 每次更新的轮数
        gamma: 折扣因子
        gae_lambda: GAE参数
        clip_range: PPO裁剪范围
        ent_coef: 熵系数
        vf_coef: 价值函数系数
        max_grad_norm: 梯度裁剪
        save_path: 模型保存路径
        log_path: 日志路径
    """
    
    # 创建保存目录
    os.makedirs(save_path, exist_ok=True)
    os.makedirs(log_path, exist_ok=True)
    
    print("🚀 开始训练飞机大战AI...")
    print(f"📊 总训练步数: {total_timesteps:,}")
    print(f"📁 模型保存路径: {save_path}")
    print(f"📝 日志路径: {log_path}")
    
    # 创建向量化环境（并行训练）
    n_envs = 4  # 4个并行环境
    env = make_vec_env(create_training_env(), n_envs=n_envs)
    eval_env = make_vec_env(create_eval_env(), n_envs=1)
    
    print(f"🔄 创建了 {n_envs} 个并行训练环境")
    
    # 创建或加载PPO模型
    if continue_from and os.path.exists(f"{continue_from}.zip"):
        print(f"🔄 从现有模型继续训练: {continue_from}")
        model = PPO.load(continue_from, env=env, verbose=1)
        print("✅ 现有模型加载成功，继续训练...")
    else:
        print("🆕 创建新的PPO模型")
        model = PPO(
            "MlpPolicy",  # 多层感知机策略
            env,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            gae_lambda=gae_lambda,
            clip_range=clip_range,
            ent_coef=ent_coef,
            vf_coef=vf_coef,
            max_grad_norm=max_grad_norm,
            verbose=1,
            device="auto",  # 自动选择CPU/GPU
            tensorboard_log=log_path
        )
    
    print("🧠 PPO模型创建完成!")
    print(f"📐 观察空间: {env.observation_space}")
    print(f"🎮 动作空间: {env.action_space}")
    
    # 设置回调函数
    callbacks = []
    
    # 评估回调
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=save_path,
        log_path=log_path,
        eval_freq=10000,  # 每10000步评估一次
        deterministic=True,
        render=False,
        verbose=1
    )
    callbacks.append(eval_callback)
    
    # 检查点回调
    checkpoint_callback = CheckpointCallback(
        save_freq=50000,  # 每50000步保存一次
        save_path=save_path,
        name_prefix="ppo_plane_fighter"
    )
    callbacks.append(checkpoint_callback)
    
    print("📋 回调函数设置完成")
    
    try:
        # 开始训练
        print("🏋️ 开始训练...")
        model.learn(
            total_timesteps=total_timesteps,
            callback=callbacks,
            progress_bar=True
        )
        
        # 保存最终模型
        final_model_path = os.path.join(save_path, "ppo_plane_fighter_final")
        model.save(final_model_path)
        print(f"💾 最终模型已保存: {final_model_path}")
        
    except KeyboardInterrupt:
        print("⏹️ 训练被用户中断")
        # 保存当前模型
        interrupted_model_path = os.path.join(save_path, "ppo_plane_fighter_interrupted")
        model.save(interrupted_model_path)
        print(f"💾 中断模型已保存: {interrupted_model_path}")
    
    finally:
        # 关闭环境
        env.close()
        eval_env.close()
        print("✅ 训练完成，环境已关闭")


def test_trained_model(model_path, episodes=5):
    """
    测试训练好的模型
    
    Args:
        model_path: 模型路径
        episodes: 测试回合数
    """
    
    print(f"🧪 测试模型: {model_path}")
    
    # 创建测试环境
    env = PlaneFighterEnv(render_mode="rgb_array")
    
    try:
        # 加载模型
        model = PPO.load(model_path)
        print("✅ 模型加载成功")
        
        # 测试多个回合
        total_scores = []
        total_steps = []
        
        for episode in range(episodes):
            obs, info = env.reset()
            episode_score = 0
            episode_steps = 0
            
            print(f"🎮 开始第 {episode + 1} 回合...")
            
            while True:
                # AI做决策
                action, _states = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(action)
                
                episode_score += reward
                episode_steps += 1
                
                if terminated or truncated:
                    break
            
            final_score = info['score']
            total_scores.append(final_score)
            total_steps.append(episode_steps)
            
            print(f"📊 第 {episode + 1} 回合结束:")
            print(f"   游戏得分: {final_score}")
            print(f"   存活步数: {episode_steps}")
            print(f"   总奖励: {episode_score:.2f}")
            print()
        
        # 统计结果
        avg_score = np.mean(total_scores)
        avg_steps = np.mean(total_steps)
        
        print("📈 测试结果统计:")
        print(f"   平均游戏得分: {avg_score:.2f}")
        print(f"   平均存活步数: {avg_steps:.0f}")
        print(f"   最高得分: {max(total_scores)}")
        print(f"   最长存活: {max(total_steps)}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        env.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="飞机大战AI训练")
    parser.add_argument("--mode", choices=["train", "test"], default="train",
                       help="运行模式: train(训练) 或 test(测试)")
    parser.add_argument("--timesteps", type=int, default=500000,
                       help="训练步数 (默认: 500000)")
    parser.add_argument("--model", type=str, default="./models/best_model",
                       help="模型路径 (测试模式使用)")
    parser.add_argument("--episodes", type=int, default=5,
                       help="测试回合数 (默认: 5)")
    parser.add_argument("--continue_from", type=str, default=None,
                       help="从现有模型继续训练 (模型路径，不包含.zip扩展名)")
    
    args = parser.parse_args()
    
    if args.mode == "train":
        print("🎯 训练模式")
        train_ppo_agent(total_timesteps=args.timesteps, continue_from=args.continue_from)
    
    elif args.mode == "test":
        print("🧪 测试模式")
        test_trained_model(args.model, args.episodes)


if __name__ == "__main__":
    main()
