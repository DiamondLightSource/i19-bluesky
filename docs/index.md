---
html_theme.sidebar_secondary.remove: true
---


How the documentation is structured
===================================

Documentation is split into [four categories](https://diataxis.fr), also accessible from links in the top bar.

<!-- https://sphinx-design.readthedocs.io/en/latest/grids.html -->

::::{grid} 2
:gutter: 4

:::{grid-item-card} {material-regular}`directions_walk;2em`
```{toctree}
:maxdepth: 2
tutorials
```
:::{card-footer}
Tutorials for installation and typical usage. New users start here.
:::

:::{grid-item-card} {material-regular}`code;2em`
```{toctree}
:maxdepth: 2
how-to
```
<<<<<<< before updating
+++
Practical step-by-step guides to install, develop and contribute to i19-bluesky.
=======
:::{card-footer}
Practical step-by-step guides for the more experienced user.
>>>>>>> after updating
:::

:::{grid-item-card} {material-regular}`info;2em`
```{toctree}
:maxdepth: 2
explanations
```
:::{card-footer}
Explanations of how it works and why it works that way.
:::

:::{grid-item-card} {material-regular}`menu_book;2em`
```{toctree}
:maxdepth: 2
reference
```
:::{card-footer}
Technical reference material including APIs and release notes.
:::

::::
