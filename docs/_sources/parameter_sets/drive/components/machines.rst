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
     - :math:`400\,\textrm{V}`
     - 
   * - Rated current
     - :math:`I_{m,R}`
     - :math:`4.4\,\textrm{A}`
     - 
   * - Rated power
     - :math:`P_{m,R}`
     - :math:`3\,\textrm{kW}`
     - 
   * - Rated frequency
     - :math:`f_{m,R}`
     - :math:`50\,\textrm{Hz}`
     - 
   * - Pole pairs
     - :math:`n_{pp}`
     - :math:`1`
     - 
   * - Power factor
     - :math:`\textrm{pf}`
     - :math:`0.85`
     - 
   * - Stator resistance
     - :math:`R_s`
     - :math:`2.7\,\Omega`
     - :math:`0.05\,\textrm{p.u.}`
   * - Rotor resistance
     - :math:`R_r`
     - :math:`2.4\,\Omega`
     - :math:`0.05\,\textrm{p.u.}`
   * - Stator leakage inductance
     - :math:`L_{ls}`
     - :math:`9.868\,\textrm{mH}`
     - :math:`0.06\,\textrm{p.u.}`
   * - Rotor leakage inductance
     - :math:`L_{lr}`
     - :math:`11.777\,\textrm{mH}`
     - :math:`0.07\,\textrm{p.u.}`
   * - Mutual inductance
     - :math:`L_m`
     - :math:`394.704\,\textrm{mH}`
     - :math:`2.36\,\textrm{p.u.}`


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
     - :math:`3300\,\textrm{V}`
     - 
   * - Rated current
     - :math:`I_{m,R}`
     - :math:`356\,\textrm{A}`
     - 
   * - Rated power
     - :math:`P_{m,R}`
     - :math:`2\,\textrm{MW}`
     - 
   * - Rated frequency
     - :math:`f_{m,R}`
     - :math:`50\,\textrm{Hz}`
     - 
   * - Pole pairs
     - :math:`n_{pp}`
     - :math:`5`
     - 
   * - Power factor
     - :math:`\textrm{pf}`
     - :math:`0.85`
     - 
   * - Stator resistance
     - :math:`R_s`
     - :math:`57.61\,\Omega`
     - :math:`10.71\,\textrm{p.u.}`
   * - Rotor resistance
     - :math:`R_r`
     - :math:`48.89\,\Omega`
     - :math:`9.14\,\textrm{p.u.}`
   * - Stator leakage inductance
     - :math:`L_{ls}`
     - :math:`2.544\,\textrm{mH}`
     - :math:`0.15\,\textrm{p.u.}`
   * - Rotor leakage inductance
     - :math:`L_{lr}`
     - :math:`1.881\,\textrm{mH}`
     - :math:`0.11\,\textrm{p.u.}`
   * - Mutual inductance
     - :math:`L_m`
     - :math:`40.01\,\textrm{mH}`
     - :math:`2.35\,\textrm{p.u.}`


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
     - :math:`274\,\textrm{V}`
     - 
   * - Rated current
     - :math:`I_{m,R}`
     - :math:`71\,\textrm{A}`
     - 
   * - Rated power
     - :math:`P_{m,R}`
     - :math:`33.7\,\textrm{kW}`
     - 
   * - Rated frequency
     - :math:`f_{m,R}`
     - :math:`50\,\textrm{Hz}`
     - 
   * - Pole pairs
     - :math:`n_{pp}`
     - :math:`4`
     - 
   * - Power factor
     - :math:`\textrm{pf}`
     - :math:`1`
     - 
   * - Stator resistance
     - :math:`R_s`
     - :math:`0.3\,\Omega`
     - :math:`0.13\,\textrm{p.u.}`
   * - Stator d-axis inductance
     - :math:`L_{sd}`
     - :math:`4\,\textrm{mH}`
     - :math:`0.56\,\textrm{p.u.}`
   * - Stator q-axis inductance
     - :math:`L_{sq}`
     - :math:`5.5\,\textrm{mH}`
     - :math:`0.78\,\textrm{p.u.}`
   * - Permanent magnet flux linkage
     - :math:`\lambda_{\textrm{PM}}`
     - :math:`0.7\,\textrm{Wb}`
     - :math:`0.98\,\textrm{p.u.}`