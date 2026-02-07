"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";
import { Task, TaskStatus } from "@/lib/types/task";
import { getTasks } from "@/lib/api/tasks";
import { configureAuthHeader, getAuthToken } from "@/lib/api/client";
import { TaskCard } from "./TaskCard";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { clsx } from "clsx";

interface TaskListProps {
  userId: string;
}

export function TaskList({ userId }: TaskListProps) {
  const router = useRouter();
  const [tasks, setTasks] = React.useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = React.useState<Task[]>([]);
  const [statusFilter, setStatusFilter] = React.useState<TaskStatus>("all");
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // Fetch tasks on mount
  React.useEffect(() => {
    loadTasks();
  }, [userId]);

  // Filter tasks when status changes
  React.useEffect(() => {
    filterTasks();
  }, [tasks, statusFilter]);

  const loadTasks = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Configure auth header before making request
      const token = getAuthToken();
      if (token) {
        configureAuthHeader(token);
      }

      const fetchedTasks = await getTasks(userId);
      // Sort by newest first
      const sorted = [...fetchedTasks].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setTasks(sorted);
    } catch (err) {
      console.error("Failed to load tasks:", err);
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  const filterTasks = () => {
    switch (statusFilter) {
      case "completed":
        setFilteredTasks(tasks.filter((task) => task.completed));
        break;
      case "pending":
        setFilteredTasks(tasks.filter((task) => !task.completed));
        break;
      case "all":
      default:
        setFilteredTasks(tasks);
        break;
    }
  };

  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) => (task.id === updatedTask.id ? updatedTask : task))
    );
  };

  const handleTaskDelete = (taskId: number) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
  };

  const handleCreateTask = () => {
    router.push("/dashboard/tasks/new");
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Spinner size="lg" />
        <p className="mt-4 text-sm text-gray-500">Loading tasks...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6">
        <h3 className="text-lg font-medium text-red-900">Error Loading Tasks</h3>
        <p className="mt-2 text-sm text-red-700">{error}</p>
        <Button
          variant="secondary"
          size="sm"
          onClick={loadTasks}
          className="mt-4"
        >
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header with Create Button */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            My Tasks
          </h1>
          <p className="text-sm text-gray-500 mt-1">Manage and track your daily tasks</p>
        </div>
        <Button
          onClick={handleCreateTask}
          size="md"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all"
        >
          <Plus className="mr-2 h-5 w-5" />
          New Task
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 bg-white/80 backdrop-blur-sm rounded-xl p-2 shadow-sm border border-gray-200">
        {(["all", "pending", "completed"] as TaskStatus[]).map((status) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={clsx(
              "flex-1 px-6 py-3 text-sm font-semibold rounded-lg transition-all duration-200",
              statusFilter === status
                ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md"
                : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
            )}
          >
            <span>{status.charAt(0).toUpperCase() + status.slice(1)}</span>
            <span className={clsx(
              "ml-2 px-2 py-0.5 rounded-full text-xs font-bold",
              statusFilter === status
                ? "bg-white/20"
                : "bg-gray-200"
            )}>
              {status === "all"
                ? tasks.length
                : status === "completed"
                ? tasks.filter((t) => t.completed).length
                : tasks.filter((t) => !t.completed).length}
            </span>
          </button>
        ))}
      </div>

      {/* Task List or Empty State */}
      {filteredTasks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center bg-white/60 backdrop-blur-sm rounded-2xl border-2 border-dashed border-gray-300">
          <div className="rounded-full bg-gradient-to-r from-blue-100 to-purple-100 p-6">
            <Plus className="h-12 w-12 text-blue-600" />
          </div>
          <h3 className="mt-6 text-xl font-bold text-gray-900">
            {statusFilter === "all"
              ? "No tasks yet"
              : statusFilter === "completed"
              ? "No completed tasks"
              : "No pending tasks"}
          </h3>
          <p className="mt-2 text-sm text-gray-500 max-w-sm">
            {statusFilter === "all"
              ? "Get started by creating your first task and boost your productivity"
              : `No ${statusFilter} tasks to show`}
          </p>
          {statusFilter === "all" && (
            <Button
              onClick={handleCreateTask}
              size="md"
              className="mt-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all"
            >
              <Plus className="mr-2 h-5 w-5" />
              Create Your First Task
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              userId={userId}
              onUpdate={handleTaskUpdate}
              onDelete={handleTaskDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
