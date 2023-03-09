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
BINARY_TEXT = TEXT.encode("ascii")


def get_texteditor(bot, text, read_only):
    """Set up TextEditor."""
    texteditor = TextEditor(text, readonly=read_only)
    bot.addWidget(texteditor)
    return texteditor


@pytest.mark.parametrize("read_only", [True, False])
def test_texteditor_str(qtbot, read_only):
    """Run TextEditor dialog."""
    texteditor = get_texteditor(qtbot, TEXT, read_only)
    texteditor.show()
    assert texteditor
    dlg_text = texteditor.get_value()
    assert TEXT == dlg_text


def test_text_editor_binary(qtbot):
    texteditor = get_texteditor(qtbot, BINARY_TEXT, read_only=True)
    texteditor.show()
    assert texteditor
    dlg_text = texteditor.get_value()
    assert BINARY_TEXT == dlg_text


@pytest.mark.parametrize("read_only", [True, False])
def test_text_editor_change_text(qtbot, read_only):
    texteditor = get_texteditor(qtbot, BINARY_TEXT, read_only=read_only)
    qtbot.keyClicks(texteditor.edit, "test")


@pytest.mark.parametrize(
    "text,return_", [(TEXT, True), (BINARY_TEXT, True), (15, False)]
)
def test_text(qtbot, text, return_):
    texteditor = TextEditor("test")
    ret = texteditor.setup_and_check(text)
    assert ret == return_


if __name__ == "__main__":
    pytest.main()
