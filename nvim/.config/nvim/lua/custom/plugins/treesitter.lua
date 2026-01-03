return {
  { -- Highlight, edit, and navigate code
    'nvim-treesitter/nvim-treesitter',
    build = ':TSUpdate',
    main = 'nvim-treesitter.configs', -- Sets main module to use for opts
    -- [[ Configure Treesitter ]] See ":help nvim-treesitter"
    opts = {
      ensure_installed = {
        'python',
        'bash',
        'json',
        'yaml',
        'toml',
        'sql',
        'dockerfile',
        'lua',
        'vim',
        'vimdoc',
        'markdown',
        'markdown_inline',
      },
      -- Autoinstall languages that are not installed
      auto_install = true,
      highlight = {
        enable = true,
        -- Some languages depend on vim's regex highlighting system (such as Ruby) for indent rules.
        --  If you are experiencing weird indenting issues, add the language to
        --  the list of additional_vim_regex_highlighting and disabled languages for indent.
        additional_vim_regex_highlighting = { 'ruby' },
      },
      indent = { enable = false, disable = { 'ruby' } },
    },
    incremental_selection = {
      enable = true,
      keymaps = {
        init_selection = '<CR>',
        node_incremental = '<CR>',
        node_decremental = '<BS>',
      },
    },
    -- There are additional nvim-treesitter modules that you can use to interact
    -- with nvim-treesitter. You should go explore a few and see what interests you:
    --
    --    - Incremental selection: Included, see ":help nvim-treesitter-incremental-selection-mod"
    --    - Show your current context: https://github.com/nvim-treesitter/nvim-treesitter-context
    --    - Treesitter + textobjects: https://github.com/nvim-treesitter/nvim-treesitter-textobjects
    textobjects = {
      select = {
        enable = true,
        lookahead = true, -- jump forward automatically

        keymaps = {
          -- functions
          ['af'] = '@function.outer',
          ['if'] = '@function.inner',

          -- classes
          ['ac'] = '@class.outer',
          ['ic'] = '@class.inner',

          -- conditionals / loops (very useful in Python)
          ['ai'] = '@conditional.outer',
          ['ii'] = '@conditional.inner',

          ['al'] = '@loop.outer',
          ['il'] = '@loop.inner',
        },
      },

      move = {
        enable = true,
        set_jumps = true,

        goto_next_start = {
          [']m'] = '@function.outer',
          [']c'] = '@class.outer',
        },
        goto_previous_start = {
          ['[m'] = '@function.outer',
          ['[c'] = '@class.outer',
        },
      },
    },
  },
  {
    'nvim-treesitter/nvim-treesitter-context',
    opts = {
      enable = true,
      max_lines = 3, -- don’t eat screen space
      multiline_threshold = 20,
      trim_scope = 'outer',
      mode = 'cursor', -- context follows cursor
    },
  },
}
