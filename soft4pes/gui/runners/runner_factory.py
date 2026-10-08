"""Factory class to create appropriate runner instances based on the controller type."""

try:
    from .grid_following_runner import GridFollowingRunner
    from .grid_forming_runner import GridFormingRunner
    from .direct_mpc_runner import DirectMPCRunner
except ImportError:  # pragma: no cover - direct script execution fallback
    from runners.grid_following_runner import GridFollowingRunner
    from runners.grid_forming_runner import GridFormingRunner
    from runners.direct_mpc_runner import DirectMPCRunner


class RunnerFactory:
    """Factory class to create appropriate runner instances based on the controller type."""

    @staticmethod
    def create(
        config,
        references,
    ):

        controller = (config.controller_type)

        # ==================================================
        # Grid Following
        # ==================================================

        if (controller == "Grid Following - Linear"):

            return GridFollowingRunner(
                config=config,
                references=references,
            )

        # ==================================================
        # Grid Forming
        # ==================================================

        if controller in [
                "Grid Forming - MPC",
                "Grid Forming - Cascade",
        ]:

            return GridFormingRunner(
                config=config,
                references=references,
            )

        # ==================================================
        # Direct MPC
        # ==================================================

        if (controller == "Direct MPC - Grid Current"):

            return DirectMPCRunner(
                config=config,
                references=references,
            )

        raise ValueError(f"Unsupported controller: "
                         f"{controller}")
