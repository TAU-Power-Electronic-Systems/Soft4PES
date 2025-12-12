Drive Components
==================

.. _drive-components:

The drive systems are built using machines and converters. The predefined drive components are listed in the respective sections after the example.

The following example shows how to create a drive system by combining individual components.

.. rubric:: Example — Creating a drive system from components

.. code-block:: python

   from pars.machine_config import get_custom_system

   config = get_custom_system(machine_name='LV_Induction_Machine',
                              converter_name='2L_LV_Converter')

The config dictionary contains the entries ``base`` (machine base-value object), ``machine_params`` (machine-parameters object), and ``conv`` (converter object).
   
.. toctree::
   :maxdepth: 2

   components/machines
   components/converters