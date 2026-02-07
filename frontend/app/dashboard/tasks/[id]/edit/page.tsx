"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { useAuth } from "@/lib/auth/auth-context";
import { getTask } from "@/lib/api/tasks";
import { TaskForm } from "@/components/tasks/TaskForm";
import { Spinner } from "@/components/ui/spinner";
import type { Task } from "@/lib/types/task";

interface EditTaskPageProps {
  params: { id: string };
}

export default function EditTaskPage({ params }: EditTaskPageProps) {
  const { user } = useAuth();
  const [task, setTask] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    const loadTask = async () => {
      try {
        setIsLoading(true);
        const data = await getTask(user.id, parseInt(params.id));
        setTask(data);
      } catch (err: any) {
        setError(err.message || "Failed to load task");
      } finally {
        setIsLoading(false);
      }
    };

    loadTask();
  }, [user, params.id]);

  if (!user) {
    return null; // Layout will handle redirect
  }

  if (isLoading) {
    return (
      <div className="container mx-auto max-w-2xl px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="container mx-auto max-w-2xl px-4 py-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-700">{error || "Task not found"}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-2xl px-4 py-8">
      {/* Back Navigation */}
      <Link
        href={`/dashboard/tasks/${task.id}`}
        className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-6"
      >
        <ChevronLeft className="h-4 w-4 mr-1" />
        Back to Task
      </Link>

      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Edit Task</h1>
        <p className="mt-2 text-sm text-gray-600">
          Update the details of your task
        </p>
      </div>

      {/* Task Form */}
      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <TaskForm userId={user.id} task={task} />
      </div>
    </div>
  );
}
