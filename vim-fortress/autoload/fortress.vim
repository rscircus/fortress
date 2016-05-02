" VIM Autoload script for FORTRESS support
"
" Author: r@rscircus.org
"
" Put this file into your ~/.vim/autoload directory.
"
" You can use mappings like:
"
"    map <C-F> :call fortress#format()<cr>
"    imap <C-F> <C-O>:call fortress#format()<cr>
"
function! fortress#format() range
  " Determine range to format.
  let l:line_ranges = a:firstline . '-' . a:lastline
  let l:cmd = 'fortress --lines=' . l:line_ranges

  " Call fortress with the current buffer
  let l:formatted_text = system(l:cmd, join(getline(1, '$'), "\n") . "\n")

  " Update the buffer.
  execute '1,' . string(line('$')) . 'delete'
  call setline(1, split(l:formatted_text, "\n"))

  " Reset cursor to first line of the formatted range.
  call cursor(a:firstline, 1)
endfunction
