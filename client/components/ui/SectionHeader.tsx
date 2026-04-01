import React from "react";

interface SectionHeaderProps {
  title: string;
  description?: string;
  className?: string;
}

export function SectionHeader({ title, description, className = "" }: SectionHeaderProps) {
  return (
    <div className={`mb-5 ${className}`}>
      <h2 className="section-header">{title}</h2>
      {description && <p className="text-sm text-app-text-muted mt-1">{description}</p>}
    </div>
  );
}
