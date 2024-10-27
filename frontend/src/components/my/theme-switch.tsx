"use client";

import { useTheme } from "next-themes";
import { MdOutlineDarkMode, MdOutlineLightMode } from "react-icons/md";

export default function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="text-muted-foreground hover:text-accent-foreground h-7">
      {theme === "light" ? (
        <button onClick={() => setTheme("dark")} className="p-0">
          <MdOutlineLightMode className="w-7 h-7" />
        </button>
      ) : (
        <button onClick={() => setTheme("light")} className="p-0">
          <MdOutlineDarkMode className="w-7 h-7" />
        </button>
      )}
    </div>
  );
}
