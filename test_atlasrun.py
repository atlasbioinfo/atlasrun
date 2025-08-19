#!/usr/bin/env python3
"""
测试AtlasRun的基本功能
"""
import os
import time
import subprocess
from pathlib import Path

def test_basic_functionality():
    """测试基本功能"""
    print("=== Testing AtlasRun Basic Functionality ===")
    
    # 测试添加任务
    print("\n1. Testing task addition...")
    result = subprocess.run(['python', '-m', 'atlasrun.cli', 'echo', 'hello world'], 
                          capture_output=True, text=True)
    print(f"Output: {result.stdout}")
    print(f"Error: {result.stdout}")
    
    # 测试状态查看
    print("\n2. Testing status...")
    result = subprocess.run(['python', '-m', 'atlasrun.cli', '--status'], 
                          capture_output=True, text=True)
    print(f"Status: {result.stdout}")
    
    # 测试任务列表
    print("\n3. Testing task list...")
    result = subprocess.run(['python', '-m', 'atlasrun.cli', '--list'], 
                          capture_output=True, text=True)
    print(f"List: {result.stdout}")

def test_queue_behavior():
    """测试队列行为"""
    print("\n=== Testing Queue Behavior ===")
    
    # 添加一个长时间运行的任务
    print("\n1. Adding a long-running task...")
    subprocess.Popen(['python', '-m', 'atlasrun.cli', 'sleep', '5'], 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(1)  # 等待任务启动
    
    # 添加另一个任务
    print("\n2. Adding another task...")
    result = subprocess.run(['python', '-m', 'atlasrun.cli', 'echo', 'second task'], 
                          capture_output=True, text=True)
    print(f"Second task result: {result.stdout}")
    
    # 查看状态
    print("\n3. Checking status...")
    result = subprocess.run(['python', '-m', 'atlasrun.cli', '--status'], 
                          capture_output=True, text=True)
    print(f"Status: {result.stdout}")
    
    # 等待任务完成
    print("\n4. Waiting for tasks to complete...")
    time.sleep(6)
    
    # 再次查看状态
    print("\n5. Final status...")
    result = subprocess.run(['python', '-m', 'atlasrun.cli', '--status'], 
                          capture_output=True, text=True)
    print(f"Final status: {result.stdout}")

if __name__ == '__main__':
    test_basic_functionality()
    test_queue_behavior()
