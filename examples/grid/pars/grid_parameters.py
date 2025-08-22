from types import SimpleNamespace
from soft4pes import model

#Grid rated values
Vg_R_SI = 400
Ig_R_SI = 18
fg_R_SI = 50

# Grid load
Rg_SI = 0.07
Lg_SI = 30e-3

# Converter parameters
Vdc_SI = 750
conv_nl = 2

# Filter parameters
R_fc_SI = 0.1
L_fc_SI = 3e-3
C_SI = 10e-6
R_c_SI = 0.001

base_LV = model.grid.BaseGrid(Vg_R_SI=Vg_R_SI,
                              Ig_R_SI=Ig_R_SI,
                              fg_R_SI=fg_R_SI)

conv = model.conv.Converter(v_dc_SI=Vdc_SI, nl=conv_nl, base=base_LV)

pars_LV = model.grid.RLGridParameters(Vg_SI=Vg_R_SI,
                                      fg_SI=fg_R_SI,
                                      Rg_SI=Rg_SI,
                                      Lg_SI=Lg_SI,
                                      base=base_LV)

lcl_params = model.grid.LCLFilterParameters(L_fc_SI=L_fc_SI,
                                            R_fc_SI=R_fc_SI,
                                            C_SI=C_SI,
                                            R_c_SI=R_c_SI,
                                            base=base_LV)

weak_LV_grid = SimpleNamespace(
    base=base_LV,
    grid_params=pars_LV,
    lcl_params=lcl_params,
    conv=conv,
)
