return {
  ---@module 'python'
  {
    'joshzcold/python.nvim',
    dependencies = {
      { 'mfussenegger/nvim-dap' },
      { 'mfussenegger/nvim-dap-python' },
      { 'neovim/nvim-lspconfig' },
      { 'L3MON4D3/LuaSnip' },
      { 'nvim-neotest/neotest' },
      { 'nvim-neotest/neotest-python' },
    },
    ---@type python.Config
    opts = { ---@diagnostic disable-line: missing-fields`
    },
    -- Optional suggested keymaps
    keys = {
      { '<leader>pv', '<cmd>Python venv pick<cr>', desc = 'python.nvim: pick venv' },
      { '<leader>pi', '<cmd>Python venv install<cr>', desc = 'python.nvim: python venv install' },
      { '<leader>pd', '<cmd>Python dap<cr>', desc = 'python.nvim: python run debug program' },

      -- Test Actions
      { '<leader>ptt', '<cmd>Python test test<cr>', desc = 'python.nvim: python run test suite' },
      { '<leader>ptm', '<cmd>Python test test_method<cr>', desc = 'python.nvim: python run test method' },
      { '<leader>ptf', '<cmd>Python test test_file<cr>', desc = 'python.nvim: python run test file' },
      { '<leader>ptdd', '<cmd>Python test test_debug<cr>', desc = 'python.nvim: run test suite in debug mode.' },
      {
        '<leader>ptdm',
        '<cmd>Python test test_method_debug<cr>',
        desc = 'python.nvim: run test method in debug mode.',
      },
      { '<leader>ptdf', '<cmd>Python test_file_debug<cr>', desc = 'python.nvim: run test file in debug mode.' },

      -- VEnv Actions
      { '<leader>ped', '<cmd>Python venv delete_select<cr>', desc = 'python.nvim: select and delete a known venv.' },
      { '<leader>peD', '<cmd>Python venv delete<cr>', desc = 'python.nvim: delete current venv set.' },

      -- Language Actions
      { '<leader>ppe', '<cmd>Python treesitter toggle_enumerate<cr>', desc = 'python.nvim: turn list into enumerate' },
      {
        '<leader>pw',
        '<cmd>Python treesitter wrap_cursor<cr>',
        desc = 'python.nvim: wrap treesitter identifier with pattern',
      },
      {
        '<leader>pw',
        mode = 'v',
        ':Python treesitter wrap_cursor<cr>',
        desc = 'python.nvim: wrap treesitter identifier with pattern',
      },
    },
  },
}
