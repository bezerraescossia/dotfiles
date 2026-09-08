return {
  "nvim-neo-tree/neo-tree.nvim",
  opts = {
    filesystem = {
      filtered_items = {
        hide_dotfiles = false,
        hide_gitignored = false,
      },
    },
  },
  config = function(_, opts)
    require("neo-tree").setup(opts)

    -- Hide the block/line cursor in Neo-tree so only the cursorline highlight
    -- marks the selection. Match the hidden-cursor color to CursorLine's bg
    -- so the covered character blends into the row instead of showing a
    -- separate block.
    local function sync_hidden_cursor_hl()
      local cursorline = vim.api.nvim_get_hl(0, { name = "CursorLine", link = false })
      vim.api.nvim_set_hl(0, "NeoTreeCursorHidden", {
        bg = cursorline.bg,
        fg = cursorline.bg,
      })
    end
    sync_hidden_cursor_hl()

    local group = vim.api.nvim_create_augroup("NeoTreeHideCursor", { clear = true })

    vim.api.nvim_create_autocmd("ColorScheme", {
      group = group,
      callback = sync_hidden_cursor_hl,
    })

    vim.api.nvim_create_autocmd("WinEnter", {
      group = group,
      callback = function()
        if vim.bo.filetype == "neo-tree" then
          vim.opt.guicursor:append("a:NeoTreeCursorHidden")
        end
      end,
    })

    vim.api.nvim_create_autocmd("WinLeave", {
      group = group,
      callback = function()
        if vim.bo.filetype == "neo-tree" then
          vim.opt.guicursor:remove("a:NeoTreeCursorHidden")
        end
      end,
    })
  end,
}
