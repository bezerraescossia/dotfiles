---@type LazySpec
return {
  "nvim-neo-tree/neo-tree.nvim",
  opts = {
    sources = {
      "filesystem",
      "document_symbols",
      "buffers",
    },
    source_selector = {
      sources = {
        { source = "filesystem" },
        { source = "document_symbols" },
        { source = "buffers" },
      },
    },
    filesystem = {
      window = {
        position = "left",
      },
      filtered_items = {
        visible = true, -- mostra os itens filtrados (ocultos) por padrão
        hide_dotfiles = false, -- não esconde arquivos que começam com "."
        hide_gitignored = false, -- opcional: também mostra arquivos no .gitignore
      },
    },
    document_symbols = {
      window = {
        mappings = {
          -- default global mapping, but document_symbols has no clipboard commands
          ["<C-r>"] = "noop",
        },
      },
    },
  },
}
