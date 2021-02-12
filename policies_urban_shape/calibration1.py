# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 10:52:09 2021

@author: Charlotte Liotta
"""

def define_paths_data():
    """
    create the paths to local data
    it would be better to rely on pathlib package to import the path in the correct format.
    cf. https://medium.com/@ageitgey/python-3-quick-tip-the-easy-way-to-deal-with-file-paths-on-windows-mac-and-linux-11a072b58d5f

    """
    path_data='C:/Users/Charlotte Liotta/Desktop/eco_urbaine/2. Donnees/'
    #path_data='/Users/vincentviguie/Documents/code/20 04 code charlotte 2/data_ordonnees/'
    path_plots='C:/Users/Charlotte Liotta/Desktop/these/'
    #path_plots='/Users/vincentviguie/Documents/code/20 04 code charlotte 2/test_plots'
    paths_data={
        "path_data" : path_data,
        "path_data_quentin": path_data + '/City_dataStudy_V02042020/City_dataStudy/',
        "path_data_city" : path_data + '/City_dataStudy_V02042020/City_dataStudy/' + 'Data/',
        "path_plots" : Path(path_plots)
        }
    return paths_data

def list_of_cities_and_databases(path_data_quentin,name):
    """ Import a list of cities for which data are available.
    
    Import the characteristics of the real estate, density and transport
    databases for each city.
    Select the most recent real estate database.
    Exclude Sales databases.
    Select Baidu transport database for chinese cities.
    """
    
    list_city = pd.read_csv(path_data_quentin + 'CityDatabases/'+name+'.csv')   
    list_city = list_city[['City', 'Country', 'GridEPSG', 'TransportSource', 
                       'RushHour', 'TransactionType', 'TransactionSource', 
                       'TransactionMonth', 'TransactionYear']]    
    list_city = list_city[list_city.TransactionType.eq('Rent')]
    #list_city = list_city[list_city.TransactionType.eq('Sale')]
    
    for city in np.unique(list_city.City):        
        most_recent_data = max(list_city.TransactionYear[list_city.City == city])
        i = list_city[((list_city.City == city) & 
                       (list_city.TransactionYear < most_recent_data))].index
        list_city = list_city.drop(i)
        
    for city in list_city.City[list_city.TransportSource == 'Baidu']:
        i = list_city[((list_city.City == city) & 
                       (list_city.TransportSource == 'Google'))].index
        list_city = list_city.drop(i)
    
    return list_city

def import_data(list_city, paths_data, city):
    """ Import all data for a given city """
    
    
    path_data=paths_data["path_data"]
    path_data_city=paths_data["path_data_city"]
    
    country = list_city.Country[list_city.City == city].iloc[0]
    proj = str(int(list_city.GridEPSG[list_city.City == city].iloc[0]))
    transport_source = list_city.TransportSource[list_city.City == city].iloc[0]
    hour = list_city.RushHour[list_city.City == city].iloc[0]
    source_ici = list_city.TransactionSource[list_city.City == city].iloc[0]
    year = str(int(list_city.TransactionYear[list_city.City == city].iloc[0]))
    month = list_city.TransactionMonth[list_city.City == city].iloc[0]
    
    #Import data
    density = pd.read_csv(path_data_city + country + '/' + city +
                      '/Population_Density/grille_GHSL_density_2015_' +
                      str.upper(city) + '.txt', sep = '\s+|,', engine='python')
    
    rents_and_size = pd.read_csv(path_data_city + country + '/' + city + 
                              '/Real_Estate/GridData/griddedRent_' + source_ici + 
                              '_' + month + year + '_' + str.upper(city) + '.csv')

    
    land_use = pd.read_csv(path_data_city + country + '/' + city + 
                       '/Land_Cover/gridUrb_ESACCI_LandCover_2015_' + 
                       str.upper(city) + '_' + proj +'.csv')
    
    data_gdp = pd.read_excel(path_data + 'gdp_capita_ppp.xlsx')
    
    income = data_gdp.oecd[data_gdp.city == city].iloc[0]    
    if np.isnan(income):
        income = data_gdp.brookings[data_gdp.city == city].iloc[0]
    if np.isnan(income):
        income = data_gdp.world_bank[data_gdp.city == city].iloc[0]
    
    conversion_to_ppa = pd.read_csv(path_data + 'conversion_ppa.csv')
    conversion_rate = conversion_to_ppa.conversion_ppa[conversion_to_ppa.Country == country].iloc[0]
    
    driving = pd.read_csv(path_data_city + country + '/' + city + 
                      '/Transport/interpDrivingTimes' + transport_source + '_' 
                      + city + '_' + hour + '_' + proj +'.csv')
    
    transit = pd.read_csv(path_data_city + country + '/' + city + 
                      '/Transport/interpTransitTimesGoogle_'+ city + '_' + 
                      hour + '_' + proj + '.csv')
    
    grille = pd.read_csv(path_data_city + country + '/' + city + '/Grid/grille_' + 
                     str.upper(city) + '_finale.csv')
    
    centre = pd.read_csv(path_data_city + country + '/' + city + '/Grid/Centre_' 
                     + str.upper(city) + '_final.csv').to_numpy()
    
    if city == 'Prague' or city == 'Tianjin' or city == 'Paris':
        distance_cbd = ((grille.XCOORD / 1000 - centre[0, 0] / 1000) ** 2 + 
                (grille.YCOORD / 1000 - centre[0, 1] / 1000) ** 2) ** 0.5
    elif city == 'Buenos_Aires' or city == 'Yerevan':
        distance_cbd = ((grille.XCOORD / 1000 - centre[0, 3] / 1000) ** 2 + 
                (grille.YCOORD / 1000 - centre[0, 4] / 1000) ** 2) ** 0.5
    else:
        distance_cbd = ((grille.XCOORD / 1000 - centre[0, 1] / 1000) ** 2 + 
                (grille.YCOORD / 1000 - centre[0, 2] / 1000) ** 2) ** 0.5
    
    print("Données pour " + city + " chargées")
    
    return country, density, rents_and_size, land_use, income, conversion_rate, driving, transit, grille, centre, distance_cbd#,prices_and_size

def calibration(dataCity, INTEREST_RATE, selected_cells, HOUSEHOLD_SIZE):
    
    bounds = ((0.01,0.8), #beta
              (0.001,None), #Ro
              (0.0,0.95), #b
              (0.001, None) #kappa
              )
    
    X0 = np.array([0.25, #beta
                   300, #Ro
                   0.64, #b
                   2] )  
    
    def minus_log_likelihood(X0):
    
        (log_simul_rent,log_simul_size,log_simul_density)=model(X0, dataCity,INTEREST_RATE, selected_cells,HOUSEHOLD_SIZE)
    
        
        sortie3,ll_R,ll_D,ll_Q,ll_R_detaille,ll_D_detaille,ll_Q_detaille = log_likelihood(log_simul_rent,log_simul_size,log_simul_density,
                                dataCity,
                                selected_cells)
    
        return -sortie3
        
    result_calibration = optimize.minimize(minus_log_likelihood, X0, bounds=bounds) 
    
    return result_calibration

def model(X0, dataCity, INTEREST_RATE, selected_cells, HOUSEHOLD_SIZE):
    """ Compute Log-Likelihood on rents, density and dwelling size.
    
    Simplified likelihood: we assume no correlation between the error terms
    on rents, densities and dwelling sizes.
    """    

    ## Starting point
    beta = X0[0]
    Ro = X0[1]
    b = X0[2]
    kappa = X0[3]
    
    a=1-b
    
    #we convert all panda dataframes to numpy so that everything is quicker
    trans_price = dataCity.transport_price.to_numpy()
    urb = dataCity.urb.to_numpy()
    income = dataCity.income  
    
    ## On simule les loyers, tailles des logements et densites
    #log_simul_rent = np.log(Ro) + (1 / beta) * (np.log(1 - (trans_price[selected_cells] / income)))
    #log_simul_size = np.log(HOUSEHOLD_SIZE) + np.log(beta * (income-(trans_price[selected_cells]))) - (log_simul_rent)
    #warning, the truye formulla is (1/a*np.log(kappa)
    #I changed it also in declare_structure
    #log_simul_density = ((1/a)*np.log(kappa)) + ((b / a) * (np.log(b / INTEREST_RATE))) + ((b / a) * (log_simul_rent)) - (log_simul_size - np.log(HOUSEHOLD_SIZE))+ np.log(urb[selected_cells])

    income_net_of_transport_costs = np.fmax(income - trans_price, np.zeros(len(trans_price)))             
    rent = (Ro * income_net_of_transport_costs**(1/beta) /income**(1/beta))
    np.seterr(divide = 'ignore', invalid = 'ignore')
    dwelling_size = beta * income_net_of_transport_costs / rent
    np.seterr(divide = 'warn', invalid = 'warn')
    #dwelling_size[np.isnan(dwelling_size)] = 0
    #dwelling_size[dwelling_size > 300] = 300
    housing = urb * ((kappa**(1/a)) * (((b / INTEREST_RATE) * rent) ** (b/(a))))
    np.seterr(divide = 'ignore', invalid = 'ignore')
    density = copy.deepcopy(housing / dwelling_size)
    np.seterr(divide = 'warn', invalid = 'warn')        
    #density[np.isnan(density)] = 0     
    return (np.log(rent),np.log(dwelling_size),np.log(density))        

def log_likelihood(log_simul_rent,log_simul_size,log_simul_density, dataCity, selected_cells):
    """ Compute Log-Likelihood on rents, density and dwelling size based on model oputputs.
    
    We assume a trivariate normal distribution. Measurement error on rents,
    but not on dwellings sizes. No spatial autocorrelation. Does not account
    for maximum and minimum.
    """
    
    rent = dataCity.rent.to_numpy()
    density = dataCity.density.to_numpy()
    size = dataCity.size.to_numpy()

    x_R = (np.log(rent[selected_cells])) - log_simul_rent[selected_cells]
    x_Q = (np.log(size[selected_cells])) - log_simul_size[selected_cells] 
    x_D = (np.log(density[selected_cells])) - log_simul_density[selected_cells]
    
    sigma_r2 = (1/sum(selected_cells)) * np.nansum(x_R ** 2)
    sigma_q2 = (1/sum(selected_cells)) * np.nansum(x_Q ** 2)
    sigma_d2 = (1/sum(selected_cells)) * np.nansum(x_D ** 2)
        
    (ll_R, ll_R_detaille) = ll_normal_distribution_detaille(x_R, sigma_r2)
    (ll_Q, ll_Q_detaille) = ll_normal_distribution_detaille(x_Q, sigma_q2)
    (ll_D, ll_D_detaille) = ll_normal_distribution_detaille(x_D, sigma_d2)
    
    return (ll_R + ll_Q + ll_D,
            ll_R,
            ll_D,
            ll_Q,
            ll_R_detaille,
            ll_D_detaille,
            ll_Q_detaille)

def ll_normal_distribution_detaille(error, sigma2):
    """ normal distribution probability density function of variable `error` and coeff
    sigma `sigma`
    
    """
    log_pdf = -(error ** 2)/(2 * (sigma2))-1/2*np.log(sigma2)-1/2*np.log(2 * np.pi)
    return (np.nansum(log_pdf),log_pdf)

class CityClass:  
    """Classe définissant une ville caractérisée par :
        - les densités en chaque pixel
        - les loyers en chaque pixel
        - les tailles des logements en chaque pixel
        - la proportion de chaque pixel qui est urbanisable
        - le revenu moyen à l échelle de la ville
        - les temps de transport au centre depuis chaque pixel
        """
        
    def __init__(self,
                 density=0,
                 rent=0,
                 size=0,
                 urb=0,
                 income=0,
                 duration=0,
                 prices=0,
                 duration_driving=0,
                 distance_driving=0,
                 duration_transit=0,
                 distance_transit=0,
                 mode_choice=0,
                 transport_price=0
                 ):
        self.density = density
        self.rent = rent
        self.size = size
        self.urb = urb
        self.income = income
        self.duration = duration
        self.prices=prices #real estate prices
        self.duration_driving=duration_driving
        self.distance_driving=distance_driving
        self.duration_transit=duration_transit
        self.distance_transit=distance_transit
        self.mode_choice=mode_choice
        self.transport_price = transport_price
        
    