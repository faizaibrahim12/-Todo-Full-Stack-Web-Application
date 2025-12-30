// T053: Individual task item component with toggle and delete

'use client';

import { useState } from 'react';
import type { Task } from '@/lib/types';

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: string) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
}

export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleToggle = async () => {
    setIsUpdating(true);
    try {
      await onToggle(task.id);
    } catch (error) {
      console.error('Failed to toggle task:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } catch (error) {
      console.error('Failed to delete task:', error);
      setIsDeleting(false);
    }
  };

  return (
    <div
      className={`flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow ${
        isDeleting ? 'opacity-50' : ''
      }`}
    >
      <input
        type="checkbox"
        checked={task.completed}
        onChange={handleToggle}
        disabled={isUpdating || isDeleting}
        className="h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-2 focus:ring-blue-500 cursor-pointer"
      />

      <span
        className={`flex-1 ${
          task.completed ? 'line-through text-gray-500' : 'text-gray-900'
        }`}
      >
        {task.title}
      </span>

      <button
        onClick={handleDelete}
        disabled={isUpdating || isDeleting}
        className="text-red-600 hover:text-red-800 disabled:opacity-50 transition-colors"
        aria-label="Delete task"
      >
        <svg
          className="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  );
}
