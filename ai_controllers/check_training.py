#!/usr/bin/env python3
"""
简单的AI训练状态检查脚本
"""

import os
import time
import psutil
from datetime import datetime

def check_training():
    """检查训练状态"""
    print("🚀 AI训练状态检查")
    print("=" * 40)
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查训练进程
    print("📊 训练进程状态:")
    training_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['name'] == 'Python' and any('train_ai.py' in cmd for cmd in proc.info['cmdline'] if cmd):
                training_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if training_processes:
        for proc in training_processes:
            try:
                cpu_percent = proc.cpu_percent()
                memory_percent = proc.memory_percent()
                print(f"  ✅ 训练进程运行中 (PID: {proc.pid})")
                print(f"     CPU使用率: {cpu_percent:.1f}%")
                print(f"     内存使用率: {memory_percent:.1f}%")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"  ❌ 无法获取进程信息 (PID: {proc.pid})")
    else:
        print("  ❌ 没有找到训练进程")
    print()
    
    # 检查模型文件
    print("🧠 模型文件状态:")
    models_dir = "./models"
    if os.path.exists(models_dir):
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.zip')]
        if model_files:
            # 按修改时间排序
            model_files.sort(key=lambda x: os.path.getmtime(os.path.join(models_dir, x)), reverse=True)
            
            print(f"  最新模型文件:")
            for model in model_files[:3]:  # 显示最新的3个
                model_path = os.path.join(models_dir, model)
                mod_time = os.path.getmtime(model_path)
                size = os.path.getsize(model_path) / 1024  # KB
                print(f"    {model} ({size:.1f}KB, {datetime.fromtimestamp(mod_time).strftime('%H:%M:%S')})")
        else:
            print("  没有找到模型文件")
    else:
        print("  模型目录不存在")
    print()
    
    # 检查日志目录
    print("📝 训练日志状态:")
    logs_dir = "./logs"
    if os.path.exists(logs_dir):
        ppo_dirs = [d for d in os.listdir(logs_dir) if d.startswith('PPO_')]
        if ppo_dirs:
            # 按修改时间排序
            ppo_dirs.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
            print(f"  最新训练目录: {ppo_dirs[0]}")
            
            # 检查最新目录的日志文件
            latest_path = os.path.join(logs_dir, ppo_dirs[0])
            log_files = [f for f in os.listdir(latest_path) if f.endswith('.tfevents')]
            if log_files:
                latest_log = max(log_files, key=lambda x: os.path.getmtime(os.path.join(latest_path, x)))
                log_time = os.path.getmtime(os.path.join(latest_path, latest_log))
                print(f"  最新日志文件: {latest_log}")
                print(f"  更新时间: {datetime.fromtimestamp(log_time).strftime('%H:%M:%S')}")
        else:
            print("  没有找到训练日志")
    else:
        print("  日志目录不存在")
    print()
    
    # 系统资源
    print("💻 系统资源:")
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    print(f"  CPU使用率: {cpu_percent:.1f}%")
    print(f"  内存使用率: {memory.percent:.1f}%")
    print(f"  可用内存: {memory.available / (1024**3):.1f} GB")

if __name__ == "__main__":
    check_training()
