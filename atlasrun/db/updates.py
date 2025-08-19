#!/usr/bin/env python3
"""
Task update operations for AtlasRun
"""
import time
from .models import TaskStatus
from .connection import get_connection


def add_task(db_path: str, command: str, working_dir: str) -> int:
    """添加新任务到队列"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (command, working_dir, status, created_at)
            VALUES (?, ?, ?, ?)
        """, (command, working_dir, TaskStatus.PENDING.value, time.time()))
        conn.commit()
        return cursor.lastrowid


def start_task(db_path: str, task_id: int, pid: int):
    """标记任务开始运行"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, pid = ?, started_at = ?
            WHERE id = ?
        """, (TaskStatus.RUNNING.value, pid, time.time(), task_id))
        conn.commit()


def complete_task(db_path: str, task_id: int, exit_code: int):
    """标记任务完成"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, completed_at = ?, exit_code = ?
            WHERE id = ?
        """, (TaskStatus.COMPLETED.value, time.time(), exit_code, task_id))
        conn.commit()


def fail_task(db_path: str, task_id: int, exit_code: int):
    """标记任务失败"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, completed_at = ?, exit_code = ?
            WHERE id = ?
        """, (TaskStatus.FAILED.value, time.time(), exit_code, task_id))
        conn.commit()


def update_pid(db_path: str, task_id: int, pid: int):
    """只更新任务的PID，不改变状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET pid = ?
            WHERE id = ?
        """, (pid, task_id))
        conn.commit()


def mark_task_pending(db_path: str, task_id: int):
    """强制标记任务为pending状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, pid = NULL, started_at = NULL, completed_at = NULL, exit_code = NULL
            WHERE id = ?
        """, (TaskStatus.PENDING.value, task_id))
        conn.commit()


def mark_task_complete(db_path: str, task_id: int, exit_code: int = 0):
    """强制标记任务为completed状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, completed_at = ?, exit_code = ?
            WHERE id = ?
        """, (TaskStatus.COMPLETED.value, time.time(), exit_code, task_id))
        conn.commit()


def mark_task_pending_by_pid(db_path: str, pid: int):
    """通过PID强制标记任务为pending状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, pid = NULL, started_at = NULL, completed_at = NULL, exit_code = NULL
            WHERE pid = ?
        """, (TaskStatus.PENDING.value, pid))
        conn.commit()


def mark_task_complete_by_pid(db_path: str, pid: int, exit_code: int = 0):
    """通过PID强制标记任务为completed状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, completed_at = ?, exit_code = ?
            WHERE pid = ?
        """, (TaskStatus.COMPLETED.value, time.time(), exit_code, pid))
        conn.commit()


def cleanup_completed_tasks(db_path: str, days: int = 7):
    """清理已完成的任务（保留指定天数）"""
    cutoff_time = time.time() - (days * 24 * 3600)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM tasks 
            WHERE status IN (?, ?) AND completed_at < ?
        """, (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, cutoff_time))
        conn.commit()
