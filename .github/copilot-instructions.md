# PlotPy AI Coding Agent Instructions

This document provides stable, repository-local guidance for AI coding agents
working on PlotPy. It is intended to remain useful when PlotPy is opened on its
own, without any additional companion workspace.

## Project Overview

**PlotPy** is a Qt plotting library for scientific applications. It provides
interactive widgets, plot items, tools, panels, and builder helpers on top of
PythonQwt and guidata.

### Technology Stack

- **Python**: 3.10+ (`from __future__ import annotations`)
- **Core**: NumPy, SciPy, scikit-image
- **GUI**: Qt via QtPy, guidata, PythonQwt
- **Build**: Some features rely on Cython extensions
- **Testing**: pytest
- **Linting**: Ruff (preferred), Pylint when needed

### Architecture

```
plotpy/
|- builder/         # Factory helpers (`make.curve`, `make.image`, ...)
|- items/           # Plot items (curves, images, shapes, annotations, quiver)
|- interfaces/      # Base interfaces for tools and items
|- mathutils/       # Computation utilities (colormaps, image filters)
|- panels/          # Side panels and dockable tools
|- plot/            # Plot widgets, plot manager, interaction plumbing
|- pyplot.py        # Simplified matplotlib-like interactive plotting API
|- styles/          # Item style management
|- tools/           # Interactive tools and commands
|- widgets/         # Ready-to-use composite widgets
|- tests/           # pytest suite
```

## Development Workflows

### Running Commands

**Always use `scripts/run_with_env.py`** when running Python commands in the
development workspace so local sibling projects are resolved correctly:

```powershell
python scripts/run_with_env.py python -m pytest --ff
python scripts/run_with_env.py python -m ruff format
python scripts/run_with_env.py python -m ruff check --fix
```

### Cython Extensions

PlotPy includes optional compiled extensions. Build them before running the
full test suite when changes touch compiled modules or code that imports them:

```powershell
python scripts/run_with_env.py python setup.py build_ext --inplace
```

## Core Patterns

### Builder Pattern

PlotPy commonly exposes items through builder helpers:

```python
from plotpy.builder import make

curve = make.curve(x, y, title="Signal", color="b")
image = make.image(data, title="Image")
quiver = make.quiver(x, y, dx, dy, title="Vector field")
```

Prefer following existing builder APIs when adding new items so interactive
widgets and tests can use the new feature consistently.

### Plot Widget + Manager Pattern

Interactive behavior is usually attached through plot managers and tools:

```python
from plotpy.plot import PlotWidget
from plotpy.tools import SelectTool

widget = PlotWidget()
widget.manager.add_tool(SelectTool)
```

### Translation Rule

Wrap user-facing strings with `_()` from `plotpy.config` when they are part of
the UI or documentation surfaced through the application.

## Coding Conventions

- Use `from __future__ import annotations` in Python modules.
- Keep imports ordered: standard library, third-party, local.
- Follow repository naming style already present in the touched module.
- Prefer concise Google-style docstrings when the surrounding code uses them.
- Keep changes focused; do not refactor unrelated plotting subsystems.

## Key Files

| File | Purpose |
|------|---------|
| `plotpy/builder/` | Public item construction helpers |
| `plotpy/items/` | Plot items and rendering behavior |
| `plotpy/items/quiver.py` | QuiverItem for 2D vector field plots |
| `plotpy/interfaces/` | Base interfaces for tools and items |
| `plotpy/mathutils/` | Computation utilities (colormaps, filters) |
| `plotpy/styles/` | Item style management |
| `plotpy/pyplot.py` | Simplified matplotlib-like plotting API |
| `plotpy/plot/` | Plot widgets, manager, event flow |
| `plotpy/tools/` | Interactive tool implementations |
| `plotpy/panels/` | UI panels around plots |
| `plotpy/widgets/` | Composite widgets for applications |
| `plotpy/config.py` | Configuration and translations |
| `scripts/run_with_env.py` | Environment loader for local dev setup |

## Related Projects

- `../guidata/` - parameter and Qt utility layer
- `../PythonQwt/` - low-level plotting primitives
- `../DataLab/` - downstream application using PlotPy
