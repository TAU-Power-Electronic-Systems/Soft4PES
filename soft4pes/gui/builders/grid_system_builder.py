"""Grid system builder for Soft4PES GUI. Allows to build a grid system based on 
the configuration provided by the user through the GUI."""

from types import SimpleNamespace

from soft4pes import model


class GridSystemBuilder:
    """Build grid-system model objects from a GUI configuration."""

    @staticmethod
    def build(config):

        # ==================================================
        # Base
        # ==================================================

        base = model.grid.BaseGrid(
            Vg_R_SI=config.Vg,
            Ig_R_SI=config.Ig,
            fg_R_SI=config.fg,
        )

        # ==================================================
        # Grid
        # ==================================================

        grid_params = model.grid.RLGridParameters(
            Vg_SI=config.Vg,
            fg_SI=config.fg,
            Rg_SI=config.Rg,
            Lg_SI=config.Lg,
            base=base,
        )

        # ==================================================
        # Converter
        # ==================================================

        conv = model.conv.Converter(
            v_dc_SI=config.Vdc,
            nl=config.converter_levels,
            base=base,
        )

        # ==================================================
        # Filter
        # ==================================================

        if config.filter_type == "L Filter":

            filter_params = (model.grid.LFilterParameters(
                L_fc_SI=config.Lfc,
                R_fc_SI=config.Rfc,
                base=base,
            ))

            sys = model.grid.RLGridLFilter(
                par_grid=grid_params,
                par_l_filter=filter_params,
                conv=conv,
                base=base,
            )

        elif config.filter_type == "LCL Filter":

            filter_params = (model.grid.LCLFilterParameters(
                L_fc_SI=config.Lfc,
                R_fc_SI=config.Rfc,
                C_SI=config.Cf,
                R_c_SI=config.Rc,
                L_fg_SI=config.Lfg,
                R_fg_SI=config.Rfg,
                base=base,
            ))

            sys = model.grid.RLGridLCLFilter(
                par_grid=grid_params,
                par_lcl_filter=filter_params,
                conv=conv,
                base=base,
            )

        else:

            raise ValueError(f"Unsupported filter: "
                             f"{config.filter_type}")

        return SimpleNamespace(
            base=base,
            grid_params=grid_params,
            filter_params=filter_params,
            conv=conv,
            sys=sys,
        )
