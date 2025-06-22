# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""Test cyclic import issue"""

# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import


def test_tools_cyclic_import():
    """Test cyclic import issue"""
    # Importing one tool from each module to check if there is a cyclic import issue
    from plotpy.tools import (
        AnnotatedPointTool,  # noqa: F401
        AverageCrossSectionTool,  # noqa: F401
        CurveStatsTool,  # noqa: F401
        DoAutoscaleTool,  # noqa: F401
        ItemCenterTool,  # noqa: F401
        OpenImageTool,  # noqa: F401
        PointTool,  # noqa: F401
        PrintTool,  # noqa: F401
        RectangularActionTool,  # noqa: F401
        SelectTool,  # noqa: F401
        YRangeCursorTool,  # noqa: F401
    )


if __name__ == "__main__":
    test_tools_cyclic_import()
