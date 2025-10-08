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


def create_base_and_converter(Vg_R_SI, Ig_R_SI, fg_R_SI, Vdc_SI, conv_nl):
    """Create base values and converter for given ratings."""
    base = model.grid.BaseGrid(Vg_R_SI=Vg_R_SI,
                               Ig_R_SI=Ig_R_SI,
                               fg_R_SI=fg_R_SI)
    conv = model.conv.Converter(v_dc_SI=Vdc_SI, nl=conv_nl, base=base)
    return base, conv


def get_parameter_set(name):
    """
    Get a complete parameter set by name.
    
    This function loads parameters from the JSON configuration file and creates
    a fully configured system ready for simulation.
    
    Parameters
    ----------
    name : str
        Name of the parameter set. Available options can be listed using
        :func:`list_available_sets`.
        
    Returns
    -------
    SimpleNamespace
        Object containing all system components and metadata.
        
    Examples
    --------
    >>> config = get_parameter_set('weak_LV_grid_LCL')
    >>> sys = config.sys
    >>> print(config.specifications['grid_voltage'])
    400V (line-to-line RMS)
    """
    if name not in PARAMETER_SETS:
        available = ', '.join(PARAMETER_SETS.keys())
        raise ValueError(
            f"Unknown parameter set '{name}'. Available: {available}")

    params = PARAMETER_SETS[name]

    # Create base and converter
    base, conv = create_base_and_converter(**params['ratings'])

    # Create grid parameters
    grid_params = model.grid.RLGridParameters(
        Vg_SI=params['ratings']['Vg_R_SI'],
        fg_SI=params['ratings']['fg_R_SI'],
        **params['grid'],
        base=base)

    # Create the appropriate system based on system_type
    system_type = params['system_type']

    result = SimpleNamespace(
        name=name,
        description=params['description'],
        system_type=system_type,
        specifications=params.get('specifications', {}),
        base=base,
        grid_params=grid_params,
        conv=conv,
    )

    if system_type == 'RLGrid':
        sys = model.grid.RLGrid(grid_params, conv, base)
        result.sys = sys
    elif system_type == 'RLGridLCLFilter':
        lcl_params = model.grid.LCLFilterParameters(**params['lcl_filter'],
                                                    base=base)
        sys = model.grid.RLGridLCLFilter(grid_params, lcl_params, conv, base)
        result.lcl_params = lcl_params
        result.sys = sys
    else:
        raise ValueError(f"Unknown system type: {system_type}")

    return result
