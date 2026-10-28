# Version 2.12 #

## PlotPy Version 2.12.0 ##

🛠️ Bug fixes:

* **Curve fitting dialog** — Running the automatic fit no longer raises `OverflowError: argument 1 overflowed` errors when a fitted value ends up far outside the range of its slider (e.g. with the Powell method on a fit range restricted to the tail of a peak). These errors left the slider of the parameter unresponsive, and the values of the following parameters were not displayed. Such values are now shown with a warning icon, whose tooltip gives the slider range, while the slider stays at its nearest end. Typing `nan` or `inf` in a parameter field now restores the previous value instead of raising errors, and the number of slider steps must be at least 2 in the parameter properties dialog (closes [Issue #76](https://github.com/PlotPyStack/PlotPy/issues/76))
* **Cross-section panels with many hidden images** — X/Y cross-section panels kept one curve for every image ever displayed, even after it was hidden, so plots containing hundreds of hidden images became progressively slower to refresh. Curves are now only kept for visible images, and are recreated when a hidden image is shown again

⚡ Performance:

* **Plot refresh** — Refreshing a plot no longer recomputes the plot layout when the title and axis styles did not change
* **Item tools and item list** — Updating the status of item-related tools and of the item list panel is no longer quadratic in the number of plot items
* **Image creation** — Creating an image item no longer recomputes the colormap lookup table when the same colormap, inversion and transparency settings were already used: the table (more than 1000 colormap evaluations) is computed once and reused, which saves a few milliseconds per image

⚙️ Dependencies:

* Python 3.10 or later is now required, and wheels are no longer built for Python 3.9. Python 3.9 users must keep an earlier compatible release (PlotPy 2.11.x)
