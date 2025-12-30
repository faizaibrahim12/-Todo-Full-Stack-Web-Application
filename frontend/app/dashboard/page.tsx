// T055: Dashboard page with task management and logout

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { useTasks } from '@/hooks/useTasks';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { AddTaskForm } from '@/components/tasks/AddTaskForm';
import { TaskList } from '@/components/tasks/TaskList';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const {
    tasks,
    isLoading: tasksLoading,
    error,
    createTask,
    toggleTaskComplete,
    deleteTask,
  } = useTasks(user?.id || null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const handleAddTask = async (title: string) => {
    await createTask({ title });
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
              <p className="text-sm text-gray-600 mt-1">{user?.email}</p>
            </div>
            <Button variant="secondary" onClick={handleLogout}>
              Log Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <Card>
          <AddTaskForm onAddTask={handleAddTask} />

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <TaskList
            tasks={tasks}
            isLoading={tasksLoading}
            onToggle={toggleTaskComplete}
            onDelete={deleteTask}
          />
        </Card>

        {/* Stats */}
        <div className="mt-6 text-center text-sm text-gray-500">
          {tasks.length > 0 && (
            <p>
              {tasks.filter((t) => t.completed).length} of {tasks.length} tasks
              completed
            </p>
          )}
        </div>
      </main>
    </div>
  );
}
