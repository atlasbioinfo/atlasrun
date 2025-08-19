#!/usr/bin/env python3
"""
Script templates for AtlasRun
"""
import time
from pathlib import Path


def create_task_script(task_id: int, command: str, working_dir: str, 
                      temp_scripts_dir: Path, log_dir: Path, 
                      wait_for_pid: int = None) -> str:
    """创建任务脚本内容"""
    
    # 构建等待逻辑
    wait_logic = ""
    if wait_for_pid:
        wait_logic = f"""
# 等待前一个任务完成
echo "Waiting for previous task (PID: {wait_for_pid}) to complete..." >&2
while kill -0 {wait_for_pid} 2>/dev/null; do
    sleep 1
done
echo "Previous task completed, starting this task..." >&2
"""
    
    stdout_log = log_dir / f"task_{task_id}.out"
    stderr_log = log_dir / f"task_{task_id}.err"
    
    script_content = f"""#!/bin/bash
# AtlasRun temporary script for task {task_id}
# Command: {command}
# Created at: {time.strftime('%Y-%m-%d %H:%M:%S')}

set -e

# 记录开始时间
echo "Task {task_id} started at $(date)" >&2

# 首先标记任务为pending状态
arun --mark-pending {task_id}

{wait_logic}
# 等待完成后，标记任务为running状态
arun --mark-running {task_id}

# 切换到工作目录
cd "{working_dir}"

# 执行命令并重定向输出
{command} > {stdout_log} 2> {stderr_log}

# 记录结束时间和退出码
exit_code=$?
echo "Task {task_id} completed at $(date) with exit code $exit_code" >&2

# 标记任务为completed状态
arun --mark-complete {task_id} $exit_code

# 脚本结束时再次调用arun -u来检查其他任务状态
exit $exit_code
"""
    
    return script_content

