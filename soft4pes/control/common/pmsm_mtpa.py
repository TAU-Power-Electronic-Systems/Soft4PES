import numpy as np
from soft4pes.control.common.controller import Controller


class MTPALookupTable(Controller):
    """
    Maximum Torque Per Ampere (MTPA) lookup table for permanent magnet synchronous machines (PMSM).
    
    This class generates and manages the MTPA trajectory, providing optimal
    current references for given torque demands.
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
            Number of angle points for trajectory generation. Default is 2001.
        """
        super().__init__()
        self.par = par
        self.iS_mag_points = iS_mag_points
        self.theta_points = theta_points
        self.mtpa_lut = {}  # Dictionary: {torque: iS_dq}
        self.generate_mtpa_trajectory()

    def generate_mtpa_trajectory(self):
        """
        Generate the maximum torque per ampere (MTPA) trajectory.
        
        Creates a lookup table mapping torque values to optimal stator current references.
        """

        iS_mag_range = np.linspace(0, 1, self.iS_mag_points)
        theta_range = np.linspace(0, np.pi / 2, self.theta_points)

        for iS_mag in iS_mag_range:
            id_trajectory = -iS_mag * np.cos(theta_range)
            iq_trajectory = iS_mag * np.sin(theta_range)

            # Calculate torque map for this current magnitude
            Te_map = np.dot(
                iq_trajectory.reshape(-1, 1),
                (self.par.Xsd - self.par.Xsq) * id_trajectory.reshape(1, -1) +
                self.par.PsiPM)

            # Extract diagonal (optimal torque for each angle)
            Te_line = [Te_map[kk, kk] for kk in range(theta_range.size)]

            # Find maximum torque and corresponding currents
            max_index = np.argmax(Te_line)
            optimal_torque = Te_line[max_index]
            optimal_iS_dq = np.array(
                [id_trajectory[max_index], iq_trajectory[max_index]])

            # Store in lookup table
            self.mtpa_lut[optimal_torque] = optimal_iS_dq

    def get_optimal_current(self, Te_ref):
        """
        Get optimal stator current reference for given torque reference.
        
        Parameters
        ----------
        Te_ref : float
            Torque reference [p.u.].
     
        Returns
        -------
        ndarray
            Optimal stator current reference [p.u.].
        """

        # Find closest torque value in lookup table
        closest_torque = min(self.mtpa_lut.keys(),
                             key=lambda torque: abs(torque - Te_ref))

        return np.array(self.mtpa_lut[closest_torque])

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
