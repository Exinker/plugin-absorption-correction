## Notebooks

- Do not over-engineer notebooks. Edit only the requested cell or formula. Keep calculations inline and visible. Do not add helper functions, generalized abstractions, extra
state dictionaries, or unrelated mode support unless explicitly requested.

- Prefer visible inline calculations over helper functions. If a helper function is necessary, pass all required inputs explicitly as arguments. Do not let helper functions
depend on notebook globals except for imported libraries.

- Do not add markdown explanation cells unless explicitly requested. Prefer short variable names, visible calculations, tables, and plots over prose descriptions.

- Prefer `functools.partial` over `lambda` when passing helper functions into `map`, `apply`, optimizers, or callbacks, if it makes the bound arguments more visible.

- Avoid `np.where` when boolean mask assignment is clearer. Prefer explicit intermediate variables such as `mask`, `corrected = value.copy()`, and `corrected[mask] = ...`.

- Do not add defensive dtype conversions inside helper functions unless mixed dtypes are known to be a problem. Normalize data once during loading or preparation instead.

- Avoid defensive `.copy()` calls in notebooks. Use `.copy()` only before mutating a sliced DataFrame/array or when preserving the original object is necessary for the next
visible calculation.
