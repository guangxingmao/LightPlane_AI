#!/usr/bin/env python3
"""
AI训练监控脚本
实时监控训练进度和状态
"""

import os
import time
import psutil
from datetime import datetime

def monitor_training():
    """监控AI训练状态"""
    print("🚀 AI训练监控器")
    print("=" * 50)
    
    while True:
        # 清屏
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🚀 AI训练监控器")
        print("=" * 50)
        print(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
            print("✅ 训练进程状态:")
            for proc in training_processes:
                try:
                    cpu_percent = proc.cpu_percent()
                    memory_percent = proc.memory_percent()
                    memory_info = proc.memory_info()
                    print(f"  PID: {proc.pid}")
                    print(f"  CPU使用率: {cpu_percent:.1f}%")
                    print(f"  内存使用率: {memory_percent:.1f}%")
                    print(f"  内存使用: {memory_info.rss / (1024**3):.2f} GB")
                    print()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    print(f"  ❌ 无法获取进程信息 (PID: {proc.pid})")
        else:
            print("❌ 没有找到训练进程")
            print()
        
        # 检查训练日志
        log_file = "training_continue.log"
        if os.path.exists(log_file):
            print("📝 训练日志 (最新内容):")
            print("-" * 30)
            
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        # 显示最后10行
                        for line in lines[-10:]:
                            line = line.strip()
                            if line:
                                print(f"  {line}")
                    else:
                        print("  日志文件为空")
            except Exception as e:
                print(f"  ❌ 读取日志失败: {e}")
        else:
            print("❌ 训练日志文件不存在")
        
        print()
        print("💡 按 Ctrl+C 退出监控")
        print("🔄 每5秒自动刷新...")
        
        # 等待5秒
        time.sleep(5)

if __name__ == "__main__":
    try:
        monitor_training()
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
