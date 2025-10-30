Drive Systems
===============

.. _drive-systems:

The following example shows how to utilize the predefined systems. The available systems are listed after the examples.

.. rubric:: Example — Using a predefined drive system

.. code-block:: python

    from pars.machine_config import get_default_system

    config = get_default_system("LV_PMSM_2L_Converter")

The user can also create custom drive systems by combining individual components in ``examples/machine/pars/machine_parameter_sets.json``, under ``parameter_sets`` as shown below

.. code-block:: json

    "LV_Induction_Machine_2L_Converter": {
      "machine": "LV_Induction_Machine",
      "converter": "2L_LV_Converter"
    }

Predefined Drive Systems
--------------------------

**2-level converter connected to a low-voltage induction machine** (``LV_Induction_Machine_2L_Converter``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Component
     - Link
     - Details
   * - Machine
     - :ref:`Low-voltage induction machine <lv-induction-machine>`
     - :math:`V_{m,R} = 400\,\mathrm{V}`, :math:`I_{m,R} = 4.4\,\mathrm{A}`  
       :math:`f_{m,R} = 50\,\mathrm{Hz}`
   * - Converter
     - :ref:`2-Level low-voltage converter <2l-lv-converter>`
     - :math:`V_{\mathrm{dc}} = 980\,\mathrm{V}`


**3-level converter connected to a medium-voltage induction machine** (``MV_Induction_Machine_3L_Converter``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Component
     - Link
     - Details
   * - Machine
     - :ref:`Medium-voltage induction machine <mv-induction-machine>`
     - :math:`V_{m,R} = 3300\,\mathrm{V}`, :math:`I_{m,R} = 356\,\mathrm{A}`  
       :math:`f_{m,R} = 50\,\mathrm{Hz}`
   * - Converter
     - :ref:`3-Level medium-voltage converter <3l-mv-converter>`
     - :math:`V_{\mathrm{dc}} = 5200\,\mathrm{V}`


**2-level converter connected to a low-voltage PMSM** (``LV_PMSM_2L_Converter``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Component
     - Link
     - Details
   * - Machine
     - :ref:`Low-voltage PMSM <lv-pmsm>`
     - :math:`V_{m,R} = 318\,\mathrm{V}`, :math:`I_{m,R} = 138\,\mathrm{A}`  
       :math:`f_{m,R} = 120\,\mathrm{Hz}`
   * - Converter
     - :ref:`2-Level low-voltage converter <2l-lv-converter>`
     - :math:`V_{\mathrm{dc}} = 980\,\mathrm{V}`


**3-level converter connected to a low-voltage PMSM** (``LV_PMSM_3L_Converter``)

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Component
     - Link
     - Details
   * - Machine
     - :ref:`Low-voltage PMSM <lv-pmsm>`
     - :math:`V_{m,R} = 318\,\mathrm{V}`, :math:`I_{m,R} = 138\,\mathrm{A}`  
       :math:`f_{m,R} = 120\,\mathrm{Hz}`
   * - Converter
     - :ref:`3-Level low-voltage converter <3l-lv-converter>`
     - :math:`V_{\mathrm{dc}} = 980\,\mathrm{V}`