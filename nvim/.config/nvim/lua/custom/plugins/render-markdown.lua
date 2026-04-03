return {
  'MeanderingProgrammer/render-markdown.nvim',
  ft = { 'markdown' },
  dependencies = {
    'nvim-treesitter/nvim-treesitter',
    { 'nvim-tree/nvim-web-devicons', enabled = vim.g.have_nerd_font },
  },
  ---@module 'render-markdown'
  ---@type render.md.UserConfig
  opts = {
    completions = {
      lsp = { enabled = true },
    },
  },
}
