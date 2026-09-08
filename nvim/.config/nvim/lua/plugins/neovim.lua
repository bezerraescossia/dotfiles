return {
  {
    "bjarneo/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      colors = {
        bg = "#0a0a0f",
        dark_bg = "#08080b",
        darker_bg = "#050508",
        lighter_bg = "#0a0a0f",

        fg = "#e0f7ff",
        dark_fg = "#4a4a5c",
        light_fg = "#e0f7ff",
        bright_fg = "#ffffff",
        muted = "#4a4a5c",

        red = "#ff2a6d",
        yellow = "#ffd700",
        orange = "#ffd700",
        green = "#39ff14",
        cyan = "#00CCCC",
        blue = "#00FFFF",
        magenta = "#ff00ff",
        brown = "#806c00",

        bright_red = "#ff5c8d",
        bright_yellow = "#ffe44d",
        bright_green = "#5fff44",
        bright_cyan = "#33dddd",
        bright_blue = "#66FFFF",
        bright_magenta = "#ff66ff",

        accent = "#00FFFF",
        cursor = "#ffffff",
        foreground = "#e0f7ff",
        background = "#0a0a0f",
        selection = "#B0ABAB",
        selection_foreground = "#0a0a0f",
        selection_background = "#00FFFF",
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "aether",
    },
  },
}
