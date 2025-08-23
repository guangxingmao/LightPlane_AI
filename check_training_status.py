#!/usr/bin/env python3
"""
快速检查AI训练状态
"""

import os
import psutil
from datetime import datetime

def check_training_status():
    """检查训练状态"""
    print("🚀 AI训练状态检查")
    print("=" * 40)
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查训练进程
    training_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['name'] == 'Python' and any('train_ai.py' in cmd for cmd in proc.info['cmdline'] if cmd):
                training_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if training_processes:
        print("✅ 训练进程运行中:")
        for proc in training_processes:
            try:
                cpu_percent = proc.cpu_percent()
                memory_percent = proc.memory_percent()
                print(f"  PID: {proc.pid}")
                print(f"  CPU使用率: {cpu_percent:.1f}%")
                print(f"  内存使用率: {memory_percent:.1f}%")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"  PID: {proc.pid} (无法获取详细信息)")
    else:
        print("❌ 没有找到训练进程")
    
    print()
    
    # 检查训练日志
    log_file = "training_continue.log"
    if os.path.exists(log_file):
        print("📝 训练日志状态:")
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    # 显示最后几行
                    print("  最新日志内容:")
                    for line in lines[-5:]:
                        line = line.strip()
                        if line:
                            print(f"    {line}")
                else:
                    print("  日志文件为空")
        except Exception as e:
            print(f"  ❌ 读取日志失败: {e}")
    else:
        print("❌ 训练日志文件不存在")
    
    print()
    
    # 检查模型文件
    models_dir = "./models"
    if os.path.exists(models_dir):
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.zip')]
        if model_files:
            # 按修改时间排序
            model_files.sort(key=lambda x: os.path.getmtime(os.path.join(models_dir, x)), reverse=True)
            print("📁 最新模型文件:")
            for model in model_files[:3]:  # 显示最新的3个
                model_path = os.path.join(models_dir, model)
                mod_time = os.path.getmtime(model_path)
                size = os.path.getsize(model_path) / 1024  # KB
                print(f"  {model} ({size:.1f}KB, {datetime.fromtimestamp(mod_time).strftime('%H:%M:%S')})")
        else:
            print("❌ 没有找到模型文件")
    else:
        print("❌ 模型目录不存在")

if __name__ == "__main__":
    check_training_status()
