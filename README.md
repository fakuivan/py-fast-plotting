# Fast plotting with PyQtGraph and Edifice

This repo contains a demo application for fast plotting using
PyQtGraph and Edifice. The component implementations are in no
way optimized, yet it manages to be much faster than a matplotlib
based implementation.

## Import issues

Python does not allow for relative imports, unless you run this on
your shell before invoking `python harmonic_comp.py`:

```
export PYTHONPATH="${PYTHONPATH}:.."
```

Run that if you see an import or module error.
