import "react";

declare module "react" {
  interface CSSProperties {
    /** Electron/Tauri title-bar drag region (Chromium). */
    WebkitAppRegion?: "drag" | "no-drag";
  }
}
