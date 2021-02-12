# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 17:40:31 2021

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
from import_cities import *
from import_policies import *

# %% PARAMETERS AND OPTIONS

param_paris = import_paris()
param_atlanta = import_atlanta()
param_sao_paolo = import_sao_paolo()
param_shanghai = import_shanghai()
param_curitiba = import_curitiba()
param_medellin = import_medellin()
param_kazan = import_kazan()

list_cities = ["param_paris", "param_atlanta", "param_sao_paolo", "param_shanghai", "param_curitiba", "param_medellin", "param_kazan"]
duration = 21

carbon_tax = import_carbon_tax(duration)
greenbelt = import_greenbelt(duration)
public_transport_speed = import_public_transport_speed(duration)
no_policy = import_no_policy(duration)

list_public_policies = ["greenbelt", "carbon_tax", "public_transport_speed", "no_policy"]

for name_city in list_cities:
    for type_policy in list_public_policies:

        param_city = globals()[name_city]
        scenario_policy = globals()[type_policy]

        grid = GridSimulation(coord_X=param_city["grid"].coord_X, coord_Y=param_city["grid"].coord_Y,distance_centre=param_city["grid"].distance_cbd,area=param_city["grid"].area)
        land = LandSimulation(coeff_land = param_city["coeff_land"])

        trans = TransportSimulation()     
        trans.real_city(param_city, scenario_policy, index)

        # %% PLOT

        #def map2D(x):
        #        plt.scatter(grid.coord_X, grid.coord_Y, s = None, c = x, marker='.', cmap=plt.cm.RdYlGn)
        #        cbar = plt.colorbar()  
        #        plt.show()

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
            city.compute_outputs(R_0, param_city, scenario_policy, trans, land, 1)
            delta_population = param_city["init_population"] - city.nb_households
            return delta_population

        R_0 = sc.optimize.fsolve(compute_residual, 300)
        city = City()
        city.compute_outputs(R_0, param_city, scenario_policy, trans, land, 1)

        #plt.scatter(grid.distance_centre, param_city["data_rent"])
        #plt.scatter(grid.distance_centre, city.rent)
        
        #plt.scatter(grid.distance_centre, param_city["data_density"])
        #plt.scatter(grid.distance_centre, city.density)
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
    
        emissions[index] = compute_emissions(param_city, city, grid, trans)
        emissions_per_capita[index] = emissions[index] / param_city["init_population"]
        population[index] = city.nb_households
        R0[index] = R_0
        rent[index, :] = city.rent
        dwelling_size[index, :] = city.dwelling_size
        housing[index, :] = city.housing
        density[index, :] = city.density
        utility[index] = (param_city["income"] * ((1 - param_city["beta"]) ** (1 - param_city["beta"])) * (param_city["beta"] ** param_city["beta"])) / (R0[index] ** param_city["beta"])
        z[index, :] = (param_city["income"] - city.rent * city.dwelling_size  - trans.transport_price)
    

        while initial_year + index < final_year:
    
            #Iterate
            index = index + 1
    
            #Adjust
            if index < 5:
                nb_households = population[index - 1] * (1 + (param_city["pop_growth_rate"][0] / 100))
            elif index < 10:
                nb_households = population[index - 1] * (1 + (param_city["pop_growth_rate"][1] / 100))
            elif index < 15:
                nb_households = population[index - 1] * (1 + (param_city["pop_growth_rate"][2] / 100))
            else:
                nb_households = population[index - 1] * (1 + (param_city["pop_growth_rate"][3] / 100))
            
            param_city["income"] = param_city["income"] * param_city["income_growth_rate"]
            
            if scenario_policy["greenbelt_implementation"][index] == 1:
                land.coeff_land[grid.distance_centre >scenario_policy["greenbelt_start"]] = scenario_policy["greenbelt_coeff"]
                
            trans = TransportSimulation()     
            trans.real_city(param_city, scenario_policy, index)
            
            #step 1 - without inertia
            def compute_residual(R_0):
                city = City()
                city.compute_outputs(R_0, param_city, scenario_policy, trans, land, 1)
                delta_population = nb_households - city.nb_households
                return delta_population
    
            R0_t1_without_inertia = sc.optimize.fsolve(compute_residual, 300)
            city_t1_without_inertia = City()
            city_t1_without_inertia.compute_outputs(R0_t1_without_inertia, param_city, scenario_policy, trans, land, 1)
            housing_supply_t1_without_inertia = city_t1_without_inertia.housing
    
            #step 2 - with inertia   
            housing_supply_t1 = compute_housing_supply(housing_supply_t1_without_inertia, housing_supply_t0, param_city)    
   
            def compute_residual(R_0):
                city = City()
                city.compute_outputs(R_0, param_city, scenario_policy, trans, land, 0, housing_supply_t1)
                delta_population = nb_households - city.nb_households
                return delta_population
    
            R0_t1 = sc.optimize.fsolve(compute_residual, 155)
            city_t1 = City()
            city_t1.compute_outputs(R0_t1, param_city, scenario_policy, trans, land, 0, housing_supply_t1)
    
            #Export outputs
            emissions[index] = copy.deepcopy(compute_emissions(param_city, city_t1, grid, trans))
            emissions_per_capita[index] = copy.deepcopy(emissions[index] / (city_t1.nb_households))
            population[index] = copy.deepcopy(city_t1.nb_households)
            R0[index] = copy.deepcopy(R0_t1)
            rent[index, :] = copy.deepcopy(city_t1.rent)
            dwelling_size[index, :] = copy.deepcopy(city_t1.dwelling_size)
            housing[index, :] = copy.deepcopy(city_t1.housing)
            density[index, :] = copy.deepcopy(city_t1.density)
            utility[index] =  (param_city["income"] * ((1 - param_city["beta"]) ** (1 - param_city["beta"])) * (param_city["beta"] ** param_city["beta"])) / (R0[index] ** param_city["beta"])
            z[index, :] = copy.deepcopy(param_city["income"] - city_t1.rent * city_t1.dwelling_size  - trans.transport_price)
            
    
            #Prepare iteration
            housing_supply_t0 = copy.deepcopy(city_t1.housing)
            
        name = type_policy + name_city
        os.mkdir("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name)
        np.save("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name + "/emissions.npy", emissions)    
        np.save("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name + "/emissions_per_capita.npy", emissions_per_capita)    
        np.save("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name + "/population.npy", population)    
        np.save("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name + "/R0.npy", R0)    
        np.save("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name + "/rent.npy", rent)    
        np.save("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name + "/dwelling_size.npy", dwelling_size)    
        np.save("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name + "/housing.npy", housing)    
        np.save("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name + "/density.npy", density)    
        np.save("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + name + "/utility.npy", utility)   

emissions_capita = {}
for name_city in list_cities:
    for type_policy in ["greenbelt"]:
        emissions_capita[name_city] = np.load("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + type_policy + name_city + "/emissions_per_capita.npy")    

utility = {}
for name_city in list_cities:
    for type_policy in ["greenbelt"]:
        utility[name_city] = np.load("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + type_policy + name_city + "/utility.npy")    

utility_no_policy = {}
for name_city in list_cities:
    for type_policy in ["no_policy"]:
        utility_no_policy[name_city] = np.load("C:/Users/Charlotte Liotta/Desktop/these/Sorties/20210210/" + type_policy + name_city + "/utility.npy")    

plt.rcParams.update({'font.size': 10})
plt.plot(emissions_capita[list_cities[0]] / emissions_capita[list_cities[0]][0], label = "Paris")
plt.plot(emissions_capita[list_cities[1]] / emissions_capita[list_cities[1]][0], label = "Atlanta")
plt.plot(emissions_capita[list_cities[2]] / emissions_capita[list_cities[2]][0], label = "Sao Paolo")
plt.plot(emissions_capita[list_cities[3]] / emissions_capita[list_cities[3]][0], label = "Shanghai")
plt.plot(emissions_capita[list_cities[4]] / emissions_capita[list_cities[4]][0], label = "Curitiba")
plt.plot(emissions_capita[list_cities[5]] / emissions_capita[list_cities[5]][0], label = "Medellin")
plt.plot(emissions_capita[list_cities[6]] / emissions_capita[list_cities[6]][0], label = "Kazan")
plt.legend()
plt.ylabel("Emissions per capita (Base year 0)")
plt.xlabel("Year (greenbelt t = 5)")

plt.plot(utility[list_cities[0]] / utility[list_cities[0]][0], label = "Paris")
plt.plot(utility[list_cities[1]] / utility[list_cities[1]][0], label = "Atlanta")
plt.plot(utility[list_cities[2]] / utility[list_cities[2]][0], label = "Sao Paolo")
plt.plot(utility[list_cities[3]] / utility[list_cities[3]][0], label = "Shanghai")
plt.plot(utility[list_cities[4]] / utility[list_cities[4]][0], label = "Curitiba")
plt.plot(utility[list_cities[5]] / utility[list_cities[5]][0], label = "Medellin")
plt.plot(utility[list_cities[6]] / utility[list_cities[6]][0], label = "Kazan")
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
plt.legend(loc = "upper right")
plt.ylabel("Welfare loss (compared to BAU scenario)")
plt.xlabel("Year (carbon taxd t = 5)")

plt.figure(figsize=(15,10))
plt.tick_params(bottom = False)
plt.rcParams.update({'font.size': 16})
plt.bar(x = range(7), height = [(1 - (emissions_capita[list_cities[0]] / emissions_capita[list_cities[0]][0])[19])*100, 
                                (1 - (emissions_capita[list_cities[1]] / emissions_capita[list_cities[1]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[2]] / emissions_capita[list_cities[2]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[3]] / emissions_capita[list_cities[3]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[4]] / emissions_capita[list_cities[4]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[5]] / emissions_capita[list_cities[5]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[6]] / emissions_capita[list_cities[6]][0])[19])*100]
        , tick_label = ["Paris", "Atlanta", "Sao Paolo", "Shanghai", "Curitiba", "Medellin", "Kazan"])
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

angles = [n / float(7) * 2 * np.pi for n in range(7)]
values = [(1 - (emissions_capita[list_cities[0]] / emissions_capita[list_cities[0]][0])[19])*100, 
                                (1 - (emissions_capita[list_cities[1]] / emissions_capita[list_cities[1]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[2]] / emissions_capita[list_cities[2]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[3]] / emissions_capita[list_cities[3]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[4]] / emissions_capita[list_cities[4]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[5]] / emissions_capita[list_cities[5]][0])[19])*100,
                                (1 - (emissions_capita[list_cities[6]] / emissions_capita[list_cities[6]][0])[19])*100]
angles += angles[:1]
values += values[:1]

f = plt.figure(figsize=(8,4))
ax = f.add_subplot(111, polar=True)
plt.polar(angles, values)
plt.fill(angles, values, alpha = 0.3)
plt.yticks([5,10,15], color = "grey", size = 15)
plt.xticks(angles[:-1], np.array(["Paris", "Atlanta", "Sao Paolo", "Shanghai", "Curitiba", "Medellin", "Kazan"]))
for label,i in zip(ax.get_xticklabels(),range(0,len(angles))):

    angle_rad=angles[i]
    if 0<angle_rad <= np.pi/2:
        ha= 'left'
        va= "bottom"

    elif np.pi/2 < angle_rad < np.pi:
        ha= 'right'
        va= "bottom"
        
    elif angle_rad == np.pi:
        ha= 'right'
        va= "bottom"
    elif angle_rad == 0:
        ha= 'left'
        va= "bottom"

    elif np.pi < angle_rad <= (3*np.pi/2):
        ha= 'right'
        va= "top"  

    else:
        ha= 'left'
        va= "top"

    label.set_verticalalignment(va)
    label.set_horizontalalignment(ha)
plt.show()