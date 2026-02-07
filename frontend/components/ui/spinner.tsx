import * as React from "react";
import { clsx } from "clsx";

export interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg";
}

export function Spinner({ size = "md", className, ...props }: SpinnerProps) {
  const sizes = {
    sm: "h-4 w-4 border-2",
    md: "h-8 w-8 border-2",
    lg: "h-12 w-12 border-3",
  };

  return (
    <div
      className={clsx("inline-flex items-center justify-center", className)}
      {...props}
    >
      <div
        className={clsx(
          "animate-spin rounded-full border-solid border-blue-600 border-t-transparent",
          sizes[size]
        )}
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  );
}
