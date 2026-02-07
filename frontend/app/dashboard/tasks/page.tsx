"use client";

import { useAuth } from "@/lib/auth/auth-context";
import { TaskList } from "@/components/tasks/TaskList";

export default function TasksPage() {
  const { user } = useAuth();

  if (!user) {
    return null; // Layout will handle redirect
  }

  return (
    <div className="container mx-auto max-w-4xl px-4 py-8">
      <TaskList userId={user.id} />
    </div>
  );
}
