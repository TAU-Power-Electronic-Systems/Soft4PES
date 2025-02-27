Soft4PES
========

Software library for power electronic systems

The aim is to develop optimal control methods for power electronic systems, such as variable speed drives and converters connected to the grid. The library consists of building blocks that allow for modular solutions, allowing for adaptation of the methods to different systems. This work is under continuous development, so stay tuned!

Installation
------------

**Install Python**: Ensure that you have Python installed on your machine. You can download and install the latest version from the `official website <https://www.python.org/>`_.

**Clone the Repository**: To get started, clone the repository to your local machine by running the following command in your terminal or command prompt::

   git clone https://github.com/TAU-Power-Electronic-Systems/Soft4PES

**Navigate to the Repository Directory**: Once the repository is cloned, navigate to the ``Soft4Pes`` directory::

   cd Soft4PES

**Install Required Dependencies**: Install the required Python packages listed in the ``requirements.txt`` file. It is recommended to either create a virtual environment or ensure that Python is added to your system's PATH variable. To install the dependencies, run:::

   pip install -r requirements.txt

**Run Example**: The repository includes example files located in the ``examples`` folder. You can test the library by running an example script. For instance, to run a grid-forming control example, use the following command:::

   python examples/grid/grid_forming_ctr.py

.. toctree::
   :titlesonly:
   :caption: API Reference
   :name: api_reference
   :maxdepth: 1

   API <autoapi/soft4pes/index>