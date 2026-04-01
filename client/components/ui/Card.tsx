import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  description?: string;
}

export function Card({ children, className = "", title, description }: CardProps) {
  return (
    <div className={`card p-5 ${className}`}>
      {(title || description) && (
        <div className="mb-4">
          {title && <h3 className="text-sm font-semibold text-primary">{title}</h3>}
          {description && <p className="text-xs text-app-text-muted mt-0.5">{description}</p>}
        </div>
      )}
      {children}
    </div>
  );
}
