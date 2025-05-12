"""
Equaitons for the bilevel shipping problem. These are implemented in a format which can
be solved by pyomo. 
"""
from pyomo.environ import Constraint

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
    
    eqn += sum(m.n_active_trains_conversion[q,t] * m.fixed_energy_penalty_conversion[q] \
               * m.variable_energy_penalty_conversion * m.single_train_limit_conversion[q] for q in m.Q)
    
    eqn -= m.energy_conversion[t]

    return eqn == 0

def vector_storage_balance(m,q,t):
    """
    Vector storage balance equation for the lower production problem.
    """
    eqn = 0

    eqn += m.vector_stored[q,t] - m.vector_stored[q,t-1]
    eqn += m.vector_flux[q,t] * m.conversion_fugitive_efficiency
    m -= m.ship_charge_rate[q,t] 

    return eqn == 0

def shipping_balance(m,t):
    """
    Shipping balance equation for the lower production problem.
    """
    eqn = 0

    eqn += sum(m.cumulative_charge[q,t] for q in m.Q)
    eqn -= sum(sum(m.ship_charge_rate[q,_t] for q in m.Q) for _t in range(t))
    eqn += sum(sum(m.n_ship_sent[q,t] * m.ship_capacity[q] for q in m.Q) for _t in range(t))

    return eqn == 0

def lower_hydrogen_storage_limit(m,t):
    """
    Lower hydrogen storage limit equation for the lower production problem.
    """
    cons = 0

    cons += m.hydrogen_storage_capacity * 0.2
    cons -= m.hydrogen_stored[t]

    return cons <= 0

def upper_hydrogen_storage_limit(m,t):
    """
    Upper hydrogen storage limit equation for the lower production problem.
    """
    cons = 0

    cons += m.hydrogen_stored[t]
    cons -= m.hydrogen_storage_capacity 

    return cons <= 0

def lower_vector_storage_limit(m,t):
    """
    Lower vector storage limit equation for the lower production problem.
    """
    cons = 0

    cons += m.vector_storage_capacity * 0.2
    cons -= m.vector_stored[t]

    return cons <= 0    

def upper_vector_storage_limit(m,t):
    """
    Upper vector storage limit equation for the lower production problem.
    """
    cons = 0

    cons += m.vector_stored[t]
    cons -= m.vector_storage_capacity 

    return cons <= 0

def lower_vector_ramping_limit(m,q,t):
    """
    Lower vector ramping limit equation for the lower production problem.
    """
    if t == 0:
        return Constraint.Skip

    cons += m.energy_conversion[t-1] 
    cons -= m.energy_conversion[t]
    cons /= m.calorific_value[q]
    cons -= m.n_active_trains_conversion[q,t] * m.single_train_limit_conversion[q] * m.ramp_down_limit[q]

    return cons <= 0

def upper_vector_ramping_limit(m,q,t):
    """
    Upper vector ramping limit equation for the lower production problem.
    """
    if t == 0:
        return Constraint.Skip

    cons += m.energy_conversion[t] 
    cons -= m.energy_conversion[t-1]
    cons /= m.calorific_value[q]
    cons -= (m.n_train_conversion - m.n_active_trains_conversion[q,t]) * m.single_train_limit_conversion[q] \
        * m.ramp_up_limit[q]

    return cons <= 0

def ship_send_limit(m,q,t):
    """
    Ship send limit equation for the lower production problem.
    """
    cons = 0

    cons += m.n_ship_sent[q,t] * m.ship_capacity[q]
    cons -= m.cumulative_charge[q,t]

    return cons <= 0

def ship_schedule_aux_lower(m,q,t):
    """
    Ship schedule auxiliary equation for the lower production problem.
    """
    cons = 0
    cons -= m.n_ship_aux[q,t]
    cons += (m.n_ship_sent[q,t] - m.ship_schedule[q,t])
    return cons <= 0

def ship_schedule_aux_upper(m,q,t):
    """
    Ship schedule auxiliary equation for the lower production problem.
    """
    cons = 0
    cons -= m.n_ship_aux[q,t]
    cons += (m.ship_schedule[q,t]- m.n_ship_sent[q,t])
    return cons <= 0


def hydrogen_production_maximisation(m):
    """
    Hydrogen production maximisation equation for the lower production problem.
    """
    obj = 0
    obj += sum(m.hydrogen_produced[t] for t in m.T)
    return obj

def shipping_target(m):
    """
    Shipping target equation for the lower production problem.
    """
    obj = 0
    obj -= sum(m.n_ship_aux[q,t] for q in m.Q for t in m.T)
    return obj