// T050: useTasks hook for task CRUD operations

'use client';

import { useState, useCallback, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Task, TaskCreate, TaskUpdate } from '@/lib/types';

export function useTasks(userId: string | null) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.getTasks(userId);
      setTasks(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const createTask = useCallback(
    async (taskData: TaskCreate) => {
      if (!userId) return;

      setError(null);

      try {
        const newTask = await api.createTask(userId, taskData);
        setTasks((prev) => [newTask, ...prev]);
        return newTask;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to create task');
        throw err;
      }
    },
    [userId]
  );

  const updateTask = useCallback(
    async (taskId: string, updates: TaskUpdate) => {
      if (!userId) return;

      setError(null);

      try {
        const updatedTask = await api.updateTask(userId, taskId, updates);
        setTasks((prev) =>
          prev.map((task) => (task.id === taskId ? updatedTask : task))
        );
        return updatedTask;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update task');
        throw err;
      }
    },
    [userId]
  );

  const deleteTask = useCallback(
    async (taskId: string) => {
      if (!userId) return;

      setError(null);

      try {
        await api.deleteTask(userId, taskId);
        setTasks((prev) => prev.filter((task) => task.id !== taskId));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete task');
        throw err;
      }
    },
    [userId]
  );

  const toggleTaskComplete = useCallback(
    async (taskId: string): Promise<void> => {
      if (!userId) return;

      const task = tasks.find((t) => t.id === taskId);
      if (!task) return;

      await updateTask(taskId, { completed: !task.completed });
    },
    [userId, tasks, updateTask]
  );

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return {
    tasks,
    isLoading,
    error,
    fetchTasks,
    refreshTasks: fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskComplete,
  };
}
