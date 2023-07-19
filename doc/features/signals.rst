Qt signals
----------

In `guiqwt` version 2, the `signals` module used to contain constants defining
the custom Qt ``SIGNAL`` objects used by `guiqwt`: the signals definition were
gathered there to avoid misspelling signals at connect and emit sites (with
old-style signals, any misspelled signal string would have lead to a silent
failure of signal emission or connection).

Since version 3, to ensure PyQt5 compatibility, `guiqwt` and thus plotpy are using
only new-style signals and slots.

All signals are summarized below, in order to facilitate migration
from `guiqwt` v2 to v3, then to plotpy.

Signals emitted by :py:class:`.BasePlot` objects:

- :py:attr:`.BasePlot.SIG_ITEM_MOVED`
- :py:attr:`.BasePlot.SIG_ITEM_RESIZED`
- :py:attr:`.BasePlot.SIG_ITEM_ROTATED`
- :py:attr:`.BasePlot.SIG_MARKER_CHANGED`
- :py:attr:`.BasePlot.SIG_AXES_CHANGED`
- :py:attr:`.BasePlot.SIG_ANNOTATION_CHANGED`
- :py:attr:`.BasePlot.SIG_RANGE_CHANGED`
- :py:attr:`.BasePlot.SIG_ITEMS_CHANGED`
- :py:attr:`.BasePlot.SIG_ACTIVE_ITEM_CHANGED`
- :py:attr:`.BasePlot.SIG_ITEM_REMOVED`
- :py:attr:`.BasePlot.SIG_ITEM_SELECTION_CHANGED`
- :py:attr:`.BasePlot.SIG_PLOT_LABELS_CHANGED`
- :py:attr:`.BasePlot.SIG_AXIS_DIRECTION_CHANGED`
- :py:attr:`.BasePlot.SIG_LUT_CHANGED`
- :py:attr:`.BasePlot.SIG_MASK_CHANGED`
- :py:attr:`.BasePlot.SIG_CS_CURVE_CHANGED`

Signals emitted by other objects:

- :py:attr:`.PanelWidget.SIG_VISIBILITY_CHANGED`
- :py:attr:`.InteractiveTool.SIG_VALIDATE_TOOL`
- :py:attr:`.InteractiveTool.SIG_TOOL_JOB_FINISHED`
- :py:attr:`.OpenFileTool.SIG_OPEN_FILE`
- :py:attr:`.ImageMaskTool.SIG_APPLIED_MASK_TOOL`
