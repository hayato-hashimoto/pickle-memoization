== Usage ==
    from pickle_memoization import memoize
    @memoize("path/to/cachedir")
    def heavy_function(file, test):
      ...

If ``heavy_function`` is called for the first time, or the function call is not the same as before, then the return value of the function will be cached to the disk; otherwise previously saved result will be used.

Function call is judged to be "the same" if all of the following conditions are met:
  1. Arguments are the same
  2. If it takes ``file``, ``files`` or ``path`` as arguments, file name and contents are the same
  3. The function name is the same
  4. The function body is the same
  5. Functions called within the body is recursively the same

Note that in some cases (non-picklable objects and anonymous functions) ``pickle_memoization`` fails to detect changes of arguments or functions.
Remove cache files manually in such cases.
