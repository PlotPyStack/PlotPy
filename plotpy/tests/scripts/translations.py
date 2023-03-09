# -*- coding: utf-8 -*-
#
# Copyright © 2012 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""Little translation test"""


from plotpy.config import _

SHOW = False  # Do not show test in GUI-based test launcher

translations = (_("Some required entries are incorrect"),)


def test_translation():
    # TODO: 0 traiter en fonction de la langue paramétré sur l'os ?
    english_text = "Some required entries are incorrect"
    french_text = "Les champs surlignés n'ont pas été remplis correctement."
    translations = (_(english_text),)
    assert translations == french_text


if __name__ == "__main__":
    test_translation()
