"""Utility functions for modulation"""

from pathlib import Path
import numpy as np
import xarray as xr
from soft4pes.control.common.utils import wrap_theta


def get_opp_switching_instants(angles, positions, v_ang, T_end, w, sys):
    """
    Read the switching angles of a QaHWS OPP that fall within the time window [0, T_end). 

    Parameters
    ----------
    angles : 1 x d ndarray
        Array of switching angles [rad].
    positions : 1 x d ndarray
        Switching positions corresponding to the switching angles.
    v_ang : float
        Angle of the converter voltage reference vector [rad].
    T_end : float
        End time of the time window [s]. The time window is defined as [0, T_end).
    w : float
        Angular frequency of the converter voltage reference vector [p.u.].
    sys : system object
        The system model.
    Returns
    -------
    t : 1 x N ndarray 
        Switching time instants within the time window [0, T_end) [s].
    U : 3 x N ndarray
        Three-phase switch positions corresponding to the switching time instants.
    u0 : 3 x 1 ndarray
        Initial three-phase switch position at the beginning of the time window [0, T_end).
    """

    # Utilize QaHWS symmetry to generate the full-wave switching pattern
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

    ANGLE_TOL = 20e-3  # Tolerance for angle comparison

    # Phase A with zero phase shift
    angles_a = angles_fw
    positions_a = positions_fw

    # Phase B
    angles_b_wrapped = wrap_theta(angles_fw + 2 * np.pi / 3 - np.pi) + np.pi
    sort_b = np.argsort(angles_b_wrapped)
    angles_b = angles_b_wrapped[sort_b]
    positions_b = positions_fw[sort_b]

    # Phase C
    angles_c_wrapped = wrap_theta(angles_fw + 4 * np.pi / 3 - np.pi) + np.pi
    sort_c = np.argsort(angles_c_wrapped)
    angles_c = angles_c_wrapped[sort_c]
    positions_c = positions_fw[sort_c]

    # Combine into 3-phase matrices
    pattern_abc = np.vstack([positions_a, positions_b, positions_c])
    angles_abc = np.vstack([angles_a, angles_b, angles_c])

    # Add a second period to ensure that all angles within the prediction horizon are captured
    pattern_abc = np.concatenate([pattern_abc, pattern_abc], axis=1)
    angles_abc = np.concatenate([angles_abc, angles_abc + 2 * np.pi], axis=1)

    # Add pi/2 to align the converter voltage with the OPP
    v_ang = wrap_theta(v_ang + np.pi / 2 - np.pi) + np.pi

    # Angle of the end of the prediction horizon
    theta_end = T_end * w * sys.base.w + v_ang

    # Get angles that fall between v_ang and theta_end
    ind_0 = angles_abc >= v_ang - ANGLE_TOL
    ind_theta_end = angles_abc < theta_end
    valid_mask = ind_0 & ind_theta_end

    # Create a mask of the valid angles
    delta_angs = np.where(valid_mask, angles_abc - v_ang, np.inf)

    # Extract initial switch position (u0)
    shifted_ind_0 = np.roll(ind_0, -1, axis=1)
    diff_ind_0 = shifted_ind_0 & ~ind_0
    u0 = np.zeros(3)
    for phase in range(3):
        # Check what the last valid index is for this phase
        if np.any(diff_ind_0[phase]):
            u0[phase] = pattern_abc[phase, diff_ind_0[phase]][0]
        else:
            # If no valid index is found, use the last value in the pattern,
            # i.e, the first value of the next period
            u0[phase] = pattern_abc[phase, -1]

    # Get the row and column indices of the valid angles
    phase_rows, angle_cols = np.where(valid_mask)

    # Get the angles and their corresponding pattern values
    valid_angles = delta_angs[phase_rows, angle_cols]
    valid_patterns = pattern_abc[phase_rows, angle_cols]

    # Sort everything by angle ascension
    sort_idx = np.argsort(valid_angles)
    sorted_phases = phase_rows[sort_idx]
    sorted_patterns = valid_patterns[sort_idx]
    sorted_angles = valid_angles[sort_idx]

    # Number of valid angles within the prediction horizon
    n_valid = len(sorted_angles)

    # Sorted angles within the prediction horizon
    t = sorted_angles / sys.base.w / w

    # Initialize U
    U = np.zeros((3, n_valid))

    # Initialize the current switch position to the initial switch position
    current_u = u0.copy()

    # Go through the sorted angles and update the switch positions accordingly
    for i in range(n_valid):
        switching_phase = sorted_phases[i]
        current_u[switching_phase] = sorted_patterns[i]
        U[:, i] = current_u

    return t, U


def load_switching_angles_from_file(filename):
    """
    Load the switching angles and positions from a file.

    Parameters
    ----------
    filename : str
        The name of the file to load.
    sys : system object
        The system model.

    Returns
    -------
    opp_lut : xarray.Dataset
        The loaded switching angles and positions.
    """

    BASE_PATH = Path.cwd()
    TARGET_PATH = BASE_PATH / 'examples' / 'opp_data'

    try:
        opp_lut = xr.open_dataset(TARGET_PATH / filename)
    except FileNotFoundError as exc:
        raise FileNotFoundError('Data for ' + filename +
                                ' not found.') from exc

    return opp_lut
