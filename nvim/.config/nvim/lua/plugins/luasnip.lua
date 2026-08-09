return {
  "L3MON4D3/LuaSnip",
  version = "v2.*",
  build = "make install_jsregexp",
  config = function()
    local ls = require("luasnip")

    -- 1. Keymaps para navegar nos choices (próximo e anterior)
    vim.keymap.set({ "i", "s" }, "<C-j>", function()
      if ls.choice_active() then
        ls.change_choice(1)
      end
    end, { silent = true, desc = "Cycle next choice" })

    vim.keymap.set({ "i", "s" }, "<C-k>", function()
      if ls.choice_active() then
        ls.change_choice(-1)
      end
    end, { silent = true, desc = "Cycle previous choice" })

    -- 2. Menu visual de seleção
    vim.keymap.set({ "i", "s" }, "<C-e>", function()
      if ls.choice_active() then
        local ok, select_choice = pcall(require, "luasnip.extras.select_choice")
        if ok then
          select_choice()
        end
      end
    end, { silent = true, desc = "Select LuaSnip choice from menu" })

    -- 3. Carrega automaticamente todos os snippets da pasta lua/snippets/
    require("luasnip.loaders.from_lua").lazy_load({
      paths = vim.fn.stdpath("config") .. "/lua/snippets",
    })
  end,
}
