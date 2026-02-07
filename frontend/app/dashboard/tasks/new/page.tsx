"use client";

import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { useAuth } from "@/lib/auth/auth-context";
import { TaskForm } from "@/components/tasks/TaskForm";

export default function NewTaskPage() {
  const { user } = useAuth();

  if (!user) {
    return null; // Layout will handle redirect
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

      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create New Task</h1>
        <p className="mt-2 text-sm text-gray-600">
          Add a new task to your todo list
        </p>
      </div>

      {/* Task Form */}
      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <TaskForm userId={user.id} />
      </div>
    </div>
  );
}
