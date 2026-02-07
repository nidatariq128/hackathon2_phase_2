"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Task, CreateTaskInput, UpdateTaskInput } from "@/lib/types/task";
import { createTask, updateTask } from "@/lib/api/tasks";
import { configureAuthHeader, getAuthToken } from "@/lib/api/client";

interface TaskFormProps {
  userId: string;
  task?: Task; // If provided, form is in edit mode
  onSuccess?: (task: Task) => void;
  onCancel?: () => void;
}

interface FormErrors {
  title?: string;
  description?: string;
  submit?: string;
}

export function TaskForm({ userId, task, onSuccess, onCancel }: TaskFormProps) {
  const router = useRouter();
  const isEditMode = !!task;

  const [formData, setFormData] = React.useState({
    title: task?.title || "",
    description: task?.description || "",
  });

  const [errors, setErrors] = React.useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Title validation
    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    } else if (formData.title.length > 200) {
      newErrors.title = "Title must be 200 characters or less";
    }

    // Description validation
    if (formData.description && formData.description.length > 1000) {
      newErrors.description = "Description must be 1000 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      // Configure auth header before making request
      const token = getAuthToken();
      if (token) {
        configureAuthHeader(token);
      }

      let result: Task;

      if (isEditMode) {
        // Update existing task
        const updateData: UpdateTaskInput = {
          title: formData.title,
          description: formData.description || undefined,
        };
        result = await updateTask(userId, task.id, updateData);
      } else {
        // Create new task
        const createData: CreateTaskInput = {
          title: formData.title,
          description: formData.description || undefined,
        };
        result = await createTask(userId, createData);
      }

      if (onSuccess) {
        onSuccess(result);
      } else {
        // Default behavior: redirect to task list
        router.push("/dashboard/tasks");
      }
    } catch (err) {
      console.error("Failed to save task:", err);
      setErrors({
        submit: err instanceof Error ? err.message : "Failed to save task",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.back();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title Input */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title <span className="text-red-500">*</span>
        </label>
        <div className="mt-1">
          <Input
            id="title"
            name="title"
            type="text"
            required
            autoFocus
            value={formData.title}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, title: e.target.value }))
            }
            error={errors.title}
            placeholder="Enter task title"
            maxLength={200}
            disabled={isSubmitting}
          />
          <p className="mt-1 text-xs text-gray-500">
            {formData.title.length}/200 characters
          </p>
        </div>
      </div>

      {/* Description Textarea */}
      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-gray-700"
        >
          Description
        </label>
        <div className="mt-1">
          <Textarea
            id="description"
            name="description"
            rows={4}
            value={formData.description}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, description: e.target.value }))
            }
            error={errors.description}
            placeholder="Enter task description (optional)"
            maxLength={1000}
            disabled={isSubmitting}
          />
          <p className="mt-1 text-xs text-gray-500">
            {formData.description.length}/1000 characters
          </p>
        </div>
      </div>

      {/* Submit Error */}
      {errors.submit && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-700">{errors.submit}</p>
        </div>
      )}

      {/* Form Actions */}
      <div className="flex gap-3 justify-end">
        <Button
          type="button"
          variant="secondary"
          onClick={handleCancel}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button type="submit" variant="primary" disabled={isSubmitting}>
          {isSubmitting
            ? isEditMode
              ? "Updating..."
              : "Creating..."
            : isEditMode
            ? "Update Task"
            : "Create Task"}
        </Button>
      </div>
    </form>
  );
}
