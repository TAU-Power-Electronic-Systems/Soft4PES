Grid Components
===============

.. _grid-components:

The grid systems are built using individual components, such as grids, filters, and converters. The predefined grid components are listed in the respective sections after the example.

The following example shows how to create a grid system by combining individual components.

.. rubric:: Example — Creating a grid system from components

.. code-block:: python

   from pars.grid_config import get_custom_system

   config = get_custom_system(grid_name='Strong_LV_Grid',
                              filter_name='No_Filter',
                              converter_name='3L_LV_Converter')

The config dictionary contains the entries ``base`` (grid base-value object), ``grid_params`` (grid-parameters object), ``lcl_params`` (filter-parameters object) and ``conv`` (converter object).

.. toctree::
   :maxdepth: 2
   
   components/grids
   components/filters
   components/converters