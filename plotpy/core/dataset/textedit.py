# Copyright CEA (2018)

# http://www.cea.fr/

# This software is a computer program whose purpose is to provide an
# Automatic GUI generation for easy dataset editing and display with
# Python.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


"""
Text visitor for DataItem objects
(for test purpose only)
"""


def prompt(item):
    """Get item value"""
    return input(item.get_prop("display", "label") + " ? ")


class TextEditVisitor:
    """Text visitor"""

    def __init__(self, instance):
        self.instance = instance

    def visit_generic(self, item):
        """Generic visitor"""
        while True:
            value = prompt(item)
            item.set_from_string(self.instance, value)
            if item.check_item(self.instance):
                break
            print("Incorrect value!")

    visit_FloatItem = visit_generic
    visit_IntItem = visit_generic
    visit_StringItem = visit_generic
