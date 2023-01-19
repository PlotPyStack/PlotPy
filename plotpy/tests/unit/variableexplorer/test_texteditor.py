# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""
Tests for texteditor.py
"""

# Test library imports
import pytest

from plotpy.widgets.variableexplorer.texteditor import TextEditor

TEXT = """01234567890123456789012345678901234567890123456789012345678901234567890123456789
dedekdh elkd ezd ekjd lekdj elkdfjelfjk e"""


@pytest.fixture
def texteditor(qtbot):
    """Set up TextEditor."""
    texteditor = TextEditor(TEXT)
    qtbot.addWidget(texteditor)
    return texteditor


def test_texteditor(texteditor):
    """Run TextEditor dialog."""
    texteditor.show()
    assert texteditor
    dlg_text = texteditor.get_value()
    assert TEXT == dlg_text


if __name__ == "__main__":
    pytest.main()
    pytest.main()
