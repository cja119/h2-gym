"""
Equaitons for the bilevel shipping problem. These are implemented in a format which can
be solved by pyomo.
"""

from pyomo.environ import Constraint


def energy_balance(m, t):
    """
    Energy balance equation for the lower production problem.
    """
    eqn = 0

    eqn -= m.energy_curtailed[t]
    eqn -= m.energy_compression[t]
    eqn -= m.energy_electrolysis[t]
    eqn -= m.energy_conversion[t]

    eqn += m.energy_fuelcell[t]

    if m.renewables.value== 'wind':
        eqn += m.energy_wind[t] * m.renewable_energy_capacity
    if m.renewables.value == 'solar':
        eqn += m.energy_solar[t] * m.renewable_energy_capacity

    return eqn == 0


def hydrogen_production(m, t):
    """
    Hydrogen production equation for the lower production problem.
    """
    eqn = 0

    eqn += m.energy_electrolysis[t] * m.electrolysis_efficiency
    eqn -= m.hydrogen_produced[t]

    return eqn == 0


def compression_balance(m, t):
    """
    Compression balance equation for the lower production problem.
    """
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
    eqn = 0

    eqn += m.hydrogen_produced[t] * m.compression_efficiency
    eqn -= m.hydrogen_stored[t]
    eqn -= m.hydrogen_used[t]

    return eqn == 0


def effluent_hydrogen_balance(m, t):
    """
    Effluent hydrogen balance equation for the lower production problem.
    """
    eqn = 0

    eqn += m.vector_flux[t] / m.vector_synthetic_efficiency
    eqn -= m.hydrogen_used[t]
    eqn -= m.hydrogen_removed[t]

    return eqn == 0


def fuel_cell_production(m, t):
    """
    Fuel cell production equation for the lower production problem.
    """
    eqn = 0

    eqn += m.hydrogen_consumed_fuelcell[t] * m.fuelcell_efficiency
    eqn -= m.energy_fuelcell[t]

    return eqn == 0


def hydrogen_storage_balance(m, t):
    """
    Hydrogen storage balance equation for the lower production problem.
    """
    eqn = 0
    if t == 0:
        eqn += m.hydrogen_stored[t]
        eqn -= m.initial_hydrogen_storage
    else:
        eqn += m.hydrogen_stored[t]
        eqn -= m.hydrogen_stored[t - 1]
        eqn += m.hydrogen_removed[t]
        eqn -= m.hydrogen_stored[t]
        eqn -= m.hydrogen_consumed_fuelcell[t]
    return eqn == 0


def vector_production(m, t):
    """
    Vector production equation for the lower production problem.
    """
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
    eqn = 0
    if t == 0:
        eqn += m.vector_stored[t]
        eqn -= m.initial_vector_storage
    else:
        eqn += (m.vector_stored[t] - m.vector_stored[t - 1]) * 1000
        eqn += m.vector_flux[t] * m.conversion_fugitive_efficiency
        eqn -= m.ship_charge_rate[t]

    return eqn == 0


def shipping_balance(m, t):
    """
    Shipping balance equation for the lower production problem.
    """
    eqn = 0

    eqn += m.cumulative_charge[t]

    if t == 0:
        eqn -= m.initial_cumulative_charge
    else:
        eqn -= sum(m.ship_charge_rate[_t] for _t in range(t))
        eqn += sum(m.n_ship_sent[_t] * m.ship_capacity for _t in range(t))

    return eqn == 0


def lower_hydrogen_storage_limit(m, t):
    """
    Lower hydrogen storage limit equation for the lower production problem.
    """
    cons = 0

    cons += m.hydrogen_storage_capacity * 0.2
    cons -= m.hydrogen_stored[t]

    return cons <= 0


def upper_hydrogen_storage_limit(m, t):
    """
    Upper hydrogen storage limit equation for the lower production problem.
    """
    cons = 0

    cons += m.hydrogen_stored[t] 
    cons -= m.hydrogen_storage_capacity

    return cons <= 0


