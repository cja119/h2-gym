"""
Equaitons for the bilevel shipping problem. These are implemented in a format which can
be solved by pyomo.
"""

from pyomo.environ import Constraint


def energy_balance(m, t):
    """
    Energy balance equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip

    eqn = 0

    eqn -= m.energy_curtailed[t]
    eqn -= m.energy_compression[t]
    eqn -= m.energy_electrolysis[t]
    eqn -= m.energy_conversion[t]

    eqn += m.energy_fuelcell[t]

    if m.renewables.value == "wind":
        eqn += m.energy_wind[t] * m.renewable_energy_capacity
    if m.renewables.value == "solar":
        eqn += m.energy_solar[t] * m.renewable_energy_capacity

    return eqn == 0


def hydrogen_production(m, t):
    """
    Hydrogen production equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    eqn = 0

    eqn += m.energy_electrolysis[t] * m.electrolysis_efficiency
    eqn -= m.hydrogen_produced[t]

    return eqn == 0


def compression_balance(m, t):
    """
    Compression balance equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    eqn = 0

    eqn += m.energy_compression[t]

    eqn -= m.hydrogen_produced[t] * m.electrolysis_compression_penalty
    eqn -= m.hydrogen_used[t] * m.production_compression_penalty
    eqn -= m.hydrogen_stored[t] * m.storage_compression_penalty

    return eqn == 0


def influent_hydrogen_balance(m, t):
    """
    Influent hydrogen balance equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    eqn = 0

    eqn += m.hydrogen_produced[t] * m.compression_efficiency
    eqn -= m.hydrogen_stored[t]
    eqn -= m.hydrogen_used[t]

    return eqn == 0


def effluent_hydrogen_balance(m, t):
    """
    Effluent hydrogen balance equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    eqn = 0

    eqn += m.vector_flux[t] / m.vector_synthetic_efficiency
    eqn += m.hydrogen_consumed_fuelcell[t]
    eqn -= m.hydrogen_used[t]
    eqn -= m.hydrogen_removed[t]

    return eqn == 0


def fuel_cell_production(m, t):
    """
    Fuel cell production equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    eqn = 0

    eqn += m.hydrogen_consumed_fuelcell[t] * m.fuelcell_efficiency
    eqn -= m.energy_fuelcell[t]

    return eqn == 0


def hydrogen_storage_balance(m, t):
    """
    Hydrogen storage balance equation for the lower production problem.
    """
    if t == 0:
        if m.fixed.value is True:
            return Constraint.Skip
        else:
            return m.hydrogen_storage[t] == 0.5 * m.hydrogen_storage_capacity
    eqn = 0
    eqn += m.hydrogen_storage[t]
    eqn -= m.hydrogen_storage[t - 1]
    eqn += m.hydrogen_removed[t]
    eqn -= m.hydrogen_produced[t]
    return eqn == 0


def vector_production(m, t):
    """
    Vector production equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    
    eqn = 0

    eqn += (
        m.vector_flux[t]
        * (m.variable_energy_penalty_conversion / m.calorific_value)
        * (1 - m.fixed_energy_penalty_conversion)
    )

    eqn += (
        m.n_active_trains_conversion[t]
        * m.fixed_energy_penalty_conversion
        * m.variable_energy_penalty_conversion
        * m.single_train_limit_conversion
    )

    eqn -= m.energy_conversion[t]

    return eqn == 0


def vector_storage_balance(m, t):
    """
    Vector storage balance equation for the lower production problem.
    """
    if t == 0:
        if m.fixed.value is True:
            return Constraint.Skip
        else:
            return m.vector_storage[t] == 0.5 * m.vector_storage_capacity
    eqn = 0
    eqn += (m.vector_storage[t] - m.vector_storage[t - 1]) * 1000
    eqn -= m.vector_flux[t] * m.conversion_fugitive_efficiency / m.calorific_value
    eqn += m.ship_charge_rate[t]

    return eqn == 0


def shipping_balance(m, t):
    """
    Shipping balance equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    
    eqn = 0

    if m.fixed.value is True:
        eqn -= m.cumulative_charge[0]

    eqn += m.cumulative_charge[t]
    eqn -= sum(m.ship_charge_rate[_t] for _t in range(t+1))
    
    if t % 24 == 0:
        eqn += sum(m.n_ship_sent[_t] * m.ship_capacity for _t in range(24,t+1,24))

    return eqn == 0


def port_capacity(m, t):
    """
    Constraint on the port capacity for the lower production problem.
    """
    if t == 0:
        if m.fixed.value is True:
            return Constraint.Skip
        else:
            return m.n_ship_sent[t] +  m.waiting_ships[t]== 0
    
    
    eqn = 0
    eqn += m.waiting_ships[t]
    eqn -= m.waiting_ships[t - 1]
    if t==1:
        eqn -= m.ship_arrived

    if t % 24 == 0:
        eqn += m.n_ship_sent[t]

    if t >= m.mean_ship_arrival_time * 24 and t % 24 == 0:
        eqn -= m.n_ship_ordered[t - m.mean_ship_arrival_time * 24]

    if t > 24 and t % 24 == 0:
        eqn -= m.expected_ships[t]

    return eqn == 0


def lower_hydrogen_storage_limit(m, t):
    """
    Lower hydrogen storage limit equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    cons = 0

    cons += m.hydrogen_storage_capacity * 0.2
    cons -= m.hydrogen_storage[t]

    return cons <= 0


def upper_hydrogen_storage_limit(m, t):
    """
    Upper hydrogen storage limit equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    cons = 0

    cons += m.hydrogen_storage[t]
    cons -= m.hydrogen_storage_capacity

    return cons <= 0

