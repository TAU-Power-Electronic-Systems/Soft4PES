import numpy as np
from soft4pes.control.common.controller import Controller


class MTPALookupTable(Controller):
    """
    Maximum Torque Per Ampere (MTPA) lookup table for permanent magnet synchronous machines (PMSM).
    
    This class generates and manages the MTPA trajectory, providing optimal current references for 
    given torque demands.
    """

    def __init__(self, par, iS_mag_points=101, theta_points=2001):
        """
        Initialize MTPA lookup table.
        
        Parameters
        ----------
        par : PMSMParameters
            Machine parameters.
        iS_mag_points : int, optional
            Number of stator current magnitude points for trajectory generation. Default is 101.
        theta_points : int, optional
            Number of current vector angle points for trajectory generation. Default is 2001.
        """
        super().__init__()
        self.par = par
        self.iS_mag_points = iS_mag_points
        self.theta_points = theta_points
        self.torque_grid = None
        self.current_grid = None
        self.generate_mtpa_trajectory()

    def generate_mtpa_trajectory(self):
        """
        Generate the maximum torque per ampere (MTPA) trajectory for both positive and negative 
        torque.
        
        The algorithm sweeps current magnitude from 0 to 1 p.u. and for each magnitude finds the
        current vector orientations that produce maximum positive and negative torque. Results are
        stored as sorted arrays for efficient interpolation.
        
        Creates
        -------
        self.torque_grid : ndarray
            Sorted array of achievable torque values [p.u.].
        self.current_grid : ndarray
            Array of optimal current vectors [id, iq] corresponding to torque_grid [p.u.].
        """
        iS_mag_range = np.linspace(0, 1, self.iS_mag_points)
        theta_range = np.linspace(-np.pi / 2, np.pi / 2, self.theta_points)

        torques = []
        currents = []

        for iS_mag in iS_mag_range:
            # Skip zero current magnitude (produces only zero torque)
            if iS_mag == 0:
                continue

            id_trajectory = -iS_mag * np.cos(theta_range)
            iq_trajectory = iS_mag * np.sin(theta_range)

            # Calculate torque for each angle
            Te_line = iq_trajectory * (
                (self.par.Xsd - self.par.Xsq) * id_trajectory + self.par.PsiPM)

            # Find maximum positive torque
            max_pos_index = np.argmax(Te_line)
            max_pos_torque = Te_line[max_pos_index]

            # Find maximum negative torque
            min_neg_index = np.argmin(Te_line)
            min_neg_torque = Te_line[min_neg_index]

            # Store positive optimal point
            if max_pos_torque > 0:
                torques.append(max_pos_torque)
                currents.append([
                    id_trajectory[max_pos_index], iq_trajectory[max_pos_index]
                ])

            # Store negative optimal point
            if min_neg_torque < 0:
                torques.append(min_neg_torque)
                currents.append([
                    id_trajectory[min_neg_index], iq_trajectory[min_neg_index]
                ])

        # Add explicit zero torque point
        torques.append(0.0)
        currents.append([0.0, 0.0])

        # Sort by torque and store as arrays
        sorted_indices = np.argsort(torques)
        self.torque_grid = np.array(torques)[sorted_indices]
        self.current_grid = np.array(currents)[sorted_indices]

    def get_optimal_current(self, Te_ref):
        """
        Get optimal stator current reference for given torque reference using linear interpolation.
        
        Parameters
        ----------
        Te_ref : float
            Torque reference [p.u.].
     
        Returns
        -------
        ndarray
            Optimal stator current reference [p.u.].
        """

        # Linear interpolation for better coverage
        id_ref = np.interp(Te_ref, self.torque_grid, self.current_grid[:, 0])
        iq_ref = np.interp(Te_ref, self.torque_grid, self.current_grid[:, 1])
        return np.array([id_ref, iq_ref])

    def execute(self, sys, kTs):
        """
        Execute MTPA lookup.

        Returns
        -------
        1 x 2 ndarray of floats
            Optimal stator current reference [p.u.].
        """
        Te_ref = self.input.T_ref
        iS_ref_dq = self.get_optimal_current(Te_ref)
        self.output.iS_ref_dq = iS_ref_dq
        return self.output
