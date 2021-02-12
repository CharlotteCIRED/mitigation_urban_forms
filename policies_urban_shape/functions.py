# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:05:38 2021

@author: Charlotte Liotta
"""

def compute_emissions(param_city, city, grid, trans):
    return 2*365 * ((sum(city.density[trans.mode == 0] * grid.distance_centre[trans.mode == 0]) * param_city["emissions_car"]) + (sum(city.density[trans.mode == 1] * grid.distance_centre[trans.mode == 1]) * param_city["emissions_public_transport"]))

def compute_housing_supply(housing_supply_t1_without_inertia, housing_supply_t0, scenario_city):
        diff_housing = ((housing_supply_t1_without_inertia - housing_supply_t0) / scenario_city["time_lag"]) - (housing_supply_t0 / scenario_city["depreciation_time"])
        for i in range(0, len(housing_supply_t1_without_inertia)):
            if housing_supply_t1_without_inertia[i] <= housing_supply_t0[i]:
                diff_housing[i] = - (housing_supply_t0[i] / scenario_city["depreciation_time"])

        housing_supply_t1 = housing_supply_t0 + diff_housing
        return housing_supply_t1