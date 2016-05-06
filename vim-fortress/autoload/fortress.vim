" VIM Autoload script for FORTRESS support
"
" Author: r@rscircus.org
"
" Put this file into your ~/.vim/autoload directory.
"
" You can use mappings like:
"
"    This one uses the style.ini in the local dir from which vim was started in:
"    map <leader>ff :call fortress#format()<cr>
"    imap <leader>ff :call fortress#format()<cr>
"
function! fortress#format() range
  " Determine range to format.
  let l:line_ranges = a:firstline . '-' . a:lastline
  let l:cmd = 'fortress -l ' . l:line_ranges . ' -s style.ini'

  " Call fortress with the current buffer
  let l:formatted_text = system(l:cmd, join(getline(1, '$'), "\n") . "\n")

  " Update the buffer.
  execute '1,' . string(line('$')) . 'delete'
  call setline(1, split(l:formatted_text, "\n"))

  " Reset cursor to first line of the formatted range.
  call cursor(a:firstline, 1)
endfunction
