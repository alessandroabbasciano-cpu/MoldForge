# Contributing to MOLD F.O.R.G.E

Keep it strictly engineering.

1. **Language:** The entire codebase, comments, commits, and pull requests MUST be in English.
2. **Style:** Strict PEP8. No exceptions.
3. **Architecture:** Do not block the PySide6 UI thread. Any heavy CadQuery/OpenCASCADE boolean operations must run in a background worker.
4. **Keep it lightweight:** Do not add massive dependencies unless absolutely critical.
