# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 15:41:57 2021

@author: Charlotte Liotta
"""

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import copy
import math

class GridSimulation:
    """Define a grid defined by :
        
        - coord_X
        - coord_Y
        - distance_centre
        """
    
    def __init__(self,coord_X=0,coord_Y=0,distance_centre=0,area=0): 
        
        self.coord_X = coord_X
        self.coord_Y = coord_Y
        self.distance_centre = distance_centre
        self.area = area
        
        
    def create_grid(self,n):
        """Create a n*n grid, centered on 0"""
        
        coord_X = np.zeros(n*n)
        coord_Y = np.zeros(n*n)
    
        index = 0
        
        for i in range(n):
            for j in range(n):
                coord_X[index] = i - n/2
                coord_Y[index] = j - n/2
                index = index + 1
        distance_centre = (coord_X**2 + coord_Y**2) ** 0.5
    
        self.coord_X = coord_X
        self.coord_Y = coord_Y
        self.distance_centre = distance_centre
        self.area = 1

    def __repr__(self):
        
        return "Grid:\n  coord_X: {}\n  coord_Y: {}\n  distance_centre: {}\n  area: {}".format(
                self.coord_X, self.coord_Y, self.distance_centre, self.area)       

class LandSimulation:
    
    def __init__(self, coeff_land=0):
        self.coeff_land = coeff_land

    def create_land(self, grid:GridSimulation, param_city, scenario_policy, index):
        """Create a uniform land-use avalability vector"""
        coeff_land = np.ones(len(grid.coord_X)) * param_city["coeff_land"]
        if param_city["shape"] == "semicircular":
            coeff_land[((math.cos(2 * np.pi * 0.5) < grid.coord_X / (np.sqrt((grid.coord_X**2) + (grid.coord_Y**2)))) & (grid.coord_Y > 0))] = 0
        
        self.coeff_land = coeff_land
        
    def __repr__(self):
        return "Land:\n  coeff_land: {}".format(
            self.coeff_land) 
    
class TransportSimulation:
    
    def __init__(self,price_car=0,price_public_transport=0,mode=0,transport_price=0):
        self.price_car = price_car
        self.price_public_transport = price_public_transport
        self.mode = mode
        self.transport_price = transport_price
        
    def create_trans(self, grid:GridSimulation, param_city, param_policy, index):
        
        if param_policy["carbon_tax_implementation"][index] == 0:
            price_car = param_city["nb_commute"] * (param_city["fixed_cost_car"] + (param_city["fuel_cost"] * grid.distance_centre) + (grid.distance_centre * param_city["cost_of_time"] * param_city["income"] / param_city["car_speed"]))
        elif param_policy["carbon_tax_implementation"][index] == 1:
            price_car = param_city["nb_commute"] * (param_city["fixed_cost_car"] + (param_city["fuel_cost"] * grid.distance_centre) + (param_policy["carbon_tax_value"] * grid.distance_centre) + (grid.distance_centre * param_city["cost_of_time"] * param_city["income"] / param_city["car_speed"]))
        
        if param_policy["public_transport_speed_implementation"][index] == 0:
            price_public_transport = param_city["nb_commute"] * ((param_city["public_transport_cost"] * grid.distance_centre) + (grid.distance_centre * param_city["cost_of_time"] * param_city["income"] / param_city["public_transport_speed"]))
        elif param_policy["public_transport_speed_implementation"][index] == 1:
            price_public_transport = param_city["nb_commute"] * ((param_city["public_transport_cost"] * grid.distance_centre) + (grid.distance_centre * param_city["cost_of_time"] * param_city["income"] / (param_policy["public_transport_speed_factor"] * param_city["public_transport_speed"])))
        
        prices = np.vstack((price_car, price_public_transport))
        transport_price = np.amin(prices, axis=0)
        mode = np.argmin(prices, axis=0)
    
        self.price_car = price_car
        self.price_public_transport = price_public_transport
        self.mode = mode
        self.transport_price = transport_price
        
    def real_city(self, param_city, param_policy, index):      
        if param_policy["carbon_tax_implementation"][index] == 0:
            prix_driving=param_city["duration_driving"]*param_city["income"]/ (3600 * 24)/365+param_city["distance_driving"]*(0.860)*7.18/100000
        elif param_policy["carbon_tax_implementation"][index] == 1:
            prix_driving=param_city["duration_driving"]*param_city["income"]/ (3600 * 24)/365+param_city["distance_driving"]*(0.860 + param_policy["carbon_tax_value"])*7.18/100000
        if param_policy["public_transport_speed_implementation"][index] == 0:
            prix_transit=param_city["duration_transit"]*param_city["income"]/ (3600 * 24)/365+param_city["distance_transit"]*0.860*7.18/100000
        elif param_policy["public_transport_speed_implementation"][index] == 1:
            prix_transit=(param_city["duration_transit"] / param_policy["public_transport_speed_factor"])*param_city["income"]/ (3600 * 24)/365+param_city["distance_transit"]*0.860*7.18/100000
        tous_prix=np.vstack((prix_driving,prix_transit))#les prix concaténés
        prix_transport=np.amin(tous_prix, axis=0)
        prix_transport[np.isnan(prix_transit)]=prix_driving[np.isnan(prix_transit)]
        prix_transport=prix_transport*2*365 # on l'exprime par rapport au revenu
        prix_transport=pd.Series(prix_transport)
        mode_choice=np.argmin(tous_prix, axis=0)
        mode_choice[np.isnan(prix_transit)]=0
        
        self.price_car = prix_driving
        self.price_public_transport = prix_transit
        self.mode = mode_choice
        self.transport_price = prix_transport

    def __repr__(self):
        return ("Trans:\nprice_car: {}\nprice_public_transport: {}\nmode: {}\ntransport_price: {}\n".format(
            self.price_car,self.price_public_transport,self.mode,self.transport_price))

class City:
    
    def __init__(self,nb_households=0,rent=0,dwelling_size=0,housing=0,density=0,R_0=0):
        self.nb_households = nb_households
        self.rent = rent
        self.dwelling_size = dwelling_size
        self.housing = housing
        self.density = density
        self.R_0 = R_0
        
    def __repr__(self):
        return ("Etat_initial:\n  nb_households: {}\n  rent: {}\n  dwelling_size: {}\n  housing: {}\n  density: {}\n  R_0:{}\n".format(
            self.nb_households,self.rent,self.dwelling_size,self.housing,self.density,self.R_0))

    def compute_outputs(self, R0, param_city, param_policy, trans, land, adjust_housing_supply, housing_supply = None):
        print(land.coeff_land)
        if adjust_housing_supply == 1:
            income_net_of_transport_costs = np.fmax(param_city["income"] - trans.transport_price, np.zeros(len(trans.transport_price)))   
            rent = (R0 * income_net_of_transport_costs**(1/param_city["beta"]) /param_city["income"]**(1/param_city["beta"]))
            np.seterr(divide = 'ignore', invalid = 'ignore')
            dwelling_size = param_city["beta"] * income_net_of_transport_costs / rent
            np.seterr(divide = 'warn', invalid = 'warn')
            dwelling_size[np.isnan(dwelling_size)] = 0
            #dwelling_size[dwelling_size > 300] = 300
            housing = land.coeff_land * ((param_city["A"]**(1/(1 - param_city["b"]))) * ((param_city["b"] / param_city["delta"] * rent) ** (param_city["b"]/(1 - param_city["b"]))))
            np.seterr(divide = 'ignore', invalid = 'ignore')
            density = copy.deepcopy(housing / dwelling_size)
            np.seterr(divide = 'warn', invalid = 'warn')        
            density[np.isnan(density)] = 0     
            nb_households = np.nansum(density)
        elif adjust_housing_supply == 0:
            income_net_of_transport_costs = np.fmax(param_city["income"] - trans.transport_price, np.zeros(len(trans.transport_price)))     
            rent = (R0 * income_net_of_transport_costs**(1/param_city["beta"]) /param_city["income"]**(1/param_city["beta"]))
            np.seterr(divide = 'ignore', invalid = 'ignore')
            dwelling_size = param_city["beta"] * income_net_of_transport_costs / rent
            np.seterr(divide = 'warn', invalid = 'warn')
            dwelling_size[np.isnan(dwelling_size)] = 0
            #dwelling_size[dwelling_size > 300] = 300
            housing = copy.deepcopy(housing_supply)
            np.seterr(divide = 'ignore', invalid = 'ignore')
            density = copy.deepcopy(housing / dwelling_size)
            np.seterr(divide = 'warn', invalid = 'warn')        
            density[np.isnan(density)] = 0 
            density[np.isinf(density)] = 0  
            nb_households = np.nansum(density)
            #housing = copy.deepcopy(housing_supply)
            #rent = ((housing / land.coeff_land) ** ((1 - param_city["b"]) / param_city["b"])) * (param_city["A"] ** (-1 / param_city["b"])) * (param_city["delta"] / param_city["b"])
            #income_net_of_transport_costs = np.fmax(param_city["income"] - trans.transport_price, np.zeros(len(trans.transport_price)))     
            #np.seterr(divide = 'ignore', invalid = 'ignore')
            #dwelling_size = param_city["beta"] * income_net_of_transport_costs / rent
            #density = copy.deepcopy(housing / dwelling_size)
            #np.seterr(divide = 'warn', invalid = 'warn')
            #density[np.isnan(density)] = 0
            #nb_households = np.nansum(density)

        self.nb_households = nb_households
        self.rent = rent
        self.dwelling_size = dwelling_size
        self.housing = housing
        self.density = density
        self.R0 = R0  