def lower_vector_storage_limit(m, t):
    """
    Lower vector storage limit equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    cons = 0

    cons += m.vector_storage_capacity * 0.2
    cons -= m.vector_storage[t]

    return cons <= 0


def upper_vector_storage_limit(m, t):
    """
    Upper vector storage limit equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    cons = 0

    cons += m.vector_storage[t]
    cons -= m.vector_storage_capacity

    return cons <= 0


def lower_vector_ramping_limit(m, t):
    """
    Lower vector ramping limit equation for the lower production problem.
    """
    if t == 0:
        return Constraint.Skip
    
    cons = 0
    cons += m.vector_flux[t - 1]
    cons -= m.vector_flux[t]
    cons /= m.calorific_value
    cons -= (
        m.n_active_trains_conversion[t-1]
        * m.single_train_limit_conversion
        * m.ramp_down_limit
    )

    return cons <= 0


def upper_vector_ramping_limit(m, t):
    """
    Upper vector ramping limit equation for the lower production problem.
    """
    if t == 0:
        return Constraint.Skip
    cons = 0

    cons += m.vector_flux[t]
    cons -= m.vector_flux[t - 1]
    cons /= m.calorific_value
    cons -= (
        (m.conversion_trains_number - m.n_active_trains_conversion[t-1])
        * m.single_train_limit_conversion
        * m.ramp_up_limit
    )

    return cons <= 0


def ship_send_limit(m, t):
    """
    Ship send limit equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    cons = 0

    cons -= m.ship_capacity
    cons += m.cumulative_charge[t]

    return cons <= 0


def ship_schedule_aux_lower(m, _t):
    """
    Ship schedule auxiliary equation for the lower production problem.
    """
    if _t == 0 and m.fixed.value is True:
        return Constraint.Skip
    
    cons = 0
    cons += m.n_ship_aux[_t]

    if _t >= m.mean_ship_arrival_time * 24:
        cons -= m.ship_schedule[_t] - sum(m.n_ship_sent[t] for t in range(_t - m.mean_ship_arrival_time * 24 , _t + 1, 24))
        cons -= sum(m.expected_ships[_t] for _t in range(_t - m.mean_ship_arrival_time * 24, _t + 1, 24))

    return cons <= 0


def ship_schedule_aux_upper(m, _t):
    """
    Ship schedule auxiliary equation for the lower production problem.
    """
    if _t == 0 and m.fixed.value is True:
        return Constraint.Skip
    cons = 0
    cons += m.n_ship_aux[_t]

    if _t >= m.mean_ship_arrival_time * 24:
        cons += m.ship_schedule[_t] - sum(m.n_ship_sent[t] for t in range(_t - m.mean_ship_arrival_time * 24, _t + 1, 24))
        cons += sum(m.expected_ships[_t] for _t in range(_t - m.mean_ship_arrival_time * 24, _t + 1, 24))
    return cons <= 0

def ship_arrival(m, t):
    """
    Ship arrival balance equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    
    cons = 0
    cons += m.ship_charge_rate[t] 
    cons -= m.waiting_ships[t] * m.ship_capacity /  m.ship_charge_limit 

    return cons <= 0


def ship_schedule_target(m, _t):
    """
    Ship schedule target equation for the lower production problem.
    """
    if _t == 0 and m.fixed.value is True:
        return Constraint.Skip
    cons = 0

    cons -= m.n_ship_aux[_t]

    return cons <= 0


def upper_vector_production_limit(m, t):
    """
    Upper vector production limit equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    cons = 0

    cons += m.vector_flux[t] / m.calorific_value
    cons -= m.single_train_limit_conversion * m.n_active_trains_conversion[t]

    return cons <= 0

def active_trains_limit(m, t):
    """
    Active trains limit equation for the lower production problem.
    """
    if t == 0 and m.fixed.value is True:
        return Constraint.Skip
    cons = 0

    cons += m.n_active_trains_conversion[t]
    cons -= m.conversion_trains_number

    return cons <= 0

def hydrogen_production_maximisation(m):
    """
    Hydrogen production maximisation equation for the lower production problem.
    """
    obj = 0
    obj += sum(m.vector_flux[t] for t in m.grid0)
    return obj


def hourly_profit(m,t):

    if t == 0:
        if m.fixed.value is True:     
            return Constraint.Skip
        else: 
            return m.cumulative_profit[t] == 0
    
    eqn = 0
    eqn += m.cumulative_profit[t]
    eqn -= m.cumulative_profit[t-1]
    
    eqn += m.waiting_ships[t]* (
        m.ship_berthing_rate + m.ship_charter_rate
    )
    if t % 24 == 0:
        eqn += m.n_ship_ordered[t] * m.ship_charter_rate * 35 * 24
        eqn  -= (m.n_ship_sent[t]
            * m.ship_capacity
            * m.calorific_value
            / 120
            * 5000
        )
    # Adding facility costs
    r_hourly = (1 + m.discount_factor) ** (1 / 8760) - 1
    H = 30 * 8760
    crf = (r_hourly * (1 + r_hourly) ** H) / ((1 + r_hourly) ** H - 1)
    eqn += (m.capex + m.opex ) * 1000000 * crf
    return eqn == 0


def profit_target(m):
    """
    Shipping target equation for the lower production problem.
    """
    return m.cumulative_profit[m.grid0.at(-1)] + sum(m.vector_flux[i] for i in range(24)) * m.calorific_value / 120 * 1000 
