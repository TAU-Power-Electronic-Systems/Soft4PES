"""Utility functions for closed-loop control with optimized pulse patterns (OPPs)."""

from pathlib import Path
import numpy as np
import xarray as xr
from soft4pes.control.common.utils import wrap_to_2pi


def read_switching_angles(angles, positions, v_ang, Tp, w, sys):
    """
    Read the switching angles that fall within the prediction horizon of the MPC controller. 

    Parameters
    ----------
    angles : 1 x d ndarray
        Array of switching angles.
    positions : 1 x d ndarray
        Switching positions corresponding to the switching angles.
    v_ang : float
        Angle of the converter voltage vector.
    Tp : float
        Length of the prediction horizon.
    w : float
        Angular frequency of the converter voltage vector.
    sys : system object
            The system model.
    Returns
    -------
    t_nom : 1 x N ndarray
        Nominal switching time instants within the prediction horizon.
    U : 3 x N ndarray
        Nominal three-phase switch positions corresponding to the nominal switching time instants.
    u_0 : 3 x 1 ndarray
        Initial three-phase switch position at the beginning of the prediction horizon.
    """

    # Parameters for reading the switching angles
    # Maximum number of switching events to consider within the prediction horizon.
    MAX_SIZE = 10

    # Threshold for angle comparison
    ANGLE_THRESHOLD = 1e-3

    # Utilize QaHWS symmetry to generate full wave switching pattern
    if sys.conv.nl == 3:
        angles_fw = np.concatenate([
            angles,
            np.pi - np.flip(angles),
            np.pi + angles,
            2 * np.pi - np.flip(angles),
        ])
        positions_fw = np.concatenate([
            positions,
            positions[-2::-1],
            np.atleast_1d(0),
            -positions[::],
            -positions[-2::-1],
            np.atleast_1d(0),
        ])
    elif sys.conv.nl == 2:
        angles_fw = np.concatenate([
            angles,
            np.pi - np.flip(angles),
            np.atleast_1d(np.pi),
            np.pi + angles,
            2 * np.pi - np.flip(angles),
            np.atleast_1d(2 * np.pi),
        ])
        positions_fw = np.concatenate([
            positions,
            -positions,
            np.atleast_1d(positions[-1]),
            -positions,
            positions,
            np.atleast_1d(-positions[-1]),
        ])
    else:
        raise ValueError('Only two- and three-level converters are supported.')

    # Phase A with zero phase shift
    angles_a = angles_fw
    positions_a = positions_fw

    # Phase B
    angles_b_wrapped = wrap_to_2pi(angles_fw + 2 * np.pi / 3)
    sort_b = np.argsort(angles_b_wrapped)
    angles_b = angles_b_wrapped[sort_b]
    positions_b = positions_fw[sort_b]

    # Phase C
    angles_c_wrapped = wrap_to_2pi(angles_fw + 4 * np.pi / 3)
    sort_c = np.argsort(angles_c_wrapped)
    angles_c = angles_c_wrapped[sort_c]
    positions_c = positions_fw[sort_c]

    # Combine into 3-phase matrices
    pattern_3p = np.vstack([positions_a, positions_b, positions_c])
    angles_3p = np.vstack([angles_a, angles_b, angles_c])

    # Add a second period to ensure that all angles within the prediction horizon are captured
    pattern_3p = np.concatenate([pattern_3p, pattern_3p], axis=1)
    angles_3p = np.concatenate([angles_3p, angles_3p + 2 * np.pi], axis=1)

    # Add pi/2 to align the converter voltage with the OPP
    v_ang = wrap_to_2pi(v_ang + np.pi / 2)

    # Angle of the end of Tp
    TpAngle = Tp * w * sys.base.w + v_ang

    # Get angles that fall inbetween v_ang and Tp
    ind0 = angles_3p >= v_ang - ANGLE_THRESHOLD
    indTp = angles_3p < TpAngle
    valid_mask = ind0 & indTp

    # Create a mask of the valid angles
    delta_angs = np.where(valid_mask, angles_3p - v_ang, np.inf)

    # Extract initial switch position (u_0)
    shifted_ind0 = np.roll(ind0, -1, axis=1)
    diff_ind0 = shifted_ind0 & ~ind0
    u_0 = np.zeros(3)
    for phase in range(3):
        # Check what the last valid index is for this phase
        if np.any(diff_ind0[phase]):
            u_0[phase] = pattern_3p[phase, diff_ind0[phase]][0]
        else:
            # If no valid index is found, use the last value in the pattern,
            # i.e, the first value of the next period
            u_0[phase] = pattern_3p[phase, -1]

    # Get the row and column indices of the valid angles
    phase_rows, angle_cols = np.where(valid_mask)

    # Get the angles and their corresponding pattern values
    valid_angles = delta_angs[phase_rows, angle_cols]
    valid_patterns = pattern_3p[phase_rows, angle_cols]

    # Sort everything by angle ascension
    sort_idx = np.argsort(valid_angles)
    sorted_phases = phase_rows[sort_idx]
    sorted_patterns = valid_patterns[sort_idx]
    sorted_angles = valid_angles[sort_idx]

    # Number of valid angles within the prediction horizon
    n_valid = len(sorted_angles)

    # Sorted angles within the prediction horizon
    t_nom = np.inf * np.ones(MAX_SIZE)
    n_fill = min(n_valid, MAX_SIZE)
    t_nom_full = sorted_angles / sys.base.w / w
    t_nom[:n_fill] = t_nom_full[:n_fill]

    # Initialize U to a fixed size
    U = np.zeros((3, MAX_SIZE))

    # Initialize the current switch position to the initial switch position
    current_u = u_0.copy()

    # Go through the sorted angles and update the switch positions accordingly
    for i in range(n_valid):
        switching_phase = sorted_phases[i]
        current_u[switching_phase] = sorted_patterns[i]

        # Only write to U if we haven't exceeded our fixed array size
        if i < MAX_SIZE:
            U[:, i] = current_u

    # If n_valid was shorter than MAX_SIZE, pad the rest of U with the last valid state
    if n_valid < MAX_SIZE:
        U[:, n_valid:] = current_u.reshape(3, 1)

    return t_nom, U, u_0


def load_switching_angles(d, sys):
    """
    Load the switching angles and positions from a file.

    Parameters
    ----------
    d : int 
        pulse number
    sys : system object
        The system model.

    Returns
    -------
    opp_lut : xarray.Dataset
        The loaded switching angles and positions.
    """

    BASE_PATH = Path.cwd()
    TARGET_PATH = BASE_PATH / 'examples' / 'data'

    try:
        opp_lut = xr.open_dataset(
            TARGET_PATH /
            (str(sys.conv.nl) + 'L_' + 'd' + str(d) + '_opp_inductive.nc'))
    except FileNotFoundError as exc:
        raise FileNotFoundError('Data for ' + str(sys.conv.nl) + 'L_d' +
                                str(d) + '_opp_inductive.nc' +
                                ' not found.') from exc

    return opp_lut
