Grids
=====

The predefined grid models are are presented after the example. 

In order to create a custom grid, a new entry can be added to ``examples/grid/pars/grid_parameter_sets.json`` under ``grids`` following the structure of the existing ones. Required parameters are an unique name for the grid model, rated voltage and current, grid frequency, grid resistance and inductance.

.. rubric:: Example — Adding a grid to grid_parameter_sets.json

.. code-block:: json

   "Weak_LV_Grid": {
       "Vg_R_SI": 400,
       "Ig_R_SI": 18,
       "fg_R_SI": 50,
       "Rg_SI": 0.07,
       "Lg_SI": 30e-3
   }


Predefined Grids
----------------

.. _weak-lv-grid:

**Weak low-voltage grid** (``Weak_LV_Grid``)

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Parameter
     - Value 
   * - :math:`V_{g,R}`
     - :math:`400\,\mathrm{V}`
   * - :math:`I_{g,R}`
     - :math:`18\,\mathrm{A}`
   * - :math:`f_{g,R}`
     - :math:`50\,\mathrm{Hz}`
   * - :math:`R_g`
     - :math:`0.07\,\Omega`
   * - :math:`L_g`
     - :math:`30\,\mathrm{mH}`

.. _strong-lv-grid:

**Strong low-voltage grid** (``Strong_LV_Grid``)

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Parameter
     - Value 
   * - :math:`V_{g,R}`
     - :math:`400\,\mathrm{V}`
   * - :math:`I_{g,R}`
     - :math:`18\,\mathrm{A}`
   * - :math:`f_{g,R}`
     - :math:`50\,\mathrm{Hz}`
   * - :math:`R_g`
     - :math:`0.07\,\Omega`
   * - :math:`L_g`
     - :math:`5\,\mathrm{mH}`

.. _strong-mv-grid:

**Strong medium-voltage grid** (``Strong_MV_Grid``)

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Parameter
     - Value 
   * - :math:`V_{g,R}`
     - :math:`3300\,\mathrm{V}`
   * - :math:`I_{g,R}`
     - :math:`1575\,\mathrm{A}`
   * - :math:`f_{g,R}`
     - :math:`50\,\mathrm{Hz}`
   * - :math:`R_g`
     - :math:`0.006\,\Omega`
   * - :math:`L_g`
     - :math:`0.19\,\mathrm{mH}`