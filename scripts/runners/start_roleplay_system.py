#!/usr/bin/env python3
"""
启动和管理roleplay访谈系统
"""

import sys
import os
import subprocess
import time
import signal
import json

def check_system_status():
    """检查系统状态"""
    print("=== 检查系统状态 ===")
    
    # 检查是否有正在运行的进程
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'full_concurrent_roleplay.py' in result.stdout:
            print("⚠️  发现正在运行的roleplay进程")
            return True
        else:
            print("✅ 没有正在运行的roleplay进程")
            return False
    except:
        print("❌ 无法检查进程状态")
        return False

def show_progress():
    """显示当前进度"""
    print("\\n=== 当前进度 ===")
    
    checkpoint_file = 'data/llm_responses_roleplay/roleplay_checkpoint.json'
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            
            print(f"检查点时间: {checkpoint.get('timestamp', 'N/A')}")
            print(f"已完成任务: {checkpoint.get('total_tasks', 0)}")
            print(f"结果数量: {checkpoint.get('total_results', 0)}")
            
            # 计算进度
            total_possible = 7 * 109  # 7个模型 * 109个国家
            completed = checkpoint.get('total_tasks', 0)
            progress = completed / total_possible * 100 if total_possible > 0 else 0
            
            print(f"总体进度: {completed}/{total_possible} ({progress:.1f}%)")
            
        except Exception as e:
            print(f"读取检查点失败: {e}")
    else:
        print("没有找到检查点文件")

def start_system():
    """启动系统"""
    print("\\n=== 启动Roleplay访谈系统 ===")
    
    if check_system_status():
        print("系统已在运行，请先停止现有进程")
        return
    
    print("启动参数:")
    print("  - 最大并发数: 8")
    print("  - 检查点间隔: 10个任务")
    print("  - 支持断点续传")
    print("  - 按Ctrl+C可随时停止")
    print()
    
    try:
        # 启动系统
        process = subprocess.Popen([
            sys.executable, 'full_concurrent_roleplay.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        print(f"系统已启动，PID: {process.pid}")
        print("正在运行... (按Ctrl+C停止)")
        
        # 实时显示输出
        try:
            for line in process.stdout:
                print(line.rstrip())
        except KeyboardInterrupt:
            print("\\n收到停止信号，正在终止进程...")
            process.terminate()
            process.wait()
            print("进程已终止")
    
    except Exception as e:
        print(f"启动失败: {e}")

def stop_system():
    """停止系统"""
    print("\\n=== 停止Roleplay访谈系统 ===")
    
    try:
        # 查找并终止进程
        result = subprocess.run(['pkill', '-f', 'full_concurrent_roleplay.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 系统已停止")
        else:
            print("❌ 没有找到运行中的进程")
    
    except Exception as e:
        print(f"停止失败: {e}")

def analyze_results():
    """分析结果"""
    print("\\n=== 分析结果 ===")
    
    try:
        subprocess.run([sys.executable, 'analyze_and_optimize.py'])
    except Exception as e:
        print(f"分析失败: {e}")

def show_menu():
    """显示菜单"""
    print("\\n=== Roleplay访谈系统管理 ===")
    print("1. 启动系统")
    print("2. 停止系统")
    print("3. 查看进度")
    print("4. 分析结果")
    print("5. 退出")
    print()

def main():
    """主函数"""
    while True:
        show_menu()
        
        try:
            choice = input("请选择操作 (1-5): ").strip()
            
            if choice == '1':
                start_system()
            elif choice == '2':
                stop_system()
            elif choice == '3':
                show_progress()
            elif choice == '4':
                analyze_results()
            elif choice == '5':
                print("退出")
                break
            else:
                print("无效选择，请重新输入")
        
        except KeyboardInterrupt:
            print("\\n\\n退出")
            break
        except EOFError:
            print("\\n\\n检测到非交互式环境，自动退出")
            break
        except Exception as e:
            print(f"操作失败: {e}")

if __name__ == "__main__":
    main()
