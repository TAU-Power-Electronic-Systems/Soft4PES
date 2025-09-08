Soft4PES
========

Software library for power electronic systems

The aim is to develop optimal control methods for power electronic systems, such as variable speed drives and converters connected to the grid. The library consists of building blocks that allow for modular solutions, allowing for adaptation of the methods to different systems. This work is under continuous development, so stay tuned!

Installation
------------

**Install Python**: Ensure that you have Python installed on your machine. You can download and install the required version from the `official website <https://www.python.org/>`_. Using a Python distribution like MiniForge is recommended. The library is compatible with Python 3.12.

**Clone the Repository**: To get started, clone the repository to your local machine by running the following command in your terminal or command prompt::

   git clone https://github.com/TAU-Power-Electronic-Systems/Soft4PES

**Navigate to the Repository Directory**: Once the repository is cloned, navigate to the ``Soft4Pes`` directory::

   cd Soft4PES

**Create a Virtual Environment (Optional)**: It is recommended to create a virtual environment to manage dependencies. Using MiniForge, you can create a virtual environment with the following command::

   conda create -n soft4pes python=3.12
   conda activate soft4pes

Note: Python 3.13 is not yet supported.

**Install Soft4PES in developer mode**: To install the library in developer mode, which allows you to make changes to the source code and have them reflected immediately, run the following command::

   pip install -e .

This step is required in order to run the examples. Note that all the required packages will be installed automatically.

**Run Example**: The repository includes example files located in the ``examples`` folder. You can test the library by running an example script. For instance, to run a grid-forming control example, use the following command:::

   python examples/grid/grid_forming_ctr.py

.. toctree::
   :titlesonly:
   :caption: API Reference
   :name: api_reference
   :maxdepth: 1

   API <autoapi/soft4pes/index>