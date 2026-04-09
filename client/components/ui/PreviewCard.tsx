"use client";

import React from "react";

interface PreviewCardProps {
  image?: React.ReactNode | string;
  title: string;
  subtitle?: string;
}

export function PreviewCard({ image, title, subtitle }: PreviewCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden w-full max-w-[260px]">
      {image && (
        <div className="bg-brand-50 flex items-center justify-center h-48 p-4">
          {typeof image === "string" ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={image} alt={title} className="object-contain h-full w-full" />
          ) : (
            image
          )}
        </div>
      )}
      <div className="p-5">
        <p className="text-base font-semibold text-primary leading-snug">{title}</p>
        {subtitle && (
          <p className="text-sm text-app-text-muted mt-1 leading-snug">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
