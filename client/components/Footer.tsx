import React from "react";

export function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="mt-6 pb-4 text-center">
      <div className="flex flex-col items-center gap-1.5">
        {/* Lab + University */}
        <div className="flex items-center gap-2 text-xs text-app-text-muted">
          <a
            href="https://www.colorado.edu/ceae/larsonlab"
            target="_blank"
            rel="noopener noreferrer"
            className="font-semibold text-brand-600 hover:text-brand-700 transition-colors"
          >
            Larson Lab
          </a>
          <span className="text-brand-200">|</span>
          <span>Civil, Environmental &amp; Architectural Engineering</span>
          <span className="text-brand-200">|</span>
          <span>University of Colorado Boulder</span>
        </div>

        {/* Contact */}
        <div className="flex items-center gap-3 text-xs text-app-text-light">
          <a
            href="mailto:larsonlab@colorado.edu"
            className="hover:text-brand-600 transition-colors"
          >
            larsonlab@colorado.edu
          </a>
          <span className="text-brand-200">·</span>
          <span>Engineering Center, Boulder, CO 80309</span>
        </div>

        {/* Copyright */}
        <p className="text-[11px] text-app-text-light mt-0.5">
          &copy; {year} Larson Lab, University of Colorado Boulder. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
