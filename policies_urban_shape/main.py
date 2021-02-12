# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 15:28:43 2021

@author: Charlotte Liotta
"""

import pandas as pd 
import numpy as np
import timeit #pour mesurer les temps
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D #pour les grapohes en 3d
import scipy as sc
from scipy import optimize
import math
import os
import pickle

from structures import *
from functions import *
from theoretical_cities import *
from import_policies import *

# %% PARAMETERS AND OPTIONS

param_baseline_city = import_baseline_city()
param_small_city = import_small_city()
param_dvlping_city = import_dvlping_city()
param_poor_city = import_poor_city()
param_low_public_transport_city = import_low_public_transport_city()
param_fast_car_city = import_fast_car_city()
param_sprawled_city = import_sprawled_city()
param_semicircular_city = import_semicircular_city()

list_cities = ["param_baseline_city", "param_small_city", "param_dvlping_city", "param_poor_city", "param_low_public_transport_city", "param_fast_car_city", "param_sprawled_city", "param_semicircular_city"]
duration = 100

carbon_tax = import_carbon_tax(duration)
greenbelt = import_greenbelt(duration)
public_transport_speed = import_public_transport_speed(duration)
no_policy = import_no_policy(duration)

#list_public_policies = ["carbon_tax", "greenbelt", "public_transport_speed", "no_policy"]
list_public_policies = ["greenbelt"]

for name_city in list_cities:
    for type_policy in list_public_policies:

        scenario_city = globals()[name_city]
        scenario_policy = globals()[type_policy]

        grid = GridSimulation()
        grid.create_grid(scenario_city["grid_size"])
        
        land = LandSimulation()
        land.create_land(grid, scenario_city, scenario_policy, 0)

        trans = TransportSimulation()
        trans.create_trans(grid, scenario_city, scenario_policy, 0)

        # %% PLOT

        def map2D(x):
                plt.scatter(grid.coord_X, grid.coord_Y, s = None, c = x, marker='.', cmap=plt.cm.RdYlGn)
                cbar = plt.colorbar()  
                plt.show()

        #def map3D(x):
            #    fig = plt.figure()
            #    ax = fig.add_subplot(111, projection='3d')    
            #    ax.scatter(grid.coord_X, grid.coord_Y, x, c = x, alpha = 0.2, marker='.')    
            #    ax.set_xlabel('coord_X')
            #    ax.set_ylabel('coord_Y')
            #    ax.set_zlabel('Value')    
            #    plt.show()
    
        # %% EQUILIBRIUM

        def compute_residual(R_0):
            city = City()
            city.compute_outputs(R_0, scenario_city, scenario_policy, trans, land, 1)
            delta_population = scenario_city["init_population"] - city.nb_households
            return delta_population

        R_0 = sc.optimize.fsolve(compute_residual, 300)
        city = City()
        city.compute_outputs(R_0, scenario_city, scenario_policy, trans, land, 1)

        #METHOD 1
        #U = zalphaqbeta
        #(((scenario_city["income"] - city.rent * city.dwelling_size  - trans.transport_price) ** (1 - scenario_city["beta"])) * (city.dwelling_size ** scenario_city["beta"]))
        #METHOD2
        #C = ((scenario_city["A"] ** (1 / (1-scenario_city["b"]))) * ((scenario_city["b"] * scenario_city["beta"] / scenario_city["delta"]) ** (scenario_city["b"] / (1 - scenario_city["b"]))) * 2 * np.pi * ((1 - scenario_city["beta"]) ** ((1 - scenario_city["beta"])/ (scenario_city["beta"] * (1 - scenario_city["b"])))))
        #gamma = 1 / ((1 - scenario_city["b"])* scenario_city["beta"])
        #mp = scenario_city["nb_commute"] * (scenario_city["public_transport_cost"] + (scenario_city["cost_of_time"]*scenario_city["income"]/scenario_city["public_transport_speed"]))
        #mc = scenario_city["nb_commute"] * (scenario_city["fuel_cost"] + (scenario_city["cost_of_time"]*scenario_city["income"]/scenario_city["car_speed"]))
        #Fc = scenario_city["nb_commute"] * scenario_city["fixed_cost_car"]
        #Y = scenario_city["income"]
        #N = scenario_city["init_population"]

        #term1 = ((C / N) ** (1 / gamma))
        #term2 = ((Y ** (gamma + 1)) / ((mp ** 2) * gamma * (gamma + 1)))
        #term3 = ((((mp ** 2) - (mc ** 2)) / ((mp ** 2) * (mc ** 2) * gamma * (gamma + 1)))  * ((Y - (mp * Fc) / (mp - mc)) ** (gamma + 1)))
        #term4 = ((Fc / (gamma * mp * mc)) * ((Y - (mp * Fc) / (mp - mc)) ** gamma))

        # * ((term2 + term3 + term4) ** (1/gamma))

        #((((scenario_city["A"] ** (1 / (1-scenario_city["b"]))) * ((scenario_city["b"] * scenario_city["beta"] / scenario_city["delta"]) ** (scenario_city["b"] / (1 - scenario_city["b"]))) * 2 * np.pi * ((1 - scenario_city["beta"]) ** ((1 - scenario_city["beta"])/ (scenario_city["beta"] * (1 - scenario_city["b"]))))) / N) ** (1 / gamma)) * ((((Y ** (gamma + 1)) / ((mp ** 2) * gamma * (gamma + 1))) + ((((mp ** 2) - (mc ** 2)) / ((mp ** 2) * (mc ** 2) * gamma * (gamma + 1)))  * ((Y - (mp * Fc) / (mp - mc)) ** (gamma + 1))) + ((Fc / (gamma * mp * mc)) * ((Y - (mp * Fc) / (mp - mc)) ** gamma))) ** (1/gamma))

        # %% DYNAMICS

        initial_year = 2020
        final_year = initial_year + duration - 1
        housing_supply_t0 = city.housing
        nb_households = city.nb_households
        index = 0

        emissions = np.zeros(duration)
        emissions_per_capita = np.zeros(duration)
        population = np.zeros(duration)
        welfare = np.zeros(duration)
        R0 = np.zeros(duration)
        utility = np.zeros(duration)
        z = np.nan * np.empty((duration, len(grid.distance_centre)))
        rent = np.nan * np.empty((duration, len(grid.distance_centre)))
        dwelling_size = np.nan * np.empty((duration, len(grid.distance_centre)))
        housing = np.nan * np.empty((duration, len(grid.distance_centre)))
        density = np.nan * np.empty((duration, len(grid.distance_centre)))

        #First iteration
    
        emissions[index] = compute_emissions(scenario_city, city, grid, trans)
        emissions_per_capita[index] = emissions[index] / scenario_city["init_population"]
        population[index] = city.nb_households
        R0[index] = R_0
        rent[index, :] = city.rent
        dwelling_size[index, :] = city.dwelling_size
        housing[index, :] = city.housing
        density[index, :] = city.density
        utility[index] = np.nanmax(((scenario_city["income"] - city.rent * city.dwelling_size  - trans.transport_price) ** (1 - scenario_city["beta"])) * (city.dwelling_size ** scenario_city["beta"]))
        z[index, :] = (scenario_city["income"] - city.rent * city.dwelling_size  - trans.transport_price)
    

        while initial_year + index < final_year:
    
            #Iterate
            index = index + 1
    
            #Adjust
            nb_households = scenario_city["init_population"] * (scenario_city["pop_growth_rate"] ** index)
            #Adjust trans if necessary
            trans = TransportSimulation()
            trans.create_trans(grid, scenario_city, scenario_policy, index)
            #Adjust land if necessary
            land = LandSimulation()
            land.create_land(grid, scenario_city, scenario_policy, index)
            if scenario_policy["greenbelt_start"] <= index:
                land.coeff_land[density[index - 1, :] <= scenario_policy["greenbelt_threshold"]] = scenario_policy["greenbelt_coeff"]
    
        
            #step 1 - without inertia
            def compute_residual(R_0):
                city = City()
                city.compute_outputs(R_0, scenario_city, scenario_policy, trans, land, 1)
                delta_population = nb_households - city.nb_households
                return delta_population
    
            R0_t1_without_inertia = sc.optimize.fsolve(compute_residual, 300)
            city_t1_without_inertia = City()
            city_t1_without_inertia.compute_outputs(R0_t1_without_inertia, scenario_city, scenario_policy, trans, land, 1)
            housing_supply_t1_without_inertia = city_t1_without_inertia.housing
    
            #step 2 - with inertia   
            housing_supply_t1 = compute_housing_supply(housing_supply_t1_without_inertia, housing_supply_t0, scenario_city)    
   
            def compute_residual(R_0):
                city = City()
                city.compute_outputs(R_0, scenario_city, scenario_policy, trans, land, 0, housing_supply_t1)
                delta_population = nb_households - city.nb_households
                return delta_population
    
            R0_t1 = sc.optimize.fsolve(compute_residual, 155)
            city_t1 = City()
            city_t1.compute_outputs(R0_t1, scenario_city, scenario_policy, trans, land, 0, housing_supply_t1)
    
            #Export outputs
            emissions[index] = copy.deepcopy(compute_emissions(scenario_city, city_t1, grid, trans))
            emissions_per_capita[index] = copy.deepcopy(emissions[index] / (city_t1.nb_households))
            population[index] = copy.deepcopy(city_t1.nb_households)
            R0[index] = copy.deepcopy(R0_t1)
            rent[index, :] = copy.deepcopy(city_t1.rent)
            dwelling_size[index, :] = copy.deepcopy(city_t1.dwelling_size)
            housing[index, :] = copy.deepcopy(city_t1.housing)
            density[index, :] = copy.deepcopy(city_t1.density)
            utility[index] = copy.deepcopy(np.nanmax(((scenario_city["income"] - city_t1.rent * city_t1.dwelling_size  - trans.transport_price) ** (1 - scenario_city["beta"])) * (city_t1.dwelling_size ** scenario_city["beta"])))
            z[index, :] = copy.deepcopy(scenario_city["income"] - city_t1.rent * city_t1.dwelling_size  - trans.transport_price)
            
    
            #Prepare iteration
            housing_supply_t0 = copy.deepcopy(city_t1.housing)
            
        name = type_policy + "_" + name_city
        os.mkdir("C:/Users/Coupain/Desktop/these/Sorties/" + name)
        np.save("C:/Users/Coupain/Desktop/these/Sorties/" + name + "/emissions.npy", emissions)    
        np.save("C:/Users/Coupain/Desktop/these/Sorties/" + name + "/emissions_per_capita.npy", emissions_per_capita)    
        np.save("C:/Users/Coupain/Desktop/these/Sorties/" + name + "/population.npy", population)    
        np.save("C:/Users/Coupain/Desktop/these/Sorties/" + name + "/R0.npy", R0)    
        np.save("C:/Users/Coupain/Desktop/these/Sorties/" + name + "/rent.npy", rent)    
        np.save("C:/Users/Coupain/Desktop/these/Sorties/" + name + "/dwelling_size.npy", dwelling_size)    
        np.save("C:/Users/Coupain/Desktop/these/Sorties/" + name + "/housing.npy", housing)    
        np.save("C:/Users/Coupain/Desktop/these/Sorties/" + name + "/density.npy", density)    
        np.save("C:/Users/Coupain/Desktop/these/Sorties/" + name + "/utility.npy", utility)   


### Plot outputs

emissions_capita = {}
for name_city in list_cities:
    for type_policy in ["greenbelt"]:
        emissions_capita[name_city] = np.load("C:/Users/Coupain/Desktop/these/Sorties/" + type_policy + '_' + name_city + "/emissions_per_capita.npy")    

utility = {}
for name_city in list_cities:
    for type_policy in ["greenbelt"]:
        utility[name_city] = np.load("C:/Users/Coupain/Desktop/these/Sorties/" + type_policy + '_' + name_city + "/utility.npy")    

utility_no_policy = {}
for name_city in list_cities:
    for type_policy in ["no_policy"]:
        utility_no_policy[name_city] = np.load("C:/Users/Coupain/Desktop/these/Sorties/" + type_policy + '_' + name_city + "/utility.npy")    

plt.rcParams.update({'font.size': 10})
plt.plot(emissions_capita[list_cities[0]] / emissions_capita[list_cities[0]][0], label = "Baseline city")
plt.plot(emissions_capita[list_cities[1]] / emissions_capita[list_cities[1]][0], label = "Small city")
plt.plot(emissions_capita[list_cities[2]] / emissions_capita[list_cities[2]][0], label = "Developing city")
plt.plot(emissions_capita[list_cities[3]] / emissions_capita[list_cities[3]][0], label = "Poor city")
plt.plot(emissions_capita[list_cities[4]] / emissions_capita[list_cities[4]][0], label = "Slow public transports")
plt.plot(emissions_capita[list_cities[5]] / emissions_capita[list_cities[5]][0], label = "Fast cars")
plt.plot(emissions_capita[list_cities[6]] / emissions_capita[list_cities[6]][0], label = "Sprawled city")
plt.plot(emissions_capita[list_cities[7]] / emissions_capita[list_cities[7]][0], label = "Seaside city")
plt.legend()
plt.ylabel("Emissions per capita (Base year 0)")
plt.xlabel("Year (carbon tax t = 5)")

plt.plot(utility[list_cities[0]] / utility[list_cities[0]][0], label = list_cities[0])
plt.plot(utility[list_cities[1]] / utility[list_cities[1]][0], label = list_cities[1])
plt.plot(utility[list_cities[2]] / utility[list_cities[2]][0], label = list_cities[2])
plt.plot(utility[list_cities[3]] / utility[list_cities[3]][0], label = list_cities[3])
plt.plot(utility[list_cities[4]] / utility[list_cities[4]][0], label = list_cities[4])
plt.plot(utility[list_cities[5]] / utility[list_cities[5]][0], label = list_cities[5])
plt.plot(utility[list_cities[6]] / utility[list_cities[6]][0], label = list_cities[6])
plt.plot(utility[list_cities[7]] / utility[list_cities[7]][0], label = list_cities[7])
plt.legend()
plt.ylabel("Welfare (Base year 0)")
plt.xlabel("Year (carbon tax t = 5)")

plt.rcParams.update({'font.size': 10})
plt.plot(utility[list_cities[0]] / utility_no_policy[list_cities[0]], label = "Baseline city")
plt.plot(utility[list_cities[1]] / utility_no_policy[list_cities[1]], label = "Small city")
plt.plot(utility[list_cities[2]] / utility_no_policy[list_cities[2]], label = "Developing city")
plt.plot(utility[list_cities[3]] / utility_no_policy[list_cities[3]], label = "Poor city")
plt.plot(utility[list_cities[4]] / utility_no_policy[list_cities[4]], label = "Slow public transports")
plt.plot(utility[list_cities[5]] / utility_no_policy[list_cities[5]], label = "Fast cars")
plt.plot(utility[list_cities[6]] / utility_no_policy[list_cities[6]], label = "Sprawled city")
plt.plot(utility[list_cities[7]] / utility_no_policy[list_cities[7]], label = "Seaside city")
plt.legend(loc = "upper right")
plt.ylabel("Welfare loss (compared to BAU scenario)")
plt.xlabel("Year (carbon taxd t = 5)")

plt.figure(figsize=(15,10))
plt.tick_params(bottom = False)
plt.rcParams.update({'font.size': 16})
plt.bar(x = range(8), height = [(1 - (emissions_capita[list_cities[0]] / emissions_capita[list_cities[0]][0])[20])*100, 
                                (1 - (emissions_capita[list_cities[1]] / emissions_capita[list_cities[1]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[2]] / emissions_capita[list_cities[2]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[3]] / emissions_capita[list_cities[3]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[4]] / emissions_capita[list_cities[4]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[5]] / emissions_capita[list_cities[5]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[6]] / emissions_capita[list_cities[6]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[7]] / emissions_capita[list_cities[7]][0])[20])*100]
        , tick_label = ["Baseline \n city", "Small \n city", "Developing \n city", "Poor \n city", "Slow \n public \n transports", "Fast \n cars", "Sprawled \n city", "Seaside \n city"])
plt.ylabel("Emissions per capita reduction after 15 years (%)")

plt.figure(figsize=(1510))
plt.tick_params(bottom = False)
plt.rcParams.update({'font.size': 14})
plt.bar(x = range(8), height = [((utility[list_cities[0]] / utility_no_policy[list_cities[0]])[99] - 1)*100, 
                                ((utility[list_cities[1]] / utility_no_policy[list_cities[1]])[99] - 1)*100,
                                ((utility[list_cities[2]] / utility_no_policy[list_cities[2]])[99] - 1)*100,
                                ((utility[list_cities[3]] / utility_no_policy[list_cities[3]])[99] - 1)*100,
                                ((utility[list_cities[4]] / utility_no_policy[list_cities[4]])[99] - 1)*100,
                                ((utility[list_cities[5]] / utility_no_policy[list_cities[5]])[99] - 1)*100,
                                ((utility[list_cities[6]] / utility_no_policy[list_cities[6]])[99] - 1)*100,
                                ((utility[list_cities[7]] / utility_no_policy[list_cities[7]])[99] - 1)*100]
        , tick_label = ["Baseline \n city", "Small \n city", "Developing \n city", "Poor \n city", "Slow \n public \n transports", "Fast \n cars", "Sprawled \n city", "Seaside \n city"])
plt.ylabel("Welfare loss (%)")

angles = [n / float(8) * 2 * np.pi for n in range(8)]
values = [(1 - (emissions_capita[list_cities[0]] / emissions_capita[list_cities[0]][0])[20])*100, 
                                (1 - (emissions_capita[list_cities[1]] / emissions_capita[list_cities[1]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[2]] / emissions_capita[list_cities[2]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[3]] / emissions_capita[list_cities[3]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[4]] / emissions_capita[list_cities[4]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[5]] / emissions_capita[list_cities[5]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[6]] / emissions_capita[list_cities[6]][0])[20])*100,
                                (1 - (emissions_capita[list_cities[7]] / emissions_capita[list_cities[7]][0])[20])*100]
angles += angles[:1]
values += values[:1]

f = plt.figure(figsize=(8,4))
ax = f.add_subplot(111, polar=True)
plt.polar(angles, values)
plt.fill(angles, values, alpha = 0.3)
plt.yticks([5,10,15], color = "grey", size = 15)
plt.xticks(angles[:-1], np.array(["Baseline \n city", "Small \n city", "Developing \n city", "Poor \n city", "Slow \n public \n transports", "Fast \n cars", "Sprawled \n city", "Seaside \n city"]))
for label,i in zip(ax.get_xticklabels(),range(0,len(angles))):

    angle_rad=angles[i]
    if 0<angle_rad <= np.pi/2:
        ha= 'center'
        va= "bottom"

    elif np.pi/2 < angle_rad < np.pi:
        ha= 'center'
        va= "bottom"
        
    elif angle_rad == np.pi:
        ha= 'right'
        va= "bottom"
    elif angle_rad == 0:
        ha= 'left'
        va= "bottom"

    elif np.pi < angle_rad <= (3*np.pi/2):
        ha= 'center'
        va= "top"  

    else:
        ha= 'left'
        va= "top"

    label.set_verticalalignment(va)
    label.set_horizontalalignment(ha)
plt.show()
