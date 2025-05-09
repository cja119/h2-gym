"""
Equaitons for the bilevel shipping problem.
"""

def energy_balance(m,t):
    """
    Energy balance equation for the lower production problem.
    """
    eqn = 0

    eqn -= m.energy_curtailed[t]
    eqn -= m.energy_compression[t]
    eqn -= m.energy_electrolysis[t]
    eqn -= m.energy_conversion[t]
    
    eqn += m.energy_fuelcell[t]

    if m.wind == True:
        eqn += m.energy_wind[t]
    if m.solar == True:
        eqn += m.energy_solar[t]

    return eqn == 0

def hydrogen_production(m,t):
    """
    Hydrogen production equation for the lower production problem.
    """
    eqn = 0

    eqn += m.energy_electrolysis[t] * m.electrolysis_efficiency
    eqn -= m.hydrogen_produced[t]

    return eqn == 0

def compression_balance(m,t):
    """
    Compression balance equation for the lower production problem.
    """
    eqn = 0

    eqn += m.energy_compression[t]

    eqn -= m.hydrogen_produced[t] * m.electrolysis_compression_penalty
    eqn -= m.hydrogen_used[t] * m.production_compression_penalty
    eqn -= m.hydrogen_stored[t] * m.storage_compression_penalty

    return eqn == 0

def influent_hydrogen_balance(m,t):
    """
    Influent hydrogen balance equation for the lower production problem.
    """
    eqn = 0

    eqn += m.hydrogen_produced[t] * m.compression_efficiency
    eqn -= m.hydrogen_stored[t]
    eqn -= m.hydrogen_used[t]
    
    return eqn == 0

def effluent_hydrogen_balance(m,t):
    """
    Effluent hydrogen balance equation for the lower production problem.
    """
    eqn = 0

    eqn += sum(m.hydrogen_consumption[q,t] for q in m.Q)
    eqn -= m.hydrogen_used[t]
    eqn -= m.hydrogen_removed[t]

    return eqn == 0

def fuel_cell_production(m,t):
    """
    Fuel cell production equation for the lower production problem.
    """
    eqn = 0

    eqn += m.hydrogen_consumed_fuelcell[t] * m.fuelcell_efficiency
    eqn -= m.energy_fuelcell[t]

    return eqn == 0



def hydrogen_storage_balance(m,t):
    """
    Hydrogen storage balance equation for the lower production problem.
    """
    eqn = 0

    eqn += m.hydrogen_stored[t]
    eqn -= m.hydrogen_stored[t-1]

    return eqn == 0

def vector_production(m,t):
    """
    Vector production equation for the lower production problem.
    """
    eqn = 0

    eqn += sum(m.vector_flux[q,t] * (m.variable_energy_penalty_conversion / m.calorific_value[q]) \
               * (1 - m.fixed_energy_penalty_conversion[q]) for q in m.Q)
    
    eqn += sum(m.n_active_traiins_conversion[q,t] * m.fixed_energy_penalty_conversion[q] \
               * m.variable_energy_penalty_conversion * m.single_train_limit_conversion[q] for q in m.Q)
    
    eqn -= m.energy_conversion[t]

    return eqn == 0

def vector_storage_balance(m,t):
    """
    Vector storage balance equation for the lower production problem.
    """
    eqn = 0

    eqn += m.vector_stored[t] - m.vector_stored[t-1]
    eqn += m.vector_flux[t] * m.conversion_fugitive_efficiency
    m -= m.number_ships[t] * m.ship_discharge_rate[t] * 

    return eqn == 0