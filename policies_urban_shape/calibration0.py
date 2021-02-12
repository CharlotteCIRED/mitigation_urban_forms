# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 10:50:10 2021

@author: Charlotte Liotta
"""

# %% Packages and Paths

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy as sc
from scipy import optimize
from pathlib import Path
from statsmodels.regression.linear_model import OLS
from matplotlib.backends.backend_pdf import PdfPages
import time #to measure execution times
from statsmodels.api import OLS
#cf. (https://pythran.readthedocs.io/en/latest/)
import pythran
import os #pour pouvoir créer des dossiers
import numdifftools as nd

COEFF_URB = 0.62
HOUSEHOLD_SIZE = 1
INTEREST_RATE = 0.05

paths_data = define_paths_data()
list_city = list_of_cities_and_databases((paths_data["path_data_quentin"]) ,'cityDatabase')#cityDatabase_intermediaire
path_data = paths_data["path_data"]

(country, density, rents_and_size, land_use,
 income, conversion_rate, driving, transit,
 grille, centre, distance_cbd) = import_data(list_city, paths_data, city)

prix_driving=driving.Duration*income/ (3600 * 24)/365+driving.Distance*0.860*7.18/100000
prix_transit=transit.Duration*income/ (3600 * 24)/365+transit.Distance*0.860*7.18/100000
tous_prix=np.vstack((prix_driving,prix_transit))#les prix concaténés
prix_transport=np.amin(tous_prix, axis=0)
prix_transport[np.isnan(prix_transit)]=prix_driving[np.isnan(prix_transit)]
prix_transport=prix_transport*2*365 # on l'exprime par rapport au revenu
prix_transport=pd.Series(prix_transport)
mode_choice=np.argmin(tous_prix, axis=0)
mode_choice[np.isnan(prix_transit)]=0

#Put them into a "city" structure
dataCity = CityClass(
    density = density.loc[:,density.columns.str.startswith("density")].squeeze(),
    rent = (rents_and_size.medRent / conversion_rate) * 12,
    size = rents_and_size.medSize,#
    urb = (land_use.OpenedToUrb / land_use.TotalArea) * COEFF_URB,
    income = income,
    duration = prix_transport,
    duration_driving=driving.Duration,
    distance_driving=driving.Distance,
    duration_transit=transit.Duration,
    distance_transit=transit.Distance,
    transport_price = prix_transport,
    mode_choice=mode_choice
    )

dataCity.total_population=np.nansum(dataCity.density)

grid = Grid(grille.XCOORD / 1000,
            grille.YCOORD / 1000,
            distance_cbd,
            grille.AREA / 1000000)

selected_cells = np.array(dataCity.duration.notnull() & (dataCity.duration!=0)
                                 & dataCity.urb.notnull()  & (dataCity.urb!=0)
                                 & dataCity.rent.notnull()  & (dataCity.rent!=0)
                                 & dataCity.size.notnull()  & (dataCity.size!=0)
                                 & dataCity.density.notnull() & (dataCity.density!=0)
                                 )

result_calibration = calibration(dataCity,
                                 INTEREST_RATE,
                                 selected_cells,
                                 HOUSEHOLD_SIZE)

calibratedParameters = {
    "beta" : result_calibration.x[0],
    "Ro" : result_calibration.x[1],
    "b" : result_calibration.x[2],
    "kappa" : result_calibration.x[3],
    "HouseholdSize" : HOUSEHOLD_SIZE
    }

np.save('C:/Users/Charlotte Liotta/Desktop/these/Sorties/database/calibratedParameters_kazan.npy', calibratedParameters)

income_net_of_transport_costs = np.fmax(dataCity.income - dataCity.transport_price, np.zeros(len(dataCity.transport_price)))   
rent = (calibratedParameters["Ro"] * income_net_of_transport_costs**(1/calibratedParameters["beta"]) /dataCity.income **(1/calibratedParameters["beta"]))
dwelling_size = calibratedParameters["beta"] * income_net_of_transport_costs / rent
housing = dataCity.urb * ((calibratedParameters["kappa"]**(1/(1 - calibratedParameters["b"]))) * ((calibratedParameters["b"] / INTEREST_RATE * rent) ** (calibratedParameters["b"]/(1 - calibratedParameters["b"]))))
density = housing / dwelling_size

plt.scatter(grid.distance_cbd, dataCity.rent)
plt.scatter(grid.distance_cbd, rent)

plt.scatter(grid.distance_cbd, dataCity.density)
plt.scatter(grid.distance_cbd, density)

plt.scatter(grid.distance_cbd, dataCity.size)
plt.scatter(grid.distance_cbd, dwelling_size)