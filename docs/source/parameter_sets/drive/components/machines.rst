Machines
========

The predefined machine models are presented after the example. 

In order to create a custom machine, a new entry can be added to ``examples/machine/pars/machine_parameter_sets.json`` under ``machines`` following the structure of the existing ones. Required parameters are an unique name for the machine model, machine class, and machine specific parameters.

.. rubric:: Example — Adding an induction machine to machine_parameter_sets.json

.. code-block:: json

    "LV_Induction_Machine": {
            "type": "Induction_Machine",
            "Vm_R_SI": 400,
            "Im_R_SI": 4.4,
            "fm_R_SI": 50,
            "npp": 1,
            "pf": 0.85,
            "Rs_SI": 2.7,
            "Rr_SI": 2.4,
            "Lls_SI": 9.868e-3,
            "Llr_SI": 11.777e-3,
            "Lm_SI": 394.704e-3
      }


Predefined Machine Models
-------------------------

.. _lv-induction-machine:

**Low-voltage induction machine** (``LV_Induction_Machine``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value
   * - Rated voltage
     - :math:`V_{m,R}`
     - :math:`400\,\mathrm{V}`
   * - Rated current
     - :math:`I_{m,R}`
     - :math:`4.4\,\mathrm{A}`
   * - Rated frequency
     - :math:`f_{m,R}`
     - :math:`50\,\mathrm{Hz}`
   * - Pole pairs
     - :math:`n_{pp}`
     - :math:`1`
   * - Power factor
     - :math:`\mathrm{pf}`
     - :math:`0.85`
   * - Stator resistance
     - :math:`R_s`
     - :math:`2.7\,\Omega`
   * - Rotor resistance
     - :math:`R_r`
     - :math:`2.4\,\Omega`
   * - Stator leakage inductance
     - :math:`L_{ls}`
     - :math:`9.868\,\mathrm{mH}`
   * - Rotor leakage inductance
     - :math:`L_{lr}`
     - :math:`11.777\,\mathrm{mH}`
   * - Mutual inductance
     - :math:`L_m`
     - :math:`394.704\,\mathrm{mH}`


.. _mv-induction-machine:

**Medium-voltage induction machine** (``MV_Induction_Machine``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value
   * - Rated voltage
     - :math:`V_{m,R}`
     - :math:`3300\,\mathrm{V}`
   * - Rated current
     - :math:`I_{m,R}`
     - :math:`356\,\mathrm{A}`
   * - Rated frequency
     - :math:`f_{m,R}`
     - :math:`50\,\mathrm{Hz}`
   * - Pole pairs
     - :math:`n_{pp}`
     - :math:`5`
   * - Power factor
     - :math:`\mathrm{pf}`
     - :math:`0.85`
   * - Stator resistance
     - :math:`R_s`
     - :math:`57.61\,\Omega`
   * - Rotor resistance
     - :math:`R_r`
     - :math:`48.89\,\Omega`
   * - Stator leakage inductance
     - :math:`L_{ls}`
     - :math:`2.544\,\mathrm{mH}`
   * - Rotor leakage inductance
     - :math:`L_{lr}`
     - :math:`1.881\,\mathrm{mH}`
   * - Mutual inductance
     - :math:`L_m`
     - :math:`40.01\,\mathrm{mH}`


.. _lv-pmsm:

**Low-voltage PMSM** (``LV_PMSM``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value
   * - Rated voltage
     - :math:`V_{m,R}`
     - :math:`318\,\mathrm{V}`
   * - Rated current
     - :math:`I_{m,R}`
     - :math:`138\,\mathrm{A}`
   * - Rated frequency
     - :math:`f_{m,R}`
     - :math:`120\,\mathrm{Hz}`
   * - Power factor
     - :math:`\mathrm{pf}`
     - :math:`0.86`
   * - Stator resistance
     - :math:`R_s`
     - :math:`0.046\,\Omega`
   * - Stator d-axis inductance
     - :math:`L_{sd}`
     - :math:`1.58\,\mathrm{mH}`
   * - Stator q-axis inductance
     - :math:`L_{sq}`
     - :math:`6.48\,\mathrm{mH}`
   * - Permanent magnet flux linkage
     - :math:`\lambda_{\mathrm{PM}}`
     - :math:`0.684`