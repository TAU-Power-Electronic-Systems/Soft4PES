Converters
==========

The predefined converter models are presented after the example. 

In order to create a custom converter, a new entry can be added to ``examples/machine/pars/machine_parameter_sets.json`` under ``converters`` following the structure of the existing ones. Required parameters are an unique name for the converter model, dc-link voltage and number of voltage levels.

.. rubric:: Example — Adding a converter to machine_parameter_sets.json

.. code-block:: json

   "2L_LV_Converter": {
            "Vdc_SI": 750,
            "conv_nl": 2
    }

Predefined Converters
---------------------

.. _2l-lv-converter:

**2-Level low-voltage converter** (``2L_LV_Converter``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value
   * - Dc-link voltage
     - :math:`V_{\mathrm{dc}}`
     - :math:`750\,\mathrm{V}`
   * - Converter voltage levels
     - :math:`n_{\mathrm{conv}}`
     - :math:`2`


.. _3l-lv-converter:

**3-Level low-voltage converter** (``3L_LV_Converter``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value
   * - Dc-link voltage
     - :math:`V_{\mathrm{dc}}`
     - :math:`750\,\mathrm{V}`
   * - Converter voltage levels
     - :math:`n_{\mathrm{conv}}`
     - :math:`3`


.. _2l-mv-converter:

**2-Level medium-voltage converter** (``2L_MV_Converter``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value
   * - Dc-link voltage
     - :math:`V_{\mathrm{dc}}`
     - :math:`5200\,\mathrm{V}`
   * - Converter voltage levels
     - :math:`n_{\mathrm{conv}}`
     - :math:`2`


.. _3l-mv-converter:

**3-Level medium-voltage converter** (``3L_MV_Converter``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value
   * - Dc-link voltage
     - :math:`V_{\mathrm{dc}}`
     - :math:`5200\,\mathrm{V}`
   * - Converter voltage levels
     - :math:`n_{\mathrm{conv}}`
     - :math:`3`