def lower_vector_storage_limit(m, t):
    """
    Lower vector storage limit equation for the lower production problem.
    """
    cons = 0

    cons += m.vector_storage_capacity * 0.2
    cons -= m.vector_stored[t]

    return cons <= 0


def upper_vector_storage_limit(m, t):
    """
    Upper vector storage limit equation for the lower production problem.
    """
    cons = 0

    cons += m.vector_stored[t]
    cons -= m.vector_storage_capacity

    return cons <= 0


def lower_vector_ramping_limit(m, t):
    """
    Lower vector ramping limit equation for the lower production problem.
    """
    cons = 0
    if t == 0:
        cons += m.energy_conversion[t]
        cons -= m.initial_conversion_process_state
    else:
        cons += m.energy_conversion[t - 1]
        cons -= m.energy_conversion[t]
        cons /= m.calorific_value
        cons -= (
            m.n_active_trains_conversion[t]
            * m.single_train_limit_conversion
            * m.ramp_down_limit
        )

    return cons <= 0


def upper_vector_ramping_limit(m, t):
    """
    Upper vector ramping limit equation for the lower production problem.
    """
    cons = 0
    if t == 0:
        cons -= m.energy_conversion[t]
        cons += m.initial_conversion_process_state
    else:
        cons += m.energy_conversion[t]
        cons -= m.energy_conversion[t - 1]
        cons /= m.calorific_value
        cons -= (
            (m.conversion_trains_number - m.n_active_trains_conversion[t])
            * m.single_train_limit_conversion
            * m.ramp_up_limit
        )

    return cons <= 0


def ship_send_limit(m, t):
    """
    Ship send limit equation for the lower production problem.
    """
    cons = 0

    cons += m.n_ship_sent[t] * m.ship_capacity
    cons -= m.cumulative_charge[t]

    return cons <= 0


def ship_schedule_aux_lower(m, _t):
    """
    Ship schedule auxiliary equation for the lower production problem.
    """
    if _t <= m.T:
        cons = 0
        cons += m.n_ship_aux[_t]
        cons -= m.ship_schedule[_t] - sum(m.n_ship_sent[t] for t in range(_t , _t + 24))
        return cons <= 0
    else:
        return Constraint.Skip


def ship_schedule_aux_upper(m, _t):
    """
    Ship schedule auxiliary equation for the lower production problem.
    """
    if _t <= m.T:
        cons = 0
        cons -= m.n_ship_aux[_t]
        cons += m.ship_schedule[_t] - sum(m.n_ship_sent[t] for t in range(_t, _t + 24))
        return cons <= 0
    else:
        return Constraint.Skip

def ship_arrival(m, t):
    """
    Ship arrival balance equation for the lower production problem.
    """
    cons = 0
    cons += m.ship_charge_rate[t]

    if t <= 24:
        if (
            m.ship_arrived > 0
            and sum(m.n_ship_sent[_t] for _t in range(t)) < m.ship_arrived
        ):
            cons -= m.ship_charge_limit * m.ship_arrived
    else:
        cons += m.ship_charge_limit * sum(
            m.n_ship_ordered[_t] for _t in range(0, t - 24)
        )
        cons -= m.ship_charge_limit * sum(m.n_ship_sent[_t] for _t in range(t))

    return cons <= 0


def ship_schedule_target(m, _t):
    """
    Ship schedule target equation for the lower production problem.
    """
    cons = 0

    cons -= m.n_ship_aux[_t]

    return cons <= 0

def upper_vector_production_limit(m, t):
    """
    Upper vector production limit equation for the lower production problem.
    """
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


def shipping_target(m):
    """
    Shipping target equation for the lower production problem.
    """
    obj = 0
    obj -= sum(m.n_ship_aux[t]  for t in m.grid1)
    return obj
