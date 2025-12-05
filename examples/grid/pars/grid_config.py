"""
Grid Parameter Sets for Soft4PES Examples
==========================================

This module provides predefined parameter sets for common grid configurations
loaded from JSON configuration files. This separation allows easy parameter
modification and automatic documentation generation.

See Also
--------
grid_parameter_sets.json : JSON file containing all parameter definitions
"""

import json
import os
from types import SimpleNamespace
from soft4pes import model

# Load parameter sets from JSON file
_current_dir = os.path.dirname(__file__)
_json_path = os.path.join(_current_dir, 'grid_parameter_sets.json')

with open(_json_path, 'r') as f:
    _config = json.load(f)

PARAMETER_SETS = _config['parameter_sets']


def create_base_and_converter(grid_params, converter_params):
    """
    Create base values and converter for given grid and converter parameters.

    Parameters
    ----------
    grid_params : dict
        Grid parameters including Vg_R_SI, Ig_R_SI, and fg_R_SI.
    converter_params : dict
        Converter parameters including Vdc_SI and conv_nl.

    Returns
    -------
    tuple
        Base values object and converter object.
    """
    # Extract grid parameters
    Vg_R_SI = grid_params.get("Vg_R_SI")
    Ig_R_SI = grid_params.get("Ig_R_SI")
    fg_R_SI = grid_params.get("fg_R_SI")

    # Create base values
    base = model.grid.BaseGrid(Vg_R_SI=Vg_R_SI,
                               Ig_R_SI=Ig_R_SI,
                               fg_R_SI=fg_R_SI)

    # Extract converter parameters
    Vdc_SI = converter_params["Vdc_SI"]
    conv_nl = converter_params["conv_nl"]

    # Create converter
    conv = model.conv.Converter(v_dc_SI=Vdc_SI, nl=conv_nl, base=base)

    return base, conv


def create_grid_parameters(grid_params, base):
    """
    Create grid parameters object.

    Parameters
    ----------
    grid_params : dict
        Grid parameters including Rg_SI and Lg_SI.
    base : BaseGrid
        Base values object.

    Returns
    -------
    RLGridParameters
        Grid parameters object.
    """
    return model.grid.RLGridParameters(Vg_SI=grid_params["Vg_R_SI"],
                                       fg_SI=grid_params["fg_R_SI"],
                                       Rg_SI=grid_params["Rg_SI"],
                                       Lg_SI=grid_params["Lg_SI"],
                                       base=base)


def create_system(grid_params, filter_params, conv, base):
    """
    Create the system model based on the presence of a filter.

    Parameters
    ----------
    grid_params : RLGridParameters
        Grid parameters object.
    filter_params : dict or None
        Filter parameters, or None if no filter is used.
    conv : Converter
        Converter object.
    base : BaseGrid
        Base values object.

    Returns
    -------
    tuple
        System object and optional filter parameters.
    """
    if filter_params:  # If a filter is defined
        lcl_params = model.grid.LCLFilterParameters(**filter_params, base=base)
        sys = model.grid.RLGridLCLFilter(grid_params, lcl_params, conv, base)
        return sys, lcl_params
    
    sys = model.grid.RLGrid(grid_params, conv, base)
    return sys, None


def get_custom_system(grid_name, filter_name, converter_name):
    """
    Create a system based on the specified grid, filter, and converter.

    Parameters
    ----------
    grid_name : str
        Name of the grid configuration.
    filter_name : str
        Name of the filter configuration.
    converter_name : str
        Name of the converter configuration.

    Returns
    -------
    SimpleNamespace
        Object containing all system components and metadata.
    """
    # Validate inputs
    if grid_name not in _config['grids']:
        raise ValueError(
            f"Unknown grid '{grid_name}'. Available grids: {', '.join(_config['grids'].keys())}"
        )
    if filter_name not in _config['filters']:
        raise ValueError(
            f"Unknown filter '{filter_name}'. Available filters: {', '.join(
                _config['filters'].keys())}"
        )
    if converter_name not in _config['converters']:
        raise ValueError(
            f"Unknown converter '{converter_name}'. Available converters: {', '.join(
                _config['converters'].keys())}"
        )

    # Load components
    grid_params = _config['grids'][grid_name]
    filter_params = _config['filters'][filter_name]
    converter_params = _config['converters'][converter_name]

    # Create base and converter
    base, conv = create_base_and_converter(grid_params, converter_params)

    # Create grid parameters
    grid_params_obj = create_grid_parameters(grid_params, base)

    # Create the system
    sys, lcl_params = create_system(grid_params_obj, filter_params, conv, base)

    # Return the system components
    return SimpleNamespace(
        name=f"{grid_name}_{filter_name}_{converter_name}",
        base=base,
        grid_params=grid_params_obj,
        conv=conv,
        lcl_params=lcl_params,
        sys=sys)


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
        Object containing all system components.
    """
    if name not in PARAMETER_SETS:
        available = ', '.join(PARAMETER_SETS.keys())
        raise ValueError(
            f"Unknown parameter set '{name}'. Available: {available}")

    params = PARAMETER_SETS[name]
    return get_custom_system(params['grid'], params['filter'],
                             params['converter'])
