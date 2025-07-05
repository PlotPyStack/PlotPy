.. _platforms:

Reference test platforms
------------------------

The following sections describe the reference platforms for the project.

.. note::

    The officially supported Python versions are 3.9, 3.10, 3.11, 3.12 and 3.13.

    The officially supported Qt binding is PyQt5. However, efforts have been
    made and will continue to be made to support PyQt6 and PySide6 as well.

    The project is currently tested on the following platforms:

    * Microsoft Windows 10 (64-bit)
    * Microsoft Windows 11 (64-bit)
    * CentOS Stream 8.8 (64-bit)
    * Ubuntu 22.04 LTS (64-bit)

    However, it should work on any other platform supported by its dependencies.

About requirements
^^^^^^^^^^^^^^^^^^

The ``requirements.txt`` mentioned in the following sections is a text file which
contains the list of all the Python packages required for building up the projet
environment. It is used by the ``pip`` command to install all the dependencies.

The ``requirements.txt`` file is generated automatically by the ``guidata-genreqs``
tool. It is based on the ``pyproject.toml`` file which is the reference file for the
project dependencies.

.. warning::

    Please note that the generation is not systematic and the ``requirements.txt``
    file may not be up-to-date.

To update the ``requirements.txt`` file, use the Visual Studio task
``Update requirements.txt`` or execute the following command:

.. code-block:: bash

    python -m guidata.utils.genreqs txt


Microsoft Windows 10
^^^^^^^^^^^^^^^^^^^^

First, install the latest version of Python 3.10 from the WinPython project.

.. note::

    At the time of writing, the latest version is 3.10.11.1 which can be
    download from `here <https://sourceforge.net/projects/winpython/files/WinPython_3.10/3.10.11.1/Winpython64-3.10.11.1dot.exe/download>`_.

Then install all the requirements using the following command from the WinPython
command prompt:

.. code-block:: bash

    pip install -r requirements.txt

Finally, build the Cython and C++ extensions using the following command (at this
stage, you may need to install the Microsoft Visual C++ Build Tools):

.. code-block:: bash

    python setup.py build_ext --inplace

That's it, you can now run the tests using the following command:

.. code-block:: bash

    pytest plotpy

CentOS Stream 8.8
^^^^^^^^^^^^^^^^^

.. note::

    The following instructions have been tested on CentOS Stream which is the
    reference platform for the project. However, they should work on
    any other Linux distribution relying on the ``yum`` package manager.
    As for the other distributions, you may need to adapt the instructions
    to your specific environment (e.g. use ``apt-get`` instead of ``yum``).

First, install the prerequisites:

.. code-block:: bash

    sudo yum install groupinstall "Development Tools" -y
    sudo yum install openssl-devel.i686 libffi-devel.i686 bzip2-devel.i686 sqlite-devel -y

Check that ``gcc`` is installed and available in the ``PATH`` environment variable:

.. code-block:: bash

    gcc --version

Install OpenSSL 1.1.1:

.. code-block:: bash

    wget https://www.openssl.org/source/openssl-1.1.1v.tar.gz
    tar -xvf openssl-1.1.1v.tar.gz
    cd openssl-1.1.1v
    ./config --prefix=/usr --openssldir=/etc/ssl --libdir=lib no-shared zlib-dynamic
    make
    sudo make install
    openssl version
    which openssl
    cd ..

Install Python 3.10.13 (the latest 3.10 version at the time of writing):

.. code-block:: bash

    wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz
    tar -xvf Python-3.10.13.tgz
    cd Python-3.10.13
    ./configure --enable-optimizations --with-openssl=/usr --enable-loadable-sqlite-extensions
    sudo make altinstall
    cd ..

Eventually add the ``/usr/local/bin`` directory to the ``PATH`` environment variable
if Python has warned you about it:

.. code-block:: bash

    sudo echo 'pathmunge /usr/local/bin' > /etc/profile.d/py310.sh
    chmod +x /etc/profile.d/py310.sh
    . /etc/profile  # or logout and login again (reload the environment variables)
    echo $PATH  # check that /usr/local/bin is in the PATH

Create a virtual environment and install the requirements:

.. code-block:: bash

    python3.10 -m venv plotpy-venv
    source plotpy-venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

Finally, build the Cython and C++ extensions using the following command:

.. code-block:: bash

    cd ~/path_to_plotpy_repo
    python setup.py build_ext --inplace

That's it, you can now run the tests using the following command:

.. code-block:: bash

    pytest plotpy