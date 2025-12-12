Grids
=====

The predefined grid models are are presented after the example. 

In order to create a custom grid, a new entry can be added to ``examples/grid/pars/grid_parameter_sets.json`` under ``grids`` following the structure of the existing ones. Required parameters are an unique name for the grid model, rated voltage and current, grid frequency, grid resistance and inductance. Note that the rated voltage is the line-to-line rms voltage and the rated current is the rms current.

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
   :widths: 40 20 20 20
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value [SI]
     - Value [pu]
   * - Grid rated voltage (line-to-line, rms)
     - :math:`V_{g,R}`
     - :math:`400\,\text{V}`
     - 
   * - Grid rated current (rms)
     - :math:`I_{g,R}`
     - :math:`18\,\text{A}`
     - 
   * - Grid rated frequency
     - :math:`f_{g,R}`
     - :math:`50\,\text{Hz}`
     - 
   * - Grid resistance
     - :math:`R_g`
     - :math:`0.07\,\Omega`
     - :math:`0.006\,\text{p.u.}`
   * - Grid inductance
     - :math:`L_g`
     - :math:`30\,\text{mH}`
     - :math:`0.73\,\text{p.u.}`

.. _strong-lv-grid:

**Strong low-voltage grid** (``Strong_LV_Grid``)

.. list-table::
   :widths: 40 20 20 20
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value [SI]
     - Value [pu]
   * - Grid rated voltage (line-to-line, rms)
     - :math:`V_{g,R}`
     - :math:`400\,\text{V}`
     - 
   * - Grid rated current (rms)
     - :math:`I_{g,R}`
     - :math:`18\,\text{A}`
     - 
   * - Grid rated frequency
     - :math:`f_{g,R}`
     - :math:`50\,\text{Hz}`
     - 
   * - Grid resistance
     - :math:`R_g`
     - :math:`0.07\,\Omega`
     - :math:`0.006\,\text{p.u.}`
   * - Grid inductance
     - :math:`L_g`
     - :math:`5\,\text{mH}`
     - :math:`0.12\,\text{p.u.}`

.. _strong-mv-grid:

**Strong medium-voltage grid** (``Strong_MV_Grid``)

.. list-table::
   :widths: 40 20 20 20
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value [SI]
     - Value [pu]
   * - Grid rated voltage (line-to-line, rms)
     - :math:`V_{g,R}`
     - :math:`3300\,\text{V}`
     - 
   * - Grid rated current (rms)
     - :math:`I_{g,R}`
     - :math:`1575\,\text{A}`
     - 
   * - Grid rated frequency
     - :math:`f_{g,R}`
     - :math:`50\,\text{Hz}`
     - 
   * - Grid resistance
     - :math:`R_g`
     - :math:`0.006\,\Omega`
     - :math:`0.0004\,\text{p.u.}`
   * - Grid inductance
     - :math:`L_g`
     - :math:`0.19\,\text{mH}`
     - :math:`0.005\,\text{p.u.}`