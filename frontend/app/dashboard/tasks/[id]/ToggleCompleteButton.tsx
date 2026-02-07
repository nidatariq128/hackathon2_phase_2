"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Check, X } from "lucide-react";
import { toggleTaskComplete } from "@/lib/api/tasks";
import { configureAuthHeader, getAuthToken } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { clsx } from "clsx";

interface ToggleCompleteButtonProps {
  taskId: number;
  userId: string;
  initialCompleted: boolean;
}

export function ToggleCompleteButton({
  taskId,
  userId,
  initialCompleted,
}: ToggleCompleteButtonProps) {
  const router = useRouter();
  const [completed, setCompleted] = React.useState(initialCompleted);
  const [isToggling, setIsToggling] = React.useState(false);

  const handleToggle = async () => {
    const previousCompleted = completed;
    setCompleted(!previousCompleted);
    setIsToggling(true);

    try {
      const token = getAuthToken();
      if (token) {
        configureAuthHeader(token);
      }

      const updatedTask = await toggleTaskComplete(userId, taskId);
      setCompleted(updatedTask.completed);
      router.refresh();
    } catch (error) {
      console.error("Failed to toggle task:", error);
      setCompleted(previousCompleted);
      alert(error instanceof Error ? error.message : "Failed to update task");
    } finally {
      setIsToggling(false);
    }
  };

  return (
    <Button
      onClick={handleToggle}
      disabled={isToggling}
      variant={completed ? "primary" : "secondary"}
      size="md"
      className={clsx(
        "min-w-[140px]",
        completed && "bg-green-600 hover:bg-green-700"
      )}
    >
      {completed ? (
        <>
          <Check className="h-4 w-4 mr-2" />
          Completed
        </>
      ) : (
        <>
          <X className="h-4 w-4 mr-2" />
          Pending
        </>
      )}
    </Button>
  );
}
