-- 1. Create a named group to prevent "stacking" (duplicate triggers) when you source your config
local refresh_group = vim.api.nvim_create_augroup('GeminiRefresh', { clear = true })

-- 2. Create the autocmd with a 'desc' for easier debugging (:au GeminiRefresh)
vim.api.nvim_create_autocmd({ 'FocusGained', 'BufEnter' }, {
  group = refresh_group,
  pattern = '*',
  desc = 'Reload buffer when Gemini CLI edits files externally',
  callback = function()
    if vim.fn.getcmdwintype() == '' then
      vim.cmd 'checktime'
    end
  end,
})
