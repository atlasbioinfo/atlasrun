#!/usr/bin/env python3
import argparse
import os
import time
from pathlib import Path
from .db import Database, TaskStatus
from .executor import TaskExecutor
from .src.task_display import show_status, show_task_info, list_tasks


def main():
    """AtlasRun - A simple command queue management tool"""
    parser = argparse.ArgumentParser(
        description="AtlasRun - A simple command queue management tool",
        usage="arun [options] [command...]",
        add_help=False
    )
    
    parser.add_argument('-s', '--status', action='store_true', 
                       help='Show current queue status')
    parser.add_argument('-l', action='store_true', 
                       help='List all tasks')
    parser.add_argument('-i', '--info', type=int, metavar='TASK_ID',
                       help='Show detailed information about a specific task')
    parser.add_argument('-c', '--cleanup', type=int, metavar='DAYS',
                       help='Clean up completed tasks older than specified days')
    parser.add_argument('-u', '--update', action='store_true',
                       help='Update task statuses (check if PIDs are still running)')
    parser.add_argument('--mark-running', type=int, metavar='PID',
                       help='Mark a task with specific PID as running (internal use)')
    parser.add_argument('--mark-pending', type=int, metavar='PID',
                       help='Force mark a task with specific PID as pending')
    parser.add_argument('--mark-complete', type=int, metavar='PID',
                       help='Force mark a task with specific PID as completed')
    parser.add_argument('-d', '--dir', metavar='DIRECTORY',
                       help='Working directory for the command')
    parser.add_argument('-h', '--help', action='store_true',
                       help='Show this help message and exit')
    
    # 解析已知参数，保留未知参数
    args, unknown = parser.parse_known_args()
    
    # 显示帮助信息
    if args.help:
        parser.print_help()
        print("\nExamples:")
        print("  arun sleep 3                    # Add command to queue")
        print("  arun -s                         # Show queue status")
        print("  arun -l                         # List all tasks")
        print("  arun -i 1                       # Show task details")
        print("  arun -c 7                       # Clean up old tasks")
        print("  arun -u                         # Update task statuses")
        print("  arun -d /tmp echo hello         # Run command in specific directory")
        return
    
    db = Database()
    
    # 处理特殊命令
    if args.status:
        show_status(db)
        return
    
    if args.l:
        list_tasks(db)
        return
    
    if args.info:
        show_task_info(db, args.info)
        return
    
    if args.cleanup:
        cleanup_tasks(db, args.cleanup)
        return
    
    if args.update:
        update_task_statuses(db)
        return
    
    if args.mark_running:
        db.mark_task_running_by_pid(args.mark_running)
        return
    
    if args.mark_pending:
        db.mark_task_pending_by_pid(args.mark_pending)
        return
    
    if args.mark_complete:
        db.mark_task_complete_by_pid(args.mark_complete)
        return
    
    # 获取命令参数（所有没有-开头的参数）
    command_parts = []
    for arg in unknown:
        if not arg.startswith('-'):
            command_parts.append(arg)
        else:
            print(f"Warning: Ignoring unknown option {arg}")
    
    if not command_parts:
        print("Error: No command specified")
        print("Use 'arun -h' for help")
        return
    
    # 组合完整命令
    full_command = ' '.join(command_parts)
    
    # 确定工作目录
    working_dir = args.dir
    if working_dir:
        working_dir = os.path.abspath(working_dir)
        if not os.path.exists(working_dir):
            print(f"Error: Directory {working_dir} does not exist")
            return
    else:
        working_dir = os.getcwd()
    
    # 初始化执行器并运行任务
    executor = TaskExecutor(db)
    
    try:
        # 运行任务
        task_id = executor.run_single_task(full_command, working_dir)
        print(f"Task {task_id} completed")
    except Exception as e:
        print(f"Error: {e}")


def cleanup_tasks(db, days):
    """清理任务"""
    db.cleanup_completed_tasks(days)
    print(f"Cleaned up tasks older than {days} days")


def update_task_statuses(db):
    """更新任务状态"""
    executor = TaskExecutor(db)
    executor.update_task_statuses()


if __name__ == '__main__':
    main()
