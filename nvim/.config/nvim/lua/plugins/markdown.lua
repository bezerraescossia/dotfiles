return {
  "MeanderingProgrammer/render-markdown.nvim",
  dependencies = { "nvim-treesitter/nvim-treesitter", "nvim-tree/nvim-web-devicons" },
  ft = { "markdown" },
  opts = {
    heading = {
      icons = function(ctx)
        if ctx.level == 1 then
          return ""
        end
        local parts = {}
        for i = 2, ctx.level do
          table.insert(parts, ctx.sections[i])
        end
        return table.concat(parts, ".") .. ". "
      end,
    },
  },
}
