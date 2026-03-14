Grid Systems
============

.. _grid-systems:
 
The following example shows how to utilize the predefined systems. The available systems are listed after the examples.  

.. rubric:: Example — Using a predefined grid system

.. code-block:: python

   from pars.grid_config import get_default_system

   config = get_default_system(name='Weak_LV_Grid_LCL_Filter_2L_conv')

The user can also create custom grid systems by combining individual components in ``examples/grid/pars/grid_parameter_sets.json``, under ``parameter_sets`` as shown below

.. rubric:: Example — Creating a grid system from components

.. code-block:: json

    "Weak_LV_Grid_LCL_Filter_2L_conv": {
      "description": [
          "2-level converter connected to a weak low voltage grid via an LCL filter"
      ],
      "grid": "Weak_LV_Grid",
      "filter": "LCL_Filter_fr_1300",
      "converter": "2L_LV_Converter"
    }

The components are defined in the same file, and predefined components can be found in the :ref:`components section <grid-components>`.

Predefined Grid Systems
-----------------------

**2-level converter connected to a weak low-voltage grid via an** :math:`\textrm{LCL}` **filter**

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Component
     - Link
     - Details
   * - Grid
     - :ref:`Weak low-voltage grid <weak-lv-grid>`
     - :math:`V_R = 400\,\textrm{V}`, :math:`I_R = 18\,\textrm{A}`
   * - Filter
     - :ref:`LCL filter <lcl-filter-1300>`
     - :math:`f_R = 1300\,\textrm{Hz}`
   * - Converter
     - :ref:`2-Level converter <2l-lv-converter>`
     - :math:`V_{\textrm{dc}} = 750\,\textrm{V}`


**2-level converter connected to a strong low-voltage grid via an** :math:`\textrm{LCL}` **filter**

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Component
     - Link
     - Details
   * - Grid
     - :ref:`Strong low-voltage grid <strong-lv-grid>`
     - :math:`V_R = 400\,\textrm{V}`, :math:`I_R = 18\,\textrm{A}`
   * - Filter
     - :ref:`LCL filter <lcl-filter-1300>`
     - :math:`f_R = 1300\,\textrm{Hz}`
   * - Converter
     - :ref:`2-Level converter <2l-lv-converter>`
     - :math:`V_{\textrm{dc}} = 750\,\textrm{V}`

**3-level converter connected to a strong medium-voltage grid via an** :math:`\mathrm{L}` **filter**

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Component
     - Link
     - Details
   * - Grid
     - :ref:`Strong medium-voltage grid <strong-mv-grid>`
     - :math:`V_R = 3300\,\textrm{V}`, :math:`I_R = 1575\,\textrm{A}`
   * - Filter
     - :ref:`L filter <l-filter-mv>`
     - :math:`L_{\mathrm{fc}} = 0.19\,\mathrm{mH}`, :math:`R_{\mathrm{fc}} = 0.5\,\mathrm{m}\Omega`
   * - Converter
     - :ref:`3-Level converter <3l-mv-converter>`
     - :math:`V_{\textrm{dc}} = 5200\,\textrm{V}`


**3-level converter connected to a strong medium-voltage grid via an** :math:`\textrm{LCL}` **filter**

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Component
     - Link
     - Details
   * - Grid
     - :ref:`Strong medium-voltage grid <strong-mv-grid>`
     - :math:`V_R = 3300\,\textrm{V}`, :math:`I_R = 1575\,\textrm{A}`
   * - Filter
     - :ref:`LCL filter <lcl-filter-380>`
     - :math:`f_R = 380\,\textrm{Hz}`
   * - Converter
     - :ref:`3-Level converter <3l-mv-converter>`
     - :math:`V_{\textrm{dc}} = 5200\,\textrm{V}`