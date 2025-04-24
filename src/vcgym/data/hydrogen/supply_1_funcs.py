def conversion_energy(U,V,etas):
    return V[1] # P_C

def hydrogen_energy(U,V,etas):
    return  V[2] # P_H_2

def hydrogen_production(U,V,etas):
    return V[0]  # P_H2_out

def hydrogen_storage(U,V,etas):
    return U[1,1] / etas['eta_H2'] + U[2,1] - V[0] #P_H2/eta_H2 + E'_H2 - P_H2_out 

def vector_production(U,V,etas):
    return V[0]

def vector_storage(U,V,etas):
    return U[3,1] + etas['eta_P_C'] * ((1 - etas['eta_F_C']) * U[1,1] + etas['eta_F_C'] *\
                                     (U[1,1]//etas['P_C_U'])) - V[0] # 

def num_ships(U,V,etas):
    return U[4,1] + V[0] - ((U[4,2] + U[3,1]) // (etas['E_M_U']))

def shipping_energy(U,V,etas):
    return U[4,2] + U[3,1] - etas['E_M_U'] * ((U[4,2] + U[3,1]) // (etas['E_M_U']))

def power_lim(U,V,etas):
    return V[0] + V[1] - V[2] - U[0,1]*etas["eta_N_T"]

def sup_lim(U,V,etas):
    return V[2] - V[1]

def ramp_up(U,V,etas):
    return V[1] - U[1,1] - (etas['N_C_U'] - V[1] // etas['P_C_U']) * etas['eta_C_U']

def ramp_lo(U,V,etas):
    return U[1,1] - V[1]  + (V[1] // etas['P_C_U']) * etas['eta_C_L']
    
def h2_store_up(U,V,etas):
    return U[1,1] / etas['eta_H2'] + U[1,1] - V[0] - etas["E_H2_U"]

def h2_store_lo(U,V,etas):
    return V[0] - U[1,1] / etas['eta_H2'] - U[2,1]  + etas["E_H2_L"]

def vec_store_up(U,V,etas):
    return U[3,1] + etas['eta_P_C'] * ((1 - etas['eta_F_C']) * U[1,1] + etas['eta_F_C'] *\
                                     (U[1,1]//etas['P_C_U'])) - V[0] - etas['E_C_U']

def vec_store_lo(U,V,etas):
    return V[0] - U[3,1] - etas['eta_P_C'] * ((1 - etas['eta_F_C']) * U[1,1] + etas['eta_F_C'] *\
                                     (U[1,1]//etas['P_C_U'])) + etas['E_C_L']
def ship_disc_lim(U,V,etas):
    return U[3,1] - (U[4,1] + V[0] - (U[4,2] + U[3,1]) // etas['E_M_U']) *  etas['P_M_U']

def total_disc_lim(U,V,etas):
    return U[4,2] + U[3,1] - etas['E_M_U'] * (U[4,1] + V[0])