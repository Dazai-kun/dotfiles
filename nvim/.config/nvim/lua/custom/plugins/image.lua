return {
  '3rd/image.nvim',
  ft = { 'markdown' },
  build = false,
  opts = {
    backend = 'kitty',
    processor = 'magick_cli',
    integrations = {
      markdown = {
        enabled = true,
        clear_in_insert_mode = true,
        download_remote_images = true,
        only_render_image_at_cursor = false,
        filetypes = { 'markdown' },
      },
    },
    max_height_window_percentage = 50,
  },
}
