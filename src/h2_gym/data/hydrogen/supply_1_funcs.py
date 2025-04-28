def conversion_energy(vars):
    return vars['conversion_power'] # P_C

def hydrogen_energy(vars):
    return  vars['hydrogen_power'] # P_H_2

def hydrogen_production(vars):
    return vars['hydrogen_power']  # P_H2_out

def hydrogen_storage(vars):
    return vars['hydrogen_energy'] / vars['eta_H2'] + vars['old_hydrogen_storage'] - vars['eta_P_C'] * \
        ((1 - vars['eta_F_C']) * vars['conversion_energy'] + \
         vars['eta_F_C'] * (vars['conversion_energy'] //vars['P_C_U'])) #P_H2/eta_H2 + E'_H2 - P_H2_out 

def vector_production(vars):
    return  vars['eta_P_C'] * ((1 - vars['eta_F_C']) * vars['conversion_energy'] + \
                        vars['eta_F_C'] * (vars['conversion_energy'] //vars['P_C_U']))

def vector_output(vars):
    return vars['vector_power']

def vector_storage(vars):
    return vars['old_vector_storage'] + vars['vector_production'] - vars['vector_power'] # 

def num_ships(vars):
    return vars['old_ships'] + vars['ship_order'] - ((vars['old_shipping_energy'] +\
                                                       vars['vector_production']) // (vars['E_M_U']))

def shipping_energy(vars):
    return vars['old_shipping_energy'] + vars['vector_production'] - vars['E_M_U'] * \
        ((vars['old_shipping_energy'] + vars['vector_production']) // (vars['E_M_U']))

def power_lim(vars):
    return vars['conversion_power']+ vars['hydrogen_power']- vars['supplemental_power'] \
        - vars['renewable_power']*vars["eta_N_T"]

def sup_lim(vars):
    return vars['supplemental_power'] - vars['conversion_power']

def ramp_up(vars):
    return vars['conversion_power'] - vars['old_conversion_power'] - \
        (vars['N_C_U'] - vars['conversion_power'] // vars['P_C_U']) * vars['eta_C_U']

def ramp_lo(vars):
    return vars['old_conversion_power'] - vars['conversion_power'] + \
        (vars['conversion_power'] // vars['P_C_U']) * vars['eta_C_L']
    
def h2_store_up(vars):
    return vars['hydrogen_energy'] / vars['eta_H2'] + vars['old_hydrogen_storage'] - vars['eta_P_C'] * \
        ((1 - vars['eta_F_C']) * vars['conversion_energy'] + \
                        vars['eta_F_C'] * (vars['conversion_energy'] //vars['P_C_U'])) - vars["E_H2_U"]

def h2_store_lo(vars):
    return vars['eta_P_C'] * ((1 - vars['eta_F_C']) * vars['conversion_energy'] +  vars['eta_F_C'] * \
                (vars['conversion_energy'] //vars['P_C_U'])) - vars['hydrogen_energy'] /\
                      vars['eta_H2'] - vars['old_hydrogen_storage'] + vars["E_H2_L"]

def vec_store_up(vars):
    return vars['old_vector_storage']+ vars['vector_production'] - vars['vector_power'] - vars['E_C_U']

def vec_store_lo(vars):
    return vars['vector_power'] - vars['old_vector_storage'] - vars['vector_production'] + vars['E_C_L']

def ship_disc_lim(vars):
    return vars['vector_production'] - (vars['old_ships'] + vars['ship_order'] - (vars['old_shipping_energy'] +\
                vars['vector_production']) // vars['E_M_U']) *  vars['P_M_U']

def total_disc_lim(vars):
    return vars['old_shipping_energy'] + vars['vector_production'] - vars['E_M_U'] * (vars['old_ships'] + vars['ship_order'] )