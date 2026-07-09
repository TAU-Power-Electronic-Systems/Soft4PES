"""
Example of direct model predictive control (MPC) for an induction machine drive system. The 
controller aims to track the stator current reference calculated based on the reference values of 
the stator flux magnitude and torque. The machine operates at a constant (nominal) speed.
"""

from types import SimpleNamespace
import numpy as np

from pars.machine_config import get_custom_system
from soft4pes import model
from soft4pes.control import lin, modulation, mpc, common
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define torque reference sequence and stator flux magnitude reference sequence using sequence
# objects. The first array contains the time instants (in seconds) and the second array the
# corresponding reference values (in per unit). The reference is interpolated linearly between the
# time instants.
T_ref_seq = Sequence(
    np.array([0, 0.05, 0.05, 0.3]),
    np.array([0, 0, 1, 1]),
)

psiS_mag_ref_seq = Sequence(
    np.array([0, 0.3]),
    np.array([1, 1]),
)

ref_seq = SimpleNamespace(T_ref_seq=T_ref_seq,
                          psiS_mag_ref_seq=psiS_mag_ref_seq)

# Define the rotor speed sequence. The rotor speed are given in per unit so that the stator
# electrical angular frequency is 1 p.u. on rated torque.
wr_seq = Sequence(
    np.array([0, 0.15, 0.25, 0.3]),
    np.array([0.9583, 0.9583, 0.4583, 0.4583]),
)

# Get the system parameters from the ready made components. All the available components and systems
# are defined in the examples/machine/pars/machine_parameter_sets.json file, and given in the
# documentation. Here, a 2-level converter connected to low voltage induction machine is used.
config = get_custom_system(machine_name='LV_Induction_Machine',
                           converter_name='2L_LV_Converter')

# Create the system model consisting of the induction machine and converter. The initial stator flux
# magnitude reference and torque reference are passed to the IM model to set the initial
# state. Moreover, a sequence object is passed to the IM model to define the time-varying rotor
# speed.
sys = model.machine.InductionMachine(
    par=config.machine_params,
    conv=config.conv,
    base=config.base,
    wr=wr_seq,
    psiS_mag_ref_init=psiS_mag_ref_seq(0),
    T_ref_init=T_ref_seq(0),
)

# Choose the control strategy.
# "MPC" for model predictive control,
# "FOC" for field-oriented control,
# "V/f" for open-loop V/f control.

CTR_STRATEGY = "FOC"

# Define the electrical angular frequency estimator
im_ws_est = lin.IMwsEstimator(sys=sys)

match CTR_STRATEGY:
    case "MPC":
        # Use Branch-and-Bound solver
        solver = mpc.solvers.BranchAndBound()

        # Uncomment to use enumeration based solver
        # solver = mpc.solvers.MpcEnum(conv=config.conv)

        # Define the direct MPC current controller, which tracks the stator current references,
        # derived from the stator flux magnitude and torque references.
        iS_ref_gen = lin.IMStatorCurrRefGen()
        iS_mpc = mpc.algorithms.IMCurrCtr(solver=solver,
                                          lambda_u=5e-3,
                                          Np=4,
                                          disc_method='exact_discretization')

        # Instantiate the controller
        ctr_sys = common.ControlSystem(
            control_loops=[im_ws_est, iS_ref_gen, iS_mpc],
            ref_seq=ref_seq,
            Ts=250e-6)
    case "FOC":
        # Define the field-oriented controller, which tracks the stator current references,
        # derived from the stator flux magnitude and torque references.
        iS_ref_gen = lin.IMStatorCurrRefGen()
        foc = lin.FOCCurrCtr(sys=sys)

        # Instantiate the controller
        ctr_sys = common.ControlSystem(
            control_loops=[im_ws_est, iS_ref_gen, foc],
            ref_seq=ref_seq,
            Ts=200e-6,
            pwm=modulation.CarrierPWM(),
            common_mode_inj=modulation.CommonModeInjection())

    case "V/f":
        # Define the open-loop V/f controller, which calculates the stator voltage based on the
        # torque reference and stator flux magnitude reference.
        iS_curr_ctr = lin.VfCurrCtr(sys=sys)

        # Instantiate the controller with OPP modulator
        ctr_sys = common.ControlSystem(control_loops=[iS_curr_ctr],
                                       ref_seq=ref_seq,
                                       Ts=250e-6,
                                       pwm=modulation.OPPPWM(
                                           sys=sys,
                                           opp_file='2L_d11_opp_inductive.nc'))

# Simulate the system
sim = Simulation(sys=sys,
                 ctr=ctr_sys,
                 Ts_sim=5e-6,
                 disc_method='exact_discretization')
sim_data = sim.simulate(t_stop=0.3)

# Save the simulation data to a .mat file
sim.save_data()

# Plot the results
plotter = Plotter(data=sim_data, sys=sys)
plotter.plot_states(states_to_plot=['iS', 'psiR'],
                    frames=['abc', 'abc'],
                    plot_u_abc=True)
plotter.plot_control_signals_machine(plot_T=True, T_ref=T_ref_seq)
plotter.plot_spectra(states_to_plot=['iS'],
                     f_fund_SI=config.base.w / (2 * np.pi),
                     f_max_SI_plot=5000,
                     start_time=0.1,
                     n_cycles=2,
                     style='line')
plotter.show_all()
