---@type LazySpec
return {
  "nvim-neo-tree/neo-tree.nvim",
  opts = {
    filesystem = {
      window = {
        position = "float",
      },
      filtered_items = {
        visible = true, -- mostra os itens filtrados (ocultos) por padrão
        hide_dotfiles = false, -- não esconde arquivos que começam com "."
        hide_gitignored = false, -- opcional: também mostra arquivos no .gitignore
      },
    },
  },
}
