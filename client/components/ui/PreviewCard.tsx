"use client";

import React from "react";

interface PreviewCardProps {
  image?: React.ReactNode | string;
  title: string;
  subtitle?: string;
}

export function PreviewCard({ image, title, subtitle }: PreviewCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden w-full max-w-[400px]">
      {image && (
        <div className="bg-brand-50 flex items-center justify-center h-72 p-6">
          {typeof image === "string" ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={image} alt={title} className="object-contain h-full w-full" />
          ) : (
            image
          )}
        </div>
      )}
      <div className="p-6">
        <p className="text-lg font-semibold text-primary leading-snug">{title}</p>
        {subtitle && (
          <p className="text-sm text-app-text-muted mt-1.5 leading-snug">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
