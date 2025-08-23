#!/usr/bin/env python3
"""
安全的文件选择器 - 使用subprocess避免线程冲突
"""

import subprocess
import sys
import os

def select_file(image_type):
    """使用subprocess调用文件选择器，避免线程冲突"""
    try:
        # 获取当前脚本的绝对路径
        script_path = os.path.abspath(__file__)
        
        # 使用subprocess调用文件选择器
        result = subprocess.run(
            [sys.executable, script_path, image_type],
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # 解析输出
            output = result.stdout.strip()
            if output.startswith("SELECTED_FILE:"):
                file_path = output.replace("SELECTED_FILE:", "").strip()
                if os.path.exists(file_path):
                    print(f"✅ 文件选择成功: {file_path}")
                    return file_path
                else:
                    print(f"❌ 选择的文件不存在: {file_path}")
                    return None
            else:
                print(f"ℹ️ 用户取消了文件选择")
                return None
        else:
            print(f"⚠️ 文件选择器返回错误: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("⏰ 文件选择超时")
        return None
    except Exception as e:
        print(f"❌ 文件选择器调用失败: {e}")
        return None

def main():
    """主函数 - 独立运行时的文件选择逻辑"""
    if len(sys.argv) != 2:
        print("USAGE: python3 pyqt5_file_selector.py <image_type>")
        sys.exit(1)
    
    image_type = sys.argv[1]
    
    try:
        # 导入PyQt5组件
        from PyQt5.QtWidgets import QApplication, QFileDialog
        from PyQt5.QtCore import Qt
        
        # 创建应用程序实例
        app = QApplication([])
        
        # 设置应用程序属性
        app.setAttribute(Qt.AA_DontShowIconsInMenus, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # 创建文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            f"Select {image_type.replace('_', ' ').title()} Image",
            os.path.expanduser('~'),
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;BMP Files (*.bmp);;GIF Files (*.gif);;All Files (*.*)"
        )
        
        # 输出选择的文件路径
        if file_path and os.path.exists(file_path):
            print(f"SELECTED_FILE:{file_path}")
            sys.exit(0)
        else:
            print("NO_FILE_SELECTED")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR:{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
