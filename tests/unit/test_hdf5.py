# -*- coding: utf-8 -*-
#
# Copyright © 2019 CEA
# Licensed under the terms of the CECILL License
# (see plotpy/__init__.py for details)

"""
Unit tests for hdf5io module
"""


import numpy as np

from plotpy.core.dataset.datatypes import BeginGroup, DataSet, EndGroup
from plotpy.core.dataset.dataitems import (
    BoolItem,
    ChoiceItem,
    ColorItem,
    FloatArrayItem,
    FloatItem,
    IntItem,
    MultipleChoiceItem,
    StringItem,
)
from plotpy.core.io.hdf5io import HDF5Reader, HDF5Writer


class Parameters(DataSet):
    """
    DataSet test
    """

    string = StringItem("String")
    float_slider = FloatItem(
        "Float (with slider)", default=0.5, min=0, max=1, step=0.01, slider=True
    )
    integer = IntItem("Integer", default=5, min=3, max=16, slider=True)
    bool1 = BoolItem("Boolean option without label")
    _bg = BeginGroup("A sub group")
    color = ColorItem("Color", default="red")
    choice = ChoiceItem(
        "Single choice 1",
        [("16", "first choice"), ("32", "second choice"), ("64", "third choice")],
    )
    _eg = EndGroup("A sub group")
    floatarray = FloatArrayItem(
        "Float array", default=np.ones((50, 5), float), format=" %.2e "
    )
    mchoice = MultipleChoiceItem("MC", [str(i) for i in range(12)])


class Parameters_AddedParameters(Parameters):
    """DataSet with additional parameters used to test a schema like evolution"""

    added_string = StringItem("Added string", default="Added string")
    added_float = FloatItem("Added float", default=0.4, min=0, max=1)
    added_integer = IntItem("Integer", default=5, min=3, max=16)
    added_bool1 = BoolItem("Boolean option without label", default=False)
    added_bg = BeginGroup("A sub group")
    added_color = ColorItem("Color", default="red")
    added_choice = ChoiceItem(
        "Single choice 1",
        [("16", "first choice"), ("32", "second choice"), ("64", "third choice")],
        default="32",
    )
    added_eg = EndGroup("A sub group")
    added_floatarray = FloatArrayItem(
        "Float array", default=np.ones((50, 5), float), format=" %.2e "
    )
    added_mchoice = MultipleChoiceItem("MC", [str(i) for i in range(12)])


class Parameters_RemovedParameters(Parameters):
    """DataSet with some removed parameters from Parameters_AddedParameters"""

    added_floatarray = FloatArrayItem(
        "Float array", default=np.ones((50, 5), float), format=" %.2e "
    )
    added_mchoice = MultipleChoiceItem("MC", [str(i) for i in range(12)])


def test_write_read_hdf5(tmpdir):
    """Test writing and reading of DataSet to hdf5 file"""
    path = tmpdir / "test.h5"

    # Create a parameter with edited values
    written_p = Parameters()
    written_p.string = "new string"
    written_p.text = "new text"
    written_p.bool1 = True
    written_p.integer = 3
    written_p.float_slider = 0.2
    written_p.color = "blue"
    written_p.mchoice = [0, 3]

    # Write the file
    with HDF5Writer(path) as writer:
        written_p.serialize(writer)

    assert path.exists()

    # Read the file
    read_p = Parameters_AddedParameters()
    with HDF5Reader(path) as reader:
        read_p.deserialize(reader)

    # Check that read parameters are equaled to written parameters
    for item in Parameters._items:
        attr = item._name
        if attr == "floatarray":
            # can't use == to compare array
            assert np.array_equal(read_p.floatarray, written_p.floatarray)
        else:
            assert getattr(read_p, attr) == getattr(written_p, attr)


def test_read_added_parameters(tmpdir):
    """Test reading hdf5 file when DataSet parameters are not present in the file.

    This simulates an API evolution with an augmented DataSet.
    """
    path = tmpdir / "test.h5"
    params = Parameters()
    with HDF5Writer(path) as writer:
        params.serialize(writer)

    # Use TestParameters_AddedParamteters to read the .h5 file
    # added_* attributes must be set to their default value
    read_params = Parameters_AddedParameters()
    with HDF5Reader(path) as reader:
        read_params.deserialize(reader)

    assert read_params.added_string == "Added string"
    assert read_params.added_float == 0.4
    assert read_params.added_integer == 5
    assert not read_params.added_bool1
    assert read_params.added_color == "red"
    assert read_params.added_choice == "32"
    assert np.array_equal(read_params.added_floatarray, np.ones((50, 5), float))
    assert read_params.added_mchoice == ()


def test_read_removed_parameter(tmpdir):
    """Test reading hdf5 file when DataSet parameters were removed."""
    # Write parameters
    added_path = tmpdir / "test_added_parameter.h5"
    written_params = Parameters_AddedParameters()

    # Set one field that is not present in the new schema
    written_params.added_string = "new value"

    # Set one field that is present in the new schema

    written_params.added_floatarray = np.ones((20, 4), float)
    with HDF5Writer(added_path) as writer:
        written_params.serialize(writer)

    data = added_path.read_binary()
    assert b"new value" in data

    # Read back the .h5 file
    read_params = Parameters_RemovedParameters()
    with HDF5Reader(added_path) as reader:
        read_params.deserialize(reader)
    assert np.array_equal(read_params.added_floatarray, np.ones((20, 4), float))
