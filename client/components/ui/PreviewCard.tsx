"use client";

import React from "react";

interface PreviewCardProps {
  /** Optional image element or URL */
  image?: React.ReactNode | string;
  title: string;
  subtitle?: string;
}

export function PreviewCard({ image, title, subtitle }: PreviewCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden w-full max-w-[260px]">
      {/* Image area */}
      {image && (
        <div className="bg-gray-50 flex items-center justify-center h-48 p-4">
          {typeof image === "string" ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={image} alt={title} className="object-contain h-full w-full" />
          ) : (
            image
          )}
        </div>
      )}

      {/* Text area */}
      <div className="p-5">
        <p className="text-base font-semibold text-gray-800 leading-snug">{title}</p>
        {subtitle && (
          <p className="text-sm text-gray-400 mt-1 leading-snug">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
