#!/usr/bin/env python3
"""
LightPlane AI 项目清理脚本
用于删除项目中未使用的测试、调试和旧版本文件
"""

import os
import shutil
import sys
from pathlib import Path

class ProjectCleaner:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.files_to_delete = []
        self.dirs_to_delete = []
        
    def analyze_project(self):
        """分析项目结构，识别可删除的文件"""
        print("🔍 分析项目结构...")
        
        # 测试和调试文件
        test_patterns = [
            "test_*.py",
            "debug_*.py", 
            "demo_*.py"
        ]
        
        # 旧版本文件
        old_files = [
            "complex_image_matting.py",
            "complex_image_matting_fixed.py",
            "advanced_ai_matting.py",
            "ai_generated_image_matting.py"
        ]
        
        # 未使用的监控文件
        unused_files = [
            "check_training_status.py",
            "monitor_training.py",
            "rl_ai_controller.py"
        ]
        
        # 训练相关文件（可选）
        training_files = [
            "train_ai.py",
            "check_training.py"
        ]
        
        # 数据集和输出目录
        data_dirs = [
            "airplane_dataset",
            "lora_output", 
            "lora_output_simple",
            "processed_images"
        ]
        
        # 查找匹配的文件
        for pattern in test_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    self.files_to_delete.append(file_path)
        
        # 查找旧版本文件
        for file_name in old_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.files_to_delete.append(file_path)
        
        # 查找未使用的文件
        for file_name in unused_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.files_to_delete.append(file_path)
        
        # 查找训练相关文件
        for file_name in training_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.files_to_delete.append(file_path)
        
        # 查找数据集目录
        for dir_name in data_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.dirs_to_delete.append(dir_path)
        
        print(f"📊 分析完成！")
        print(f"   发现 {len(self.files_to_delete)} 个可删除的文件")
        print(f"   发现 {len(self.dirs_to_delete)} 个可删除的目录")
    
    def show_files_to_delete(self):
        """显示将要删除的文件列表"""
        if not self.files_to_delete and not self.dirs_to_delete:
            print("✅ 没有需要删除的文件")
            return
        
        print("\n🗑️ 将要删除的文件:")
        for file_path in self.files_to_delete:
            print(f"   📄 {file_path}")
        
        print("\n🗑️ 将要删除的目录:")
        for dir_path in self.dirs_to_delete:
            print(f"   📁 {dir_path}")
    
    def confirm_deletion(self):
        """确认删除操作"""
        if not self.files_to_delete and not self.dirs_to_delete:
            return True
        
        print(f"\n⚠️ 警告：这将删除 {len(self.files_to_delete)} 个文件和 {len(self.dirs_to_delete)} 个目录")
        print("请确认您要删除这些文件！")
        
        response = input("输入 'yes' 确认删除，或按回车取消: ").strip().lower()
        return response == 'yes'
    
    def backup_files(self, backup_dir="backup_before_cleanup"):
        """备份要删除的文件"""
        if not self.files_to_delete and not self.dirs_to_delete:
            return
        
        backup_path = self.project_root / backup_dir
        backup_path.mkdir(exist_ok=True)
        
        print(f"\n💾 备份文件到 {backup_path}...")
        
        # 备份文件
        for file_path in self.files_to_delete:
            if file_path.exists():
                backup_file = backup_path / file_path.name
                shutil.copy2(file_path, backup_file)
                print(f"   备份: {file_path.name}")
        
        # 备份目录
        for dir_path in self.dirs_to_delete:
            if dir_path.exists():
                backup_dir_path = backup_path / dir_path.name
                shutil.copytree(dir_path, backup_dir_path)
                print(f"   备份: {dir_path.name}/")
        
        print("✅ 备份完成！")
    
    def delete_files(self):
        """执行删除操作"""
        if not self.files_to_delete and not self.dirs_to_delete:
            print("✅ 没有文件需要删除")
            return
        
        print(f"\n🗑️ 开始删除文件...")
        
        # 删除文件
        for file_path in self.files_to_delete:
            try:
                if file_path.exists():
                    file_path.unlink()
                    print(f"   删除文件: {file_path.name}")
            except Exception as e:
                print(f"   ❌ 删除失败 {file_path.name}: {e}")
        
        # 删除目录
        for dir_path in self.dirs_to_delete:
            try:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    print(f"   删除目录: {dir_path.name}/")
            except Exception as e:
                print(f"   ❌ 删除失败 {dir_path.name}/: {e}")
        
        print("✅ 删除操作完成！")
    
    def cleanup_empty_dirs(self):
        """清理空目录"""
        print("\n🧹 清理空目录...")
        
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if dir_path.exists() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        print(f"   删除空目录: {dir_path}")
                except Exception as e:
                    pass  # 忽略无法删除的目录
        
        print("✅ 空目录清理完成！")
    
    def show_remaining_structure(self):
        """显示清理后的项目结构"""
        print("\n📁 清理后的项目结构:")
        
        def print_tree(path, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
            
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                next_prefix = "    " if is_last else "│   "
                
                if item.is_file():
                    print(f"{prefix}{current_prefix}{item.name}")
                elif item.is_dir():
                    print(f"{prefix}{current_prefix}{item.name}/")
                    print_tree(item, prefix + next_prefix, max_depth, current_depth + 1)
        
        print_tree(self.project_root)
    
    def run_cleanup(self, backup=True, confirm=True):
        """运行完整的清理流程"""
        print("🚀 LightPlane AI 项目清理工具")
        print("=" * 50)
        
        # 分析项目
        self.analyze_project()
        
        # 显示要删除的文件
        self.show_files_to_delete()
        
        if not self.files_to_delete and not self.dirs_to_delete:
            print("\n🎉 项目已经很干净了！")
            return
        
        # 确认删除
        if confirm and not self.confirm_deletion():
            print("❌ 操作已取消")
            return
        
        # 备份文件
        if backup:
            self.backup_files()
        
        # 删除文件
        self.delete_files()
        
        # 清理空目录
        self.cleanup_empty_dirs()
        
        # 显示清理后的结构
        self.show_remaining_structure()
        
        print("\n🎉 项目清理完成！")
        print("💡 提示：如果出现问题，可以从 backup_before_cleanup 目录恢复文件")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LightPlane AI 项目清理工具")
    parser.add_argument("--no-backup", action="store_true", help="不备份文件直接删除")
    parser.add_argument("--no-confirm", action="store_true", help="不确认直接删除")
    parser.add_argument("--project-root", default=".", help="项目根目录路径")
    
    args = parser.parse_args()
    
    cleaner = ProjectCleaner(args.project_root)
    
    try:
        cleaner.run_cleanup(
            backup=not args.no_backup,
            confirm=not args.no_confirm
        )
    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 清理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
