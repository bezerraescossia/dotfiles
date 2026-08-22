-- AstroUI provides the basis for configuring the AstroNvim User Interface
-- Configuration documentation can be found with `:h astroui`
-- NOTE: We highly recommend setting up the Lua Language Server (`:LspInstall lua_ls`)
--       as this provides autocomplete and documentation while editing

---@type LazySpec
return {
  "AstroNvim/astroui",
  ---@type AstroUIOpts
  opts = {
    -- change colorscheme
    colorscheme = "oxocarbon",
    -- AstroUI allows you to easily modify highlight groups easily for any and all colorschemes
    highlights = {
      init = { -- this table overrides highlights in all themes
        -- Normal = { bg = "#000000" },
      },
      astrodark = { -- a table of overrides/changes when applying the astrotheme theme
        -- Normal = { bg = "#000000" },
      },
      oxocarbon = { -- a table of overrides/changes when applying the oxocarbon theme
        SnacksPickerListCursorLine = { bg = "#afc5cc" }, -- cursor line in find/grep picker results (Snacks)
      },
    },
    -- lazygit run inside nvim gets its theme generated from Neovim highlight groups
    -- (see astroui-lazygit-config.yml), not from ~/.config/lazygit/config.yml, so it
    -- needs its own override here
    lazygit = {
      theme = {
        -- oxocarbon's FloatBorder is nearly the same color as the background (by design,
        -- for a borderless float look), which made inactive panel borders invisible
        inactiveBorderColor = { fg = "Comment" },
      },
    },
    -- Icons can be configured throughout the interface
    icons = {
      -- configure the loading of the lsp in the status line
      LSPLoading1 = "⠋",
      LSPLoading2 = "⠙",
      LSPLoading3 = "⠹",
      LSPLoading4 = "⠸",
      LSPLoading5 = "⠼",
      LSPLoading6 = "⠴",
      LSPLoading7 = "⠦",
      LSPLoading8 = "⠧",
      LSPLoading9 = "⠇",
      LSPLoading10 = "⠏",
    },
  },
}
