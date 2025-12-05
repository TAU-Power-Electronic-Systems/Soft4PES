"""
Machine Parameter Sets for Soft4PES Examples
============================================

This module provides predefined parameter sets for machines and converters,
loaded from JSON configuration files. This separation allows easy parameter
modification and automatic documentation generation.

See Also
--------
machine_parameter_sets.json : JSON file containing all machine and converter parameter definitions
"""

import json
import os
from types import SimpleNamespace
from soft4pes import model

# Load parameter sets from JSON file
_current_dir = os.path.dirname(__file__)
_json_path = os.path.join(_current_dir, 'machine_parameter_sets.json')

with open(_json_path, 'r') as f:
    _config = json.load(f)

PARAMETER_SETS = _config['parameter_sets']


def create_base_and_converter(machine_params, converter_params):
    """
    Create base values and converter for given machine and converter parameters.

    Parameters
    ----------
    machine_params : dict
        Machine parameters including Vm_R_SI, Im_R_SI, and fm_R_SI.
    converter_params : dict
        Converter parameters including Vdc_SI and conv_nl.

    Returns
    -------
    tuple
        Base values object and converter object.
    """
    # Extract machine parameters
    Vm_R_SI = machine_params.get("Vm_R_SI")
    Im_R_SI = machine_params.get("Im_R_SI")
    fm_R_SI = machine_params.get("fm_R_SI")
    pf = machine_params.get("pf")
    npp = machine_params.get("npp")

    # Create base values
    base = model.machine.BaseMachine(Vm_R_SI=Vm_R_SI,
                                     Im_R_SI=Im_R_SI,
                                     fm_R_SI=fm_R_SI,
                                     npp=npp,
                                     pf=pf)

    # Extract converter parameters
    Vdc_SI = converter_params["Vdc_SI"]
    conv_nl = converter_params["conv_nl"]

    # Create converter
    conv = model.conv.Converter(v_dc_SI=Vdc_SI, nl=conv_nl, base=base)

    return base, conv


def create_machine_parameters(machine_params, base):
    """
    Create machine parameters object.

    Parameters
    ----------
    machine_params : dict
        Machine parameters including resistance, inductance, and other machine-specific parameters.
    base : BaseMachine
        Base values object.

    Returns
    -------
    MachineParameters
        Machine parameters object.
    """
    machine_type = machine_params.get("type", "Induction_Machine")

    if machine_type == "Induction_Machine":
        return model.machine.InductionMachineParameters(
            fs_SI=machine_params["fm_R_SI"],
            pf=machine_params["pf"],
            Rs_SI=machine_params["Rs_SI"],
            Rr_SI=machine_params["Rr_SI"],
            Lls_SI=machine_params["Lls_SI"],
            Llr_SI=machine_params["Llr_SI"],
            Lm_SI=machine_params["Lm_SI"],
            base=base)
    if machine_type == "PMSM":
        return model.machine.PMSMParameters(
            fs_SI=machine_params["fm_R_SI"],
            pf_SI=machine_params["pf"],
            Rs_SI=machine_params["Rs_SI"],
            Lsd_SI=machine_params["Lsd_SI"],
            Lsq_SI=machine_params["Lsq_SI"],
            LambdaPM_SI=machine_params["LambdaPM_SI"],
            base=base)
    raise ValueError(f"Unknown machine type: {machine_type}")


def get_custom_system(machine_name, converter_name):
    """
    Create a system based on the specified machine and converter.

    Parameters
    ----------
    machine_name : str
        Name of the machine configuration.
    converter_name : str
        Name of the converter configuration.

    Returns
    -------
    SimpleNamespace
        Object containing all system components and metadata.
    """
    # Validate inputs
    if machine_name not in _config['machines']:
        raise ValueError(
            f"Unknown machine '{machine_name}'. Available machines: {', '.join(
                _config['machines'].keys())}"
        )
    if converter_name not in _config['converters']:
        raise ValueError(
            f"Unknown converter '{converter_name}'. Available converters: {', '.join(
                _config['converters'].keys())}"
        )

    # Load components
    machine_params = _config['machines'][machine_name]
    converter_params = _config['converters'][converter_name]

    # Create base and converter
    base, conv = create_base_and_converter(machine_params, converter_params)

    # Create machine parameters
    machine_params_obj = create_machine_parameters(machine_params, base)

    # Return the system components
    return SimpleNamespace(
        name=f"{machine_name}_{converter_name}",
        base=base,
        machine_params=machine_params_obj,
        conv=conv)
        

def get_default_system(name):
    """
    Get a predefined parameter set by name.

    Parameters
    ----------
    name : str
        Name of the parameter set.

    Returns
    -------
    SimpleNamespace
        Object containing all system components and metadata.
    """
    if name not in PARAMETER_SETS:
        available = ', '.join(PARAMETER_SETS.keys())
        raise ValueError(
            f"Unknown parameter set '{name}'. Available: {available}")

    params = PARAMETER_SETS[name]
    return get_custom_system(params['machine'], params['converter'])
