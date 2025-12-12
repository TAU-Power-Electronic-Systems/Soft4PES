Machines
========

The predefined machine models are presented after the example. 

In order to create a custom machine, a new entry can be added to ``examples/machine/pars/machine_parameter_sets.json`` under ``machines`` following the structure of the existing ones. Required parameters are an unique name for the machine model, machine class, and machine specific parameters. Note that the rated voltage is the line-to-line rms voltage and the rated current is the rms current.

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
   :widths: 40 20 20 20
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value [SI]
     - Value [pu]
   * - Rated voltage
     - :math:`V_{m,R}`
     - :math:`400\,\text{V}`
     - 
   * - Rated current
     - :math:`I_{m,R}`
     - :math:`4.4\,\text{A}`
     - 
   * - Rated power
     - :math:`P_{m,R}`
     - :math:`3\,\text{kW}`
     - 
   * - Rated frequency
     - :math:`f_{m,R}`
     - :math:`50\,\text{Hz}`
     - 
   * - Pole pairs
     - :math:`n_{pp}`
     - :math:`1`
     - 
   * - Power factor
     - :math:`\mathrm{pf}`
     - :math:`0.85`
     - 
   * - Stator resistance
     - :math:`R_s`
     - :math:`2.7\,\Omega`
     - :math:`0.05\,\text{p.u.}`
   * - Rotor resistance
     - :math:`R_r`
     - :math:`2.4\,\Omega`
     - :math:`0.05\,\text{p.u.}`
   * - Stator leakage inductance
     - :math:`L_{ls}`
     - :math:`9.868\,\text{mH}`
     - :math:`0.06\,\text{p.u.}`
   * - Rotor leakage inductance
     - :math:`L_{lr}`
     - :math:`11.777\,\text{mH}`
     - :math:`0.07\,\text{p.u.}`
   * - Mutual inductance
     - :math:`L_m`
     - :math:`394.704\,\text{mH}`
     - :math:`2.36\,\text{p.u.}`


.. _mv-induction-machine:

**Medium-voltage induction machine** (``MV_Induction_Machine``)

.. list-table::
   :widths: 40 20 20 20
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value [SI]
     - Value [pu]
   * - Rated voltage
     - :math:`V_{m,R}`
     - :math:`3300\,\text{V}`
     - 
   * - Rated current
     - :math:`I_{m,R}`
     - :math:`356\,\text{A}`
     - 
   * - Rated power
     - :math:`P_{m,R}`
     - :math:`2\,\text{MW}`
     - 
   * - Rated frequency
     - :math:`f_{m,R}`
     - :math:`50\,\text{Hz}`
     - 
   * - Pole pairs
     - :math:`n_{pp}`
     - :math:`5`
     - 
   * - Power factor
     - :math:`\mathrm{pf}`
     - :math:`0.85`
     - 
   * - Stator resistance
     - :math:`R_s`
     - :math:`57.61\,\Omega`
     - :math:`10.71\,\text{p.u.}`
   * - Rotor resistance
     - :math:`R_r`
     - :math:`48.89\,\Omega`
     - :math:`9.14\,\text{p.u.}`
   * - Stator leakage inductance
     - :math:`L_{ls}`
     - :math:`2.544\,\text{mH}`
     - :math:`0.15\,\text{p.u.}`
   * - Rotor leakage inductance
     - :math:`L_{lr}`
     - :math:`1.881\,\text{mH}`
     - :math:`0.11\,\text{p.u.}`
   * - Mutual inductance
     - :math:`L_m`
     - :math:`40.01\,\text{mH}`
     - :math:`2.35\,\text{p.u.}`


.. _lv-pmsm:

**Low-voltage PMSM** (``LV_PMSM``)

.. list-table::
   :widths: 40 20 20 20
   :header-rows: 1

   * - Parameter
     - Symbol
     - Value [SI]
     - Value [pu]
   * - Rated voltage
     - :math:`V_{m,R}`
     - :math:`274\,\text{V}`
     - 
   * - Rated current
     - :math:`I_{m,R}`
     - :math:`71\,\text{A}`
     - 
   * - Rated power
     - :math:`P_{m,R}`
     - :math:`33.7\,\text{kW}`
     - 
   * - Rated frequency
     - :math:`f_{m,R}`
     - :math:`50\,\text{Hz}`
     - 
   * - Pole pairs
     - :math:`n_{pp}`
     - :math:`4`
     - 
   * - Power factor
     - :math:`\mathrm{pf}`
     - :math:`1`
     - 
   * - Stator resistance
     - :math:`R_s`
     - :math:`0.3\,\Omega`
     - :math:`0.13\,\text{p.u.}`
   * - Stator d-axis inductance
     - :math:`L_{sd}`
     - :math:`4\,\text{mH}`
     - :math:`0.56\,\text{p.u.}`
   * - Stator q-axis inductance
     - :math:`L_{sq}`
     - :math:`5.5\,\text{mH}`
     - :math:`0.78\,\text{p.u.}`
   * - Permanent magnet flux linkage
     - :math:`\lambda_{\mathrm{PM}}`
     - :math:`0.7\,\text{Wb}`
     - :math:`0.98\,\text{p.u.}`