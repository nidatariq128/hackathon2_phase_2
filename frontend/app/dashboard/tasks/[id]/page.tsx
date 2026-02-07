"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, Edit, Trash2 } from "lucide-react";
import { format } from "date-fns";
import { useAuth } from "@/lib/auth/auth-context";
import { getTask } from "@/lib/api/tasks";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { clsx } from "clsx";
import { DeleteTaskButton } from "./DeleteTaskButton";
import { ToggleCompleteButton } from "./ToggleCompleteButton";
import type { Task } from "@/lib/types/task";

interface TaskDetailPageProps {
  params: { id: string };
}

export default function TaskDetailPage({ params }: TaskDetailPageProps) {
  const router = useRouter();
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
        href="/dashboard/tasks"
        className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-6"
      >
        <ChevronLeft className="h-4 w-4 mr-1" />
        Back to Tasks
      </Link>

      {/* Task Detail Card */}
      <div className="rounded-lg border bg-white shadow-sm">
        {/* Header */}
        <div className="border-b px-6 py-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1
                className={clsx(
                  "text-2xl font-bold",
                  task.completed ? "text-gray-500 line-through" : "text-gray-900"
                )}
              >
                {task.title}
              </h1>
              <div className="mt-2 flex items-center space-x-3 text-sm text-gray-500">
                <span>
                  Created {format(new Date(task.created_at), "MMM d, yyyy")}
                </span>
                {task.updated_at !== task.created_at && (
                  <>
                    <span>•</span>
                    <span>
                      Updated {format(new Date(task.updated_at), "MMM d, yyyy")}
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Completion Badge */}
            <span
              className={clsx(
                "rounded-full px-3 py-1 text-xs font-medium",
                task.completed
                  ? "bg-green-100 text-green-700"
                  : "bg-yellow-100 text-yellow-700"
              )}
            >
              {task.completed ? "Completed" : "Pending"}
            </span>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-6">
          <div className="mb-6">
            <h2 className="text-sm font-medium text-gray-700 mb-2">
              Description
            </h2>
            {task.description ? (
              <p className="text-gray-900 whitespace-pre-wrap">
                {task.description}
              </p>
            ) : (
              <p className="text-gray-400 italic">No description provided</p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3 pt-4 border-t">
            <ToggleCompleteButton
              taskId={task.id}
              userId={user.id}
              initialCompleted={task.completed}
            />

            <Link href={`/dashboard/tasks/${task.id}/edit`}>
              <Button variant="secondary" size="sm">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            </Link>

            <DeleteTaskButton taskId={task.id} userId={user.id} />
          </div>
        </div>
      </div>
    </div>
  );
}
