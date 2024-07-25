#!/bin/bash
set -e -u -x

ARCH=$(uname -m)
export PLAT=manylinux_2_24_$ARCH

# Accurately check if Python version is 3.8 or greater
function is_python_version_ge_38 {
    local pydir="$1"
    if [[ $pydir =~ cp([0-9]+)([0-9]+)-cp ]]; then
        local version="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
        # Use sort with version sort flag to compare version against 3.8
        if [[ $(echo -e "3.8\n$version" | sort -V | head -n1) == "3.8" ]]; then
            return 0  # True, version is >= 3.8
        fi
    fi
    return 1  # False, version is < 3.8
}

# Compile wheels, only for CPython 3.8+
for PYDIR in /opt/python/*; do
    if is_python_version_ge_38 "$PYDIR"; then
        PYBIN="$PYDIR/bin"
        "${PYBIN}/pip" install -r /io/requirements.txt
        "${PYBIN}/pip" wheel /io/ --no-deps -w wheelhouse/
    fi
done

# Bundle external shared libraries into the wheels
for wheel in wheelhouse/*.whl; do
    if auditwheel show "$wheel"; then
        auditwheel repair "$wheel" --plat "$PLAT" -w /io/wheelhouse/
    fi
done

# Install packages and test, only for CPython 3.8+
for PYDIR in /opt/python/*; do
    if is_python_version_ge_38 "$PYDIR"; then
        PYBIN="$PYDIR/bin"
        "${PYBIN}/pip" install plotpy --no-index -f /io/wheelhouse
        (cd "$HOME"; INSTDIR=$("${PYBIN}/python" -c "import plotpy, os.path as osp; print(osp.dirname(plotpy.__file__))"); export QT_QPA_PLATFORM=offscreen; "${PYBIN}/pytest" "$INSTDIR")
    fi
done
