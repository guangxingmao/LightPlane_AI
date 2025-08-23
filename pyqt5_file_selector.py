#!/usr/bin/env python3
"""
独立的 PyQt5 文件选择器
用于避免与 pygame 的冲突
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import Qt

def select_file(image_type):
    """选择文件并返回路径"""
    try:
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
        
        # 返回选择的文件路径
        if file_path and os.path.exists(file_path):
            print(f"SELECTED_FILE:{file_path}")
            return file_path
        else:
            print("NO_FILE_SELECTED")
            return None
            
    except Exception as e:
        print(f"ERROR:{str(e)}")
        return None

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("USAGE: python3 pyqt5_file_selector.py <image_type>")
        sys.exit(1)
    
    image_type = sys.argv[1]
    result = select_file(image_type)
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
