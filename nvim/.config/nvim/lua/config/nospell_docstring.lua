-- Markdown files get *italic*/**bold** exempted from spellcheck via the
-- (emphasis)/(strong_emphasis) @nospell override in
-- after/queries/markdown_inline/highlights.scm, since tree-sitter actually
-- parses those as markdown there. Elsewhere (docstrings, comments) there's
-- no markdown parser running over the string/comment text, so the same
-- *word*/**word** convention is exempted here with a plain scan restricted
-- to nodes the buffer's own highlight query already marks @spell (i.e.
-- comments and docstrings, never plain code).
local M = {}

local ns = vim.api.nvim_create_namespace("nospell_docstring")

local function mark_line(bufnr, row, line, from, to)
  local i = from + 1
  while true do
    local star = line:find("*", i, true)
    if not star or star > to then
      break
    end
    local s, e = line:find("^%*%*[%w_'%-]+%*%*", star)
    if not s then
      s, e = line:find("^%*[%w_'%-]+%*", star)
    end
    if s and e <= to then
      vim.api.nvim_buf_set_extmark(bufnr, ns, row, s - 1, { end_col = e, spell = false })
      i = e + 1
    else
      i = star + 1
    end
  end
end

local function mark_node(bufnr, node)
  local srow, scol, erow, ecol = node:range()
  for row = srow, erow do
    local line = vim.api.nvim_buf_get_lines(bufnr, row, row + 1, false)[1]
    if line then
      mark_line(bufnr, row, line, row == srow and scol or 0, row == erow and ecol or #line)
    end
  end
end

function M.refresh(bufnr)
  bufnr = bufnr or 0
  if vim.bo[bufnr].filetype == "markdown" then
    return -- handled by the markdown_inline query override instead
  end
  vim.api.nvim_buf_clear_namespace(bufnr, ns, 0, -1)

  local ok, parser = pcall(vim.treesitter.get_parser, bufnr)
  if not ok or not parser then
    return
  end

  parser:parse()
  parser:for_each_tree(function(tree, lang_tree)
    local query_ok, query = pcall(vim.treesitter.query.get, lang_tree:lang(), "highlights")
    if not query_ok or not query then
      return
    end
    for id, node in query:iter_captures(tree:root(), bufnr, 0, -1) do
      if query.captures[id] == "spell" then
        mark_node(bufnr, node)
      end
    end
  end)
end

function M.setup()
  vim.api.nvim_create_augroup("nospell_docstring", { clear = true })
  vim.api.nvim_create_autocmd({ "BufEnter", "TextChanged", "TextChangedI", "InsertLeave" }, {
    group = "nospell_docstring",
    callback = function(ev)
      M.refresh(ev.buf)
    end,
  })

  -- autocmds.lua loads on VeryLazy, after the startup buffer's own BufEnter
  -- already fired, so give that buffer an initial pass too.
  M.refresh(vim.api.nvim_get_current_buf())
end

return M
