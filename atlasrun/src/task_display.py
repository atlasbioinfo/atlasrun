#!/usr/bin/env python3
"""
Task display utilities for AtlasRun
"""
import time
from datetime import datetime
from tabulate import tabulate
from ..db import TaskStatus


def format_duration(start_time, end_time=None):
    """格式化持续时间"""
    if not start_time:
        return "-"
    
    if not end_time:
        end_time = time.time()
    
    duration = end_time - start_time
    if duration < 60:
        return f"{int(duration)}s"
    elif duration < 3600:
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes}m {seconds}s"
    else:
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_time(timestamp):
    """格式化时间戳"""
    if not timestamp:
        return "-"
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")


def get_status_icon(status):
    """获取状态图标"""
    status_icons = {
        TaskStatus.RUNNING: "▶",
        TaskStatus.PENDING: "⏳", 
        TaskStatus.COMPLETED: "✓",
        TaskStatus.FAILED: "✗"
    }
    return status_icons.get(status, "?")


def list_tasks(db):
    """显示任务列表"""
    # 获取所有任务
    all_tasks = db.get_all_tasks(limit=50)  # 限制显示最近50个任务
    
    if not all_tasks:
        print("No tasks found")
        return
    
    # 准备表格数据
    table_data = []
    headers = ["ID", "Status", "PID", "Submit Time", "Duration", "Command"]
    
    for task in all_tasks:
        # 计算运行时间
        if task.status == TaskStatus.RUNNING and task.start_time:
            duration = format_duration(task.start_time)
        elif task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and task.start_time and task.completed_at:
            duration = format_duration(task.start_time, task.completed_at)
        else:
            duration = "-"
        
        # 状态显示
        status_display = f"{get_status_icon(task.status)} {task.status.value}"
        
        # 添加行数据
        row = [
            task.id,
            status_display,
            task.pid or "-",
            format_time(task.created_at),
            duration,
            task.command[:50] + "..." if len(task.command) > 50 else task.command
        ]
        table_data.append(row)
    
    # 按ID排序
    table_data.sort(key=lambda x: x[0])
    
    # 使用tabulate打印表格
    print("\n" + tabulate(
        table_data,
        headers=headers,
        tablefmt="fancy_grid",
        colalign=("right", "left", "right", "right", "right", "left")
    ) + "\n")


def show_status(db):
    """显示队列状态"""
    pending_tasks = db.get_pending_tasks()
    running_tasks = db.get_running_tasks()
    
    print("=== AtlasRun Queue Status ===")
    print(f"Pending tasks: {len(pending_tasks)}")
    print(f"Running tasks: {len(running_tasks)}")
    
    if running_tasks:
        print("\nRunning tasks:")
        for task in running_tasks:
            print(f"  {task.id}: {task.command} (PID: {task.pid})")
    
    if pending_tasks:
        print("\nPending tasks:")
        for task in pending_tasks:
            print(f"  {task.id}: {task.command}")


def show_task_info(db, task_id):
    """显示任务详细信息"""
    task = db.get_task_by_id(task_id)
    
    if not task:
        print(f"Task {task_id} not found")
        return
    
    print(f"=== Task {task_id} Information ===")
    print(f"Command: {task.command}")
    print(f"Working Directory: {task.working_dir}")
    print(f"Status: {task.status.value}")
    print(f"PID: {task.pid or 'N/A'}")
    print(f"Created: {format_time(task.created_at)}")
    
    if task.started_at:
        print(f"Started: {format_time(task.started_at)}")
    
    if task.completed_at:
        print(f"Completed: {format_time(task.completed_at)}")
        print(f"Exit Code: {task.exit_code}")
