Filters
=======

The predefined filter models are presented after the example. 

In order to create a custom filter, a new entry can be added to ``examples/grid/pars/grid_parameter_sets.json`` under ``filters`` following the structure of the existing ones. Required parameters are an unique name for the filter model, and resistance, inductance and capacitance values. Filterless system can also be used with the ``No_Filter`` entry.

.. rubric:: Example — Adding an LCL filter to grid_parameter_sets.json

.. code-block:: json

  "LCL_Filter_fr_1300": {
              "L_fc_SI": 3e-3,
              "R_fc_SI": 0.1,
              "C_SI": 10e-6,
              "R_c_SI": 1e-3,
              "L_fg_SI": 3e-3,
              "R_fg_SI": 0.1
  }


Predefined Filters
------------------

.. _lcl-filter-1300:

:math:`\mathrm{LCL}` **filter** (:math:`f_r = 1300\,\mathrm{Hz}`) (``LCL_Filter_fr_1300``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value
   * - Filter converter-side inductance
     - :math:`L_{\mathrm{fc}}`
     - :math:`3\,\mathrm{mH}`
   * - Filter converter-side resistance
     - :math:`R_{\mathrm{fc}}`
     - :math:`0.1\,\Omega`
   * - Filter capacitance
     - :math:`C`
     - :math:`10\,\mu\mathrm{F}`
   * - Damping resistor (capacitor)
     - :math:`R_c`
     - :math:`1\,\mathrm{m}\Omega`
   * - Filter grid-side inductance
     - :math:`L_{\mathrm{fg}}`
     - :math:`3\,\mathrm{mH}`
   * - Filter grid-side resistance
     - :math:`R_{\mathrm{fg}}`
     - :math:`0.1\,\Omega`


.. _lcl-filter-380:

:math:`\mathrm{LCL}` **filter** (:math:`f_r = 380\,\mathrm{Hz}`) (``LCL_Filter_fr_380``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value
   * - Filter converter-side inductance
     - :math:`L_{\mathrm{fc}}`
     - :math:`0.4\,\mathrm{mH}`
   * - Filter converter-side resistance
     - :math:`R_{\mathrm{fc}}`
     - :math:`0.5\,\mathrm{m}\Omega`
   * - Filter capacitance
     - :math:`C`
     - :math:`850\,\mu\mathrm{F}`
   * - Damping resistor (capacitor)
     - :math:`R_c`
     - :math:`0.4\,\mathrm{m}\Omega`
   * - Filter grid-side inductance
     - :math:`L_{\mathrm{fg}}`
     - :math:`0.4\,\mathrm{mH}`
   * - Filter grid-side resistance
     - :math:`R_{\mathrm{fg}}`
     - :math:`0.5\,\mathrm{m}\Omega`


.. _no-filter:

**No filter** (``No_Filter``)

Direct connection to the grid without any filter.