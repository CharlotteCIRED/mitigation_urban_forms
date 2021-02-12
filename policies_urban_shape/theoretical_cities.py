# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 10:28:53 2021

@author: Charlotte Liotta
"""

import numpy as np
import pandas as pd
import pickle

def import_baseline_city():
    param_baseline_city = {
        "beta" : 0.3,
        "A" : 2.014,
        "b" : 0.64,
        "delta" : 0.05,
        "coeff_land" : 1,
        "grid_size" : 100,
        "nb_commute" : 2 * 365,        
        "depreciation_time" : 100,
        "time_lag" : 3,
        "emissions_car" : 100, #gCO2/voy/km
        "emissions_public_transport" : 6, #gCO2/voy/km
        "pop_growth_rate" : 1.006,
        "income" : 65000,
        "init_population" : 5220000,
        "fixed_cost_car" : 5, #per commute
        "fuel_cost" : 0.2, #euro per km
        "public_transport_cost" : 0.2, #euro per km
        "car_speed" : 20, #km/h
        "public_transport_speed" : 13, #km/h
        "cost_of_time" : 1 / (365 * 7),
        "shape" : "circular"
        }
    
    return param_baseline_city

def import_small_city():
    param_small_city = {
        "beta" : 0.3,
        "A" : 2.014,
        "b" : 0.64,
        "delta" : 0.05,
        "coeff_land" : 1,
        "grid_size" : 100,
        "nb_commute" : 2 * 365,        
        "depreciation_time" : 100,
        "time_lag" : 3,
        "emissions_car" : 100, #gCO2/voy/km
        "emissions_public_transport" : 6, #gCO2/voy/km
        "pop_growth_rate" : 1.006,
        "income" : 65000,
        "init_population" : 740000,
        "fixed_cost_car" : 5, #per commute
        "fuel_cost" : 0.2, #euro per km
        "public_transport_cost" : 0.2, #euro per km
        "car_speed" : 20, #km/h
        "public_transport_speed" : 13, #km/h
        "cost_of_time" : 1 / (365 * 7),
        "shape" : "circular"
        }
    
    return param_small_city

def import_dvlping_city():
    param_dvlping_city = {
        "beta" : 0.3,
        "A" : 2.014,
        "b" : 0.64,
        "delta" : 0.05,
        "coeff_land" : 1,
        "grid_size" : 100,
        "nb_commute" : 2 * 365,        
        "depreciation_time" : 100,
        "time_lag" : 3,
        "emissions_car" : 100, #gCO2/voy/km
        "emissions_public_transport" : 6, #gCO2/voy/km
        "pop_growth_rate" : 1.023,
        "income" : 65000,
        "init_population" : 5220000,
        "fixed_cost_car" : 5, #per commute
        "fuel_cost" : 0.2, #euro per km
        "public_transport_cost" : 0.2, #euro per km
        "car_speed" : 20, #km/h
        "public_transport_speed" : 13, #km/h
        "cost_of_time" : 1 / (365 * 7),
        "shape" : "circular"
        }
    
    return param_dvlping_city

def import_poor_city():
    param_poor_city = {
        "beta" : 0.3,
        "A" : 2.014,
        "b" : 0.64,
        "delta" : 0.05,
        "coeff_land" : 1,
        "grid_size" : 100,
        "nb_commute" : 2 * 365,        
        "depreciation_time" : 100,
        "time_lag" : 3,
        "emissions_car" : 100, #gCO2/voy/km
        "emissions_public_transport" : 6, #gCO2/voy/km
        "pop_growth_rate" : 1.006,
        "income" : 19200,
        "init_population" : 5220000,
        "fixed_cost_car" : 5, #per commute
        "fuel_cost" : 0.2, #euro per km
        "public_transport_cost" : 0.2, #euro per km
        "car_speed" : 20, #km/h
        "public_transport_speed" : 13, #km/h
        "cost_of_time" : 1 / (365 * 7),
        "shape" : "circular"
        }
    
    return param_poor_city

def import_low_public_transport_city():
    param_low_public_transport_city = {
        "beta" : 0.3,
        "A" : 2.014,
        "b" : 0.64,
        "delta" : 0.05,
        "coeff_land" : 1,
        "grid_size" : 100,
        "nb_commute" : 2 * 365,        
        "depreciation_time" : 100,
        "time_lag" : 3,
        "emissions_car" : 100, #gCO2/voy/km
        "emissions_public_transport" : 6, #gCO2/voy/km
        "pop_growth_rate" : 1.006,
        "income" : 65000,
        "init_population" : 5220000,
        "fixed_cost_car" : 5, #per commute
        "fuel_cost" : 0.2, #euro per km
        "public_transport_cost" : 0.2, #euro per km
        "car_speed" : 20, #km/h
        "public_transport_speed" : 10, #km/h
        "cost_of_time" : 1 / (365 * 7),
        "shape" : "circular"
        }
    
    return param_low_public_transport_city

def import_fast_car_city():
    param_fast_car_city = {
        "beta" : 0.3,
        "A" : 2.014,
        "b" : 0.64,
        "delta" : 0.05,
        "coeff_land" : 1,
        "grid_size" : 100,
        "nb_commute" : 2 * 365,        
        "depreciation_time" : 100,
        "time_lag" : 3,
        "emissions_car" : 100, #gCO2/voy/km
        "emissions_public_transport" : 6, #gCO2/voy/km
        "pop_growth_rate" : 1.006,
        "income" : 65000,
        "init_population" : 5220000,
        "fixed_cost_car" : 5, #per commute
        "fuel_cost" : 0.2, #euro per km
        "public_transport_cost" : 0.2, #euro per km
        "car_speed" : 55, #km/h
        "public_transport_speed" : 13, #km/h
        "cost_of_time" : 1 / (365 * 7),
        "shape" : "circular"
        }
    
    return param_fast_car_city

def import_sprawled_city():
    param_sprawled_city = {
        "beta" : 0.4,
        "A" : 2.014,
        "b" : 0.64,
        "delta" : 0.05,
        "coeff_land" : 1,
        "grid_size" : 100,
        "nb_commute" : 2 * 365,        
        "depreciation_time" : 100,
        "time_lag" : 3,
        "emissions_car" : 100, #gCO2/voy/km
        "emissions_public_transport" : 6, #gCO2/voy/km
        "pop_growth_rate" : 1.006,
        "income" : 65000,
        "init_population" : 5220000,
        "fixed_cost_car" : 5, #per commute
        "fuel_cost" : 0.2, #euro per km
        "public_transport_cost" : 0.2, #euro per km
        "car_speed" : 20, #km/h
        "public_transport_speed" : 13, #km/h
        "cost_of_time" : 1 / (365 * 7),
        "shape" : "circular"
        }
    
    return param_sprawled_city

def import_semicircular_city():
    param_semicircular_city = {
        "beta" : 0.3,
        "A" : 2.014,
        "b" : 0.64,
        "delta" : 0.05,
        "coeff_land" : 1,
        "grid_size" : 100,
        "nb_commute" : 2 * 365,        
        "depreciation_time" : 100,
        "time_lag" : 3,
        "emissions_car" : 100, #gCO2/voy/km
        "emissions_public_transport" : 6, #gCO2/voy/km
        "pop_growth_rate" : 1.006,
        "income" : 65000,
        "init_population" : 5220000,
        "fixed_cost_car" : 5, #per commute
        "fuel_cost" : 0.2, #euro per km
        "public_transport_cost" : 0.2, #euro per km
        "car_speed" : 20, #km/h
        "public_transport_speed" : 13, #km/h
        "cost_of_time" : 1 / (365 * 7),
        "shape" : "semicircular"
        }
    
    return param_semicircular_city
