"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Trash2 } from "lucide-react";
import { format } from "date-fns";
import { Task } from "@/lib/types/task";
import { toggleTaskComplete, deleteTask } from "@/lib/api/tasks";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { clsx } from "clsx";

interface TaskCardProps {
  task: Task;
  userId: string;
  onUpdate: (task: Task) => void;
  onDelete: (taskId: number) => void;
}

export function TaskCard({ task, userId, onUpdate, onDelete }: TaskCardProps) {
  const router = useRouter();
  const [isToggling, setIsToggling] = React.useState(false);
  const [isDeleting, setIsDeleting] = React.useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);

  // Optimistic update for completion toggle
  const handleToggleComplete = async (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();

    const previousCompleted = task.completed;
    const optimisticTask = { ...task, completed: !previousCompleted };

    // Immediately update UI
    onUpdate(optimisticTask);
    setIsToggling(true);

    try {
      const updatedTask = await toggleTaskComplete(userId, task.id);
      onUpdate(updatedTask);
    } catch (error) {
      // Rollback on error
      console.error("Failed to toggle task:", error);
      onUpdate({ ...task, completed: previousCompleted });
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteTask(userId, task.id);
      onDelete(task.id);
      setDeleteDialogOpen(false);
    } catch (error) {
      console.error("Failed to delete task:", error);
      alert(error instanceof Error ? error.message : "Failed to delete task");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCardClick = () => {
    router.push(`/dashboard/tasks/${task.id}`);
  };

  return (
    <div
      onClick={handleCardClick}
      className={clsx(
        "group relative flex items-start gap-4 rounded-2xl border-2 p-5 transition-all duration-200",
        "hover:border-blue-400 hover:shadow-xl hover:-translate-y-0.5 cursor-pointer",
        "bg-white/80 backdrop-blur-sm",
        task.completed && "opacity-75 hover:opacity-100"
      )}
    >
      {/* Checkbox with custom styling */}
      <div className="pt-1" onClick={(e) => e.stopPropagation()}>
        <label className="relative flex items-center justify-center cursor-pointer">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggleComplete}
            disabled={isToggling}
            className="sr-only peer"
            aria-label={`Mark "${task.title}" as ${
              task.completed ? "incomplete" : "complete"
            }`}
          />
          <div className={clsx(
            "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all",
            "peer-focus:ring-2 peer-focus:ring-offset-2 peer-focus:ring-blue-500",
            task.completed
              ? "bg-gradient-to-r from-blue-600 to-purple-600 border-transparent"
              : "border-gray-300 hover:border-blue-500 bg-white"
          )}>
            {task.completed && (
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
        </label>
      </div>

      {/* Task Content */}
      <div className="flex-1 min-w-0">
        <h3
          className={clsx(
            "text-lg font-semibold text-gray-900 mb-1",
            task.completed && "line-through text-gray-500"
          )}
        >
          {task.title}
        </h3>
        {task.description && (
          <p
            className={clsx(
              "text-sm text-gray-600 line-clamp-2 mb-2",
              task.completed && "text-gray-400"
            )}
          >
            {task.description}
          </p>
        )}
        <div className="flex items-center gap-2">
          <span className={clsx(
            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
            task.completed
              ? "bg-green-100 text-green-800"
              : "bg-yellow-100 text-yellow-800"
          )}>
            {task.completed ? "Completed" : "Pending"}
          </span>
          <span className="text-xs text-gray-500">
            {format(new Date(task.created_at), "MMM d, yyyy")}
          </span>
        </div>
      </div>

      {/* Delete Button */}
      <div onClick={(e) => e.stopPropagation()}>
        <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <DialogTrigger asChild>
            <button
              className={clsx(
                "rounded-lg p-2.5 text-gray-400 transition-all",
                "hover:bg-red-50 hover:text-red-600 hover:scale-110",
                "focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2",
                "opacity-0 group-hover:opacity-100"
              )}
              aria-label={`Delete task "${task.title}"`}
            >
              <Trash2 className="h-5 w-5" />
            </button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Task</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete "{task.title}"? This action cannot
                be undone.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="secondary"
                onClick={() => setDeleteDialogOpen(false)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? "Deleting..." : "Delete"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
