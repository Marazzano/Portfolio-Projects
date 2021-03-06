import pandas as pd
import os 
import numpy as np
import math 

import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.iolib.summary2 import summary_col
from stargazer.stargazer import Stargazer
from IPython.core.display import HTML



#Run this python to produce everything, and more, that is in the research results
  #to RUN this code you must: 
    # 1. download the "Colon_Ag_Dev_Research" folder 
    # 2. provide the location of the folder into the *root* variable below
    # 3. press RUN! (all produced data will go into the "Output" subfolder) 


#location of the "Colon_Ag_Dev_Research" Folder
root = ""

input_loc = "{}/Input".format(root)

output_loc = "{}/Output".format(root)




#this is the folder location where the rain data is stored.
rain_loc = "{}/Precip_Data".format(input_loc)


#location of data with Haryana district locations
distr_cord_loc = "{}/HaryanaDistrictsLocations.csv".format(input_loc)
#district area file location
distr_area_val_loc = "{}/Haryana_Districts_Area.csv".format(input_loc)




##################################
#
#Rainfall Portion of the paper
#
#
###############################




#initialize place to store rinafall
distr_rainfall = pd.read_csv(distr_cord_loc, usecols=["districts"],index_col = "districts")
distr_rain_shock = pd.read_csv(distr_cord_loc, usecols=["districts"],index_col = "districts");
distr_loc = pd.read_csv(distr_cord_loc , index_col = "districts")
distr_list = pd.read_csv(distr_cord_loc)["districts"].to_list()
                              
#years for calculations such as making averages
beg_year = 1975
end_year = 2017

reg_beg_year = 2004
reg_end_year = 2017 
for year in list(range(beg_year,end_year)):#i do not include reg_end_year in the range list because 2018 doesnt exist
    year_2 = year +1
    #obtaining file based off of year
    fileloc1 = os.path.join(rain_loc, 'precip.{}'.format(year))
    fileloc2 = os.path.join(rain_loc, 'precip.{}'.format(year_2))
    #creating dataframe for the years precipitation values
    year_1_df = pd.read_table(fileloc1, header=None, sep=r"\s+", usecols = [0,1,8,9,10,11,12,13])
    year_1_df.columns =["long","lat","m7",'m8','m9','m10','m11','m12']
    year_2_df = pd.read_table(fileloc2, header=None, sep=r"\s+", usecols = [0,1,2,3,4,5,6,7])
    year_2_df.columns =["long","lat","m1",'m2','m3','m4','m5','m6']
    
    #These lines are removing weather data that is not in Haryana
    indexNames = year_1_df[(year_1_df['long'] < distr_loc["long"].min())].index
    year_1_df.drop(indexNames , inplace=True)
    indexNames = year_1_df[(year_1_df['long'] > distr_loc["long"].max())].index
    year_1_df.drop(indexNames , inplace=True)
    indexNames = year_1_df[(year_1_df['lat'] < distr_loc["lat"].min())].index
    year_1_df.drop(indexNames , inplace=True)
    indexNames = year_1_df[(year_1_df['lat'] > distr_loc["lat"].max())].index 
    
    indexNames = year_2_df[(year_2_df['long'] < distr_loc["long"].min())].index
    year_2_df.drop(indexNames , inplace=True)
    indexNames = year_2_df[(year_2_df['long'] > distr_loc["long"].max())].index
    year_2_df.drop(indexNames , inplace=True)
    indexNames = year_2_df[(year_2_df['lat'] < distr_loc["lat"].min())].index
    year_2_df.drop(indexNames , inplace=True)
    indexNames = year_2_df[(year_2_df['lat'] > distr_loc["lat"].max())].index 
    
    
    
    #to retrieve the data
    rainfall_vals = []
    for distr in distr_list:
        rainfall= 0
        loc = distr_loc.loc[distr].to_list()
        year_1_rain = year_1_df.query("lat == {} and long == {}".format(loc[0],loc[1]))[["m7",'m8','m9','m10','m11','m12']]
        for val in year_1_rain.iloc[0]:
            rainfall =+ float(val)
        year_2_rain = year_2_df.query("lat == {} and long == {}".format(loc[0],loc[1]))[["m1",'m2','m3','m4','m5','m6']]
        for val in year_2_rain.iloc[0]:
            rainfall =+ float(val)
        rainfall_vals.append(rainfall)
        
    distr_rainfall[year] = rainfall_vals
#create quartile percentages for each row and a dataframe with the info
lower_qrt = distr_rainfall.quantile(q= .2, axis = 1).tolist()
upper_qrt = distr_rainfall.quantile(q= .8, axis = 1).tolist()    
 
temp_dict = {"districts": distr_list, "upper_qrt": upper_qrt, "lower_qrt" : lower_qrt}
district_qrt = pd.DataFrame(temp_dict).set_index("districts")



#drop years that aren't needed for the regression
distr_rainfall = distr_rainfall.drop(columns = list(range(beg_year,reg_beg_year)))
distr_rainfall = distr_rainfall.drop(columns = list(range(reg_end_year,end_year)))
 
distr_tot_rainfall = distr_rainfall.copy(deep=True)
 
#now we redifine the rainfall dataframe values depending on if it is in various values  
for district in distr_list:
    for year in distr_rainfall.columns.tolist():
        if distr_rainfall.at[district,year] >  district_qrt.at[district,"upper_qrt"]:
             distr_rainfall.at[district,year] = 1
             
        elif distr_rainfall.at[district,year] <  district_qrt.at[district,"lower_qrt"]:
             distr_rainfall.at[district,year] = -1
        
        else:
             distr_rainfall.at[district,year] = 0
    
#Regresion of wether or not rainfall data is a random variable. 
t0_t1 = []
for i in range(len(distr_tot_rainfall.iloc[0])-1): 
   temp_df = distr_tot_rainfall.iloc[:,[i,i+1]]
   temp_df.columns = ["t0", "t1"]
   t0_t1.append(temp_df)
t0_t1_df = pd.concat(t0_t1)
distr_rain_t0_t1 = pd.DataFrame(data = t0_t1_df,columns= ["t0", "t1"])

   
fit = ols('t1~ t0', data=distr_rain_t0_t1).fit()
stargazer = Stargazer([fit])
reg_table_loc = "{}/{}".format(output_loc,"Reg_Tables") 
with open("{}/Rainfal_t0_t1_regression.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())








    
###########
#
#
#
#This is the normall crop regression portion of the analysis
#
#
###########

 

norm_crop_loc = "{}/Norm_Crop_Data".format(input_loc)

#location of first file inorder to create columns and row indexis 
ex_norm_crop_loc = "{}/Ag_Prod_2009.csv".format(norm_crop_loc)

loc = "/Users/marazzanocolon/Desktop/Excel Ag Production/Excel_Ag_Prod 09-17/Ag_Prod_2009.csv"

out_reg_crop_prod = "{}/Norm_Crop_Prod".format(output_loc)




#create multidemensional df to create axis of df object
temp_df = pd.read_csv(ex_norm_crop_loc, header = None)
Type1 = temp_df.loc[0].to_list()[1:]
Type2 = temp_df.loc[1].to_list()[1:]
Type3 = temp_df.loc[2].to_list()[1:]
columns = pd.MultiIndex.from_arrays([Type1,Type2,Type3], names=["Grain_Cat", "Grain_Name", "APY"])
row = temp_df[0].to_list()[3:]
index = pd.MultiIndex.from_arrays([row], names=["Districts"])
data = pd.read_csv(ex_norm_crop_loc, header = None, skiprows = 3).drop(labels = 0, axis = 1)

#creating df to extract area
ag_area = pd.read_csv(distr_area_val_loc, index_col="Districts")

#create CSV files for the percent prod values
i = 0
df_index = pd.DataFrame(row, columns = ["Districts"])
for crop in columns.get_level_values(1).to_list():
    i += 1 #we need only every third value due to data configuration.
    if i%3==0:

        open("{}/{}_Prod.csv".format(out_reg_crop_prod,crop), 'w')
        df_index.to_csv("{}/{}_Prod.csv".format(out_reg_crop_prod,crop), mode='a', index=False)


#these are the years for the data that will be shown in the paper
reg_beg_year = 2005
reg_end_year = 2017

prod_loc = "/Users/marazzanocolon/Desktop/Excel Ag Production/Excel_Ag_Prod 09-17"
 
for year in range(reg_beg_year,reg_end_year+1):
    #print(year)
    
    fileloc = os.path.join(norm_crop_loc, 'Ag_Prod_{}.csv'.format(year))
    data = pd.read_csv(fileloc, header = None, skiprows = 3).drop(labels = 0, axis = 1).loc(axis= 1)[range(1,85)]
    work_df = pd.DataFrame(data)
    work_df.columns = columns
    work_df.index = index
    yearly_area_df = ag_area.loc(axis =1)["{}".format(year)].to_list()#has data for yearly perc areas
    
    i = 0
    for crop in columns.get_level_values(1).to_list(): 
        i += 1 #we need only evry third value due to data configuration.
        if i%3==0:

            yearly_area_df = ag_area.loc(axis =1)["{}".format(year)].to_list()
            temp_df = work_df.loc(axis=1)[:,"{}".format(crop),'A'].to_numpy().tolist()
            #for diagnosis
            temp_df_2 = work_df.loc(axis=1)[:,"{}".format(crop),'A'].to_numpy().tolist()
            crop_df= pd.read_csv("{}/{}_Prod.csv".format(out_reg_crop_prod,crop))
            crop_col= [None]*len(temp_df)
           
            for i in range(0,len(temp_df)):
                try: 
                    
                    
                    temp_df[i][0]= (float(temp_df[i][0])/yearly_area_df[i])*100
                except ValueError:
                    temp_df[i][0] = math.nan
                
            for i in range(0,len(temp_df)):
                crop_col[i] = temp_df[i][0]
                
                #used to see abnormally high data measurements
                if crop_col[i] >= 30:
                    if crop not in ["Total_Foodgrains","Total Cereals","Wheat","Rice"]: 
                        a_value = temp_df_2[i][0]
                        print(crop_col[i],distr_list[i],a_value,crop,year)
                    if crop == "Rice":
                        a_value = temp_df_2[i][0]
                        print(crop_col[i],distr_list[i],a_value,crop,year)
                if crop_col[i] >= 100 : #checks to make sure croparea/totalarea is >= 1
                    print(crop_col[i],year, crop)
                    
                #print(crop_col)
            crop_df[year] = crop_col
            crop_df.to_csv("{}/{}_Prod.csv".format(out_reg_crop_prod,crop), index = False)
           

yoy_file_loc = "{}/YoY_Ind_Crop_Prod".format(output_loc)
long_yoy_file_loc = "{}/Long_YoY_Ind_Crop_Prod".format(output_loc)

#this section creates the files where we get crop percent area           
for crop in columns.get_level_values(1).to_list():
    i += 1 #we need only every third value due to data configuration.
    if i%3==0:
        open('{}/{}_YoY_Prod.csv'.format(yoy_file_loc,crop), 'w')
        open('{}/{}_Long_YoY_Prod.csv'.format(long_yoy_file_loc,crop), 'w')
        
        df_index.to_csv('{}/{}_YoY_Prod.csv'.format(yoy_file_loc,crop), mode='a', index=False)
        
        #here we acess the yearly percent areas just created
        crop_df= pd.read_csv("{}/{}_Prod.csv".format(out_reg_crop_prod,crop))
        
        long_change_df = pd.DataFrame(columns = ["long_change"])
        
        for year in range(reg_beg_year,reg_end_year):
            
            year_change_df= pd.read_csv('{}/{}_YoY_Prod.csv'.format(yoy_file_loc,crop))
            year_0_col = crop_df.loc(axis=1)["{}".format(year)].to_numpy()
            year_1_col = crop_df.loc(axis=1)["{}".format(year+1)].to_numpy()
            year_change_df["{}".format(year+1)] = year_1_col - year_0_col #year+1 because I want to "year"'s change from previous
            # Finanlly add year to csv
            year_change_df.to_csv('{}/{}_YoY_Prod.csv'.format(yoy_file_loc,crop), index=False)
        
        year_0_col = crop_df.loc(axis=1)["{}".format(reg_beg_year+3)].to_numpy()
        yea_f_col = crop_df.loc(axis=1)["{}".format(reg_end_year)].to_numpy()
        
        long_change_df["long_change"] = yea_f_col - year_0_col
        long_change_df.to_csv('{}/{}_Long_YoY_Prod.csv'.format(long_yoy_file_loc,crop), index=False)
        
        plt.figure()
        fig = sns.histplot(data=pd.read_csv('{}/{}_Long_YoY_Prod.csv'.format(long_yoy_file_loc,crop)), x= "long_change")
        fig.set(title = crop)


######This is where we create the crop data in a format that can be used for regresion
        



data_column = ["Year", "YoY", "Districts", "Upper", "Lower", "Magnitude", "Total_Rainfall"]


norm_crop_reg_loc = "{}/Norm_Crop_Reg".format(output_loc)

for crop in columns.get_level_values(1).to_list():
    i += 1 #we need only every third value due to data configuration.
    
    if i%3==0:
        open('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,crop), 'w')
        Reg_Data_df = pd.DataFrame( columns = data_column)
        Crop_YoY_df = pd.read_csv('{}/{}_YoY_Prod.csv'.format(yoy_file_loc,crop),index_col = "Districts" )
       
        for year in range(reg_beg_year,reg_end_year):
            year_0 = year
            year_1 = year + 1
            row_df = pd.DataFrame( columns = data_column, index = [0]) #create empty df to fill the Reg_Data df
            row_df["Year"] = year_1
            for district in distr_list:
                row_df["Districts"] = district
                row_df["YoY"] = Crop_YoY_df.at[district,"{}".format(year_1)]
                row_df["Total_Rainfall"] = distr_tot_rainfall.at[district,year_0]
                #so we now fill out weather or not if the distr during "year" was Positive or Negative shock
                if distr_rainfall.at[district,year_0] == 1:
                    row_df["Upper"] = 1
                    row_df["Lower"] = 0
                    row_df["Magnitude"] = "Upper"
                    Reg_Data_df = Reg_Data_df.append(row_df)
                elif distr_rainfall.at[district,year_0] == -1:
                    row_df["Lower"] = 1
                    row_df["Upper"] = 0
                    row_df["Magnitude"] = "Lower"
                    Reg_Data_df = Reg_Data_df.append(row_df)
                else:
                    row_df["Lower"] = 0
                    row_df["Upper"] = 0
                    row_df["Magnitude"] = "Middle"
                    Reg_Data_df = Reg_Data_df.append(row_df)
                #add this row to the data frame
                
                
        #here we finally add the crops Year,District, Upper or Lower Shock variables to 
    Reg_Data_df.to_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,crop))
 


########
# 
#
#
#This is where HYV regression data is created
#
#
#
#######


HYV_crops=["Rice", "Rice", "Rice","Maize","Maize","Maize", "Bajra","Bajra","Bajra", "Wheat","Wheat","Wheat"]
HYV_data_type=["Total", "HYV","Percentage","Total", "HYV","Percentage","Total", "HYV","Percentage","Total", "HYV","Percentage"]

HYV_columns = pd.MultiIndex.from_arrays([HYV_crops, HYV_data_type], names=["HYV_crops", "HYV_data_type"])
HYV_index = index 

HYV_loc = "/Users/marazzanocolon/Desktop/Dev Econ Research Project/HYV Data/"

hyv_loc = "{}/HYV_Crop_Data".format(input_loc)

out_hyv_reg_loc = "{}/HYV_Reg_Data".format(output_loc)

reg_beg_year = 2005
reg_end_year = 2017




for crop in ["Rice", "Maize", "Bajra", "Wheat"]:
    HYV_crop_df= pd.DataFrame(columns = list(range(reg_beg_year,reg_end_year+1)), index=HYV_index)
    HYV_crop_df.index = HYV_index
    
    for year in range(reg_beg_year,reg_end_year+1):
        HYV_fileloc = os.path.join(hyv_loc, 'HYV_{}.csv'.format(year))
        data = pd.read_csv(HYV_fileloc, header = None, skiprows = 2)
        work_df = pd.DataFrame(data).drop(labels = 0, axis = 1).loc(axis= 1)[range(1,13 )]
        work_df.columns = HYV_columns
        work_df.index = HYV_index
        
        for district in distr_list:
            val = work_df.loc(axis=1)["{}".format(crop),'Percentage'].loc[district][0]
            try: 
                val = float(val)
            
            
            except ValueError: #this is how we deal with missing or error values
                val = math.nan
            
            if val > 90:
                print(val, district, year)
            
            HYV_crop_df[year][district]  =  val
                                                                                             
    
    YoY_HYV_crop_df= pd.DataFrame(columns = list(range(reg_beg_year+1,reg_end_year)), index=HYV_index)


        
    for year in range(reg_beg_year,reg_end_year):
        year_0_col = HYV_crop_df.loc(axis=1)[year].to_numpy()
        year_1_col = HYV_crop_df.loc(axis=1)[year+1].to_numpy()
        YoY_HYV_crop_df.loc(axis=1)[year+1] = year_1_col - year_0_col #year+1 because I want to "year"'s change from previous

    #finally we input that data in a format that can be used in regression while saving the files
    HYV_reg_data_column = ["Year", "YoY", "Districts", "Upper", "Lower", "Magnitude", "Total_Rainfall"]
    HYV_reg_df = pd.DataFrame( columns = HYV_reg_data_column) 
    open('{}/HYV_{}_Reg_data.csv'.format(out_hyv_reg_loc,crop), 'w')
    for year in range(reg_beg_year,reg_end_year):
            year_0 = year
            year_1 = year + 1
            row_df = pd.DataFrame( columns = data_column, index = [0])#create empty df to fill the Reg_Data df
            row_df["Year"] = year_1
            for district in distr_list:
                row_df["Districts"] = district
                row_df["YoY"] = YoY_HYV_crop_df.at[district,year_1]
                row_df["Total_Rainfall"] = distr_tot_rainfall.at[district,year_0]
                #so we now fill out whether or not if the distr during "year_0", the previous year, was Positive or Negative shock
                if distr_rainfall.at[district,year_0] == 1:
                    row_df["Upper"] = 1
                    row_df["Lower"] = 0
                    row_df["Magnitude"] = "Upper"
                    HYV_reg_df = HYV_reg_df.append(row_df)
                elif distr_rainfall.at[district,year_0] == -1:
                    row_df["Lower"] = 1
                    row_df["Upper"] = 0
                    row_df["Magnitude"] = "Lower"
                    HYV_reg_df = HYV_reg_df.append(row_df)
                else:
                    row_df["Lower"] = 0
                    row_df["Upper"] = 0
                    row_df["Magnitude"] = "Middle"
                    HYV_reg_df = HYV_reg_df.append(row_df)
                #add this row to the data frame
    HYV_reg_df.to_csv('{}/HYV_{}_Reg_data.csv'.format(out_hyv_reg_loc,crop), index = False)


###############
#
#
#This is the data analysis portion of the paper
#
#we create figures and tables, some of which can be found in the paper
#
#
#
##############







reg_table_loc = "{}/{}".format(output_loc,"Reg_Tables") 

no_fixed = []
no_fixed_dict = {}
with_fixed =[]
with_fixed_dict ={}
crop_list = []

area= []
area_dict= {}
area_fixed = []
area_fixed_dict = {}

ones = []

for crop in columns.get_level_values(1).to_list():
    i += 1 #we need only every third value due to data configuration.
    if i%3==0:
        crop_list.append(crop)
        ones.append(1)
        #print(crop)
        open('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,crop))
        data = pd.read_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,crop))
        try:
            fit = ols('YoY ~ C(Upper) + C(Lower)', data=data).fit()
            no_fixed.append(fit)
            no_fixed_dict[crop] = fit
            
            fit = ols('YoY ~ C(Upper) + C(Lower) + C(Districts)', data=data).fit()
            with_fixed.append(fit)
            with_fixed_dict[crop] = fit 
            
            fit = ols('YoY ~ Total_Rainfall', data=data).fit()
            area.append(fit)
            area_dict[crop] = fit
            
            fit = ols('YoY ~ Total_Rainfall + C(Districts)', data=data).fit()
            area_fixed.append(fit)
            area_fixed_dict[crop] = fit
        
        except ValueError:
            crop_list.pop()
            ones.pop()
    
#Make HYV Regressions with NO fixed effects tables 
stargazer = Stargazer(no_fixed)
stargazer.covariate_order(['C(Upper)[T.1]', "C(Lower)[T.1]",'Intercept'])
stargazer.add_custom_notes(['IMPORTANT : This regression has no fixed effects'])
stargazer.custom_columns(crop_list, ones)
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/Crop_Reg_NO_Fixed_Effects_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())

#Make HYV Regressions with fixed effects tables 
stargazer = Stargazer(with_fixed)
stargazer.covariate_order(['C(Upper)[T.1]', "C(Lower)[T.1]",'Intercept'])
stargazer.add_custom_notes(['IMPORTANT : This regression has fixed effects but they have been REMOVED from tabulation for viewing'])
stargazer.custom_columns(crop_list,ones)
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/Crop_Reg_Fixed_Effects_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())

#Investigates notabel results from first regression on Reg Crops

crop_order = ["Rice", "Bajra", "Maize", "Wheat", "Barley", "Toral_Foodgrains"]
notable_crop_col_name =["Rice (Wet)", "Bajra (Wet)", "Maize (Dry)", "Wheat (Dry)", "Barley (Dry)", "Total_Foodgrains"]

stargazer = Stargazer([area_dict["Rice"] ,area_dict["Bajra"]\
                       ,area_dict["Maize"] ,area_dict["Wheat"]\
                       ,area_dict["Barley"],area_dict["Total_Foodgrains"]])
                      
                       

stargazer.add_custom_notes(['IMPORTANT : This regression has no fixed effects'])
stargazer.custom_columns(notable_crop_col_name,[1]*len(notable_crop_col_name))
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/Crop_Reg_NO_Fixed_Effects_Notable_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())


stargazer = Stargazer([with_fixed_dict["Rice"] ,with_fixed_dict["Bajra"]\
                       ,with_fixed_dict["Maize"] ,with_fixed_dict["Wheat"]\
                       ,with_fixed_dict["Barley"],with_fixed_dict["Total_Foodgrains"]])


stargazer.add_custom_notes(['IMPORTANT : This regression has fixed effects'])
stargazer.custom_columns(notable_crop_col_name,[1]*len(notable_crop_col_name))
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/Crop_Reg_Fixed_Effects_Notable_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())


######Run same regressions but with rainfall data

stargazer = Stargazer(area)
stargazer.covariate_order(['Total_Rainfall','Intercept'])
stargazer.add_custom_notes(['IMPORTANT : This regression has no fixed effects'])
stargazer.custom_columns(crop_list, ones)
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/Crop_Reg_NO_Fixed_Effects_Area_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())

#Make HYV Regressions with fixed effects tables 
stargazer = Stargazer(area_fixed)
stargazer.covariate_order(['Total_Rainfall','Intercept'])
stargazer.add_custom_notes(['IMPORTANT : This regression has fixed effects but they have been REMOVED from tabulation for viewing'])
stargazer.custom_columns(crop_list,ones)
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/Crop_Reg_Fixed_Effects_Area_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())

#Investigates notabel results from first regression on Reg Crops

crop_order = ["Rice", "Bajra", "Maize", "Wheat", "Barley", "Toral_Foodgrains"]
notable_crop_col_name =["Rice (Wet)", "Bajra (Wet)", "Maize (Dry)", "Wheat (Dry)", "Barley (Dry)", "Total_Foodgrains"]

stargazer = Stargazer([area_dict["Rice"] ,area_dict["Bajra"]\
                       ,area_dict["Maize"] ,area_dict["Wheat"]\
                       ,area_dict["Barley"],area_dict["Total_Foodgrains"]])
                      
                       
stargazer.covariate_order(['Total_Rainfall','Intercept'])
stargazer.add_custom_notes(['IMPORTANT : This regression has no fixed effects'])
stargazer.custom_columns(notable_crop_col_name,[1]*len(notable_crop_col_name))
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/Crop_Reg_NO_Fixed_Effects_Notable_Area_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())


stargazer = Stargazer([area_fixed_dict["Rice"] ,area_fixed_dict["Bajra"]\
                       ,area_fixed_dict["Maize"] ,area_fixed_dict["Wheat"]\
                       ,area_fixed_dict["Barley"],area_fixed_dict["Total_Foodgrains"]])

stargazer.covariate_order(['Total_Rainfall','Intercept'])
stargazer.add_custom_notes(['IMPORTANT : This regression has fixed effects'])
stargazer.custom_columns(notable_crop_col_name,[1]*len(notable_crop_col_name))
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/Crop_Reg_Fixed_Effects_Notable_Area_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())




### Now we analyze and create data for HYV data!!!!!    
HYV_crops =   ["HYV Rice", " HYV Maize", "HYV Bajra", "HYV Wheat"]
fit_d = {}
fit_d2 = {}


area = {}
area_f = {}

#HYV Regressions 
for crop in ["Rice", "Maize", "Bajra", "Wheat"]:
    print(crop)
    data = pd.read_csv('{}/HYV_{}_Reg_data.csv'.format(out_hyv_reg_loc,crop))
    
    fit = ols('YoY ~ C(Upper) + C(Lower) + C(Districts)', data=data).fit()
    fit_d[crop] = fit
    
    fit = ols('YoY ~ C(Upper) + C(Lower)', data=data).fit()
    fit_d2[crop] = fit
    
    fit = ols('YoY ~ Total_Rainfall', data=data).fit()
    area[crop] = fit
    
    fit = ols('YoY ~ Total_Rainfall + C(Districts)', data=data).fit()
    area_f[crop] = fit
    

#Make HYV Regressions with fixed effects tables in HTML format
stargazer = Stargazer([fit_d["Bajra"],fit_d["Maize"],fit_d["Rice"],fit_d["Wheat"]])
stargazer.covariate_order(['C(Upper)[T.1]', "C(Lower)[T.1]",'Intercept'])
stargazer.add_custom_notes(['IMPORTANT : This regression has district fixed effects not shown here'])
stargazer.custom_columns(HYV_crops, [1,1,1,1])
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/HYV_Fixed_Effects_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())

#Make HYV Regressions with NO fixed effects tables in HTML format
stargazer = Stargazer([fit_d2["Bajra"],fit_d2["Maize"],fit_d2["Rice"],fit_d2["Wheat"]])
stargazer.covariate_order(['C(Upper)[T.1]', "C(Lower)[T.1]",'Intercept'])
stargazer.add_custom_notes(['IMPORTANT : This regression has no fixed effects'])
stargazer.custom_columns(HYV_crops, [1,1,1,1])
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/HYV_NO_Fixed_Effects_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())


#Make HYV AREA Regressions with fixed effects tables in HTML format
stargazer = Stargazer([area_f["Bajra"],area_f["Maize"],area_f["Rice"],area_f["Wheat"]])
stargazer.covariate_order(["Total_Rainfall", 'Intercept', ])
stargazer.add_custom_notes(['IMPORTANT : This regression has district fixed effects not shown here'])
stargazer.custom_columns(HYV_crops, [1,1,1,1])
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/HYV_Fixed_Effects_Area_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())

#Make HYV AREA Regressions with NO fixed effects tables in HTML format
stargazer = Stargazer([area["Bajra"],area["Maize"],area["Rice"],area["Wheat"]])
stargazer.covariate_order(["Total_Rainfall", 'Intercept', ])
stargazer.add_custom_notes(['IMPORTANT : This regression has no fixed effects'])
stargazer.custom_columns(HYV_crops, [1,1,1,1])
stargazer.rename_covariates({"C(Upper)[T.1]" :"Upper", "C(Lower)[T.1]": "Lower"})
with open("{}/HYV_NO_Fixed_Area_Effects_Table.html".format(reg_table_loc), "w") as file:
    file.write(stargazer.render_html())













#HERE we creat the category scatterplots
order = ["Lower", "Middle", "Upper"]


x= "Magnitude"
y= "YoY"
xlabel= "Rainfall Magnitude (t-1)"



temp_loc = '{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,crop)

crop = "Rice"
plt.figure()
rice_plot  = sns.catplot(x=x, y=y, \
                 data=pd.read_csv(temp_loc),\
                     order = order)
rice_plot.set(title='{}'.format("Rice"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)')

crop = "Maize"
plt.figure()
maize_plot = sns.catplot(x=x, y=y, \
                 data=pd.read_csv(temp_loc),\
                     order = order)
                     
maize_plot.set(title='{}'.format("Maize"),\
               xlabel=xlabel,\
              ylabel='YoY (pp)')

crop = "Bajra"    
plt.figure()
bajra_plot = sns.catplot(x=x, y=y, \
                 data=pd.read_csv(temp_loc),\
                     order = order)
bajra_plot.set(title='{}'.format("Bajra"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)')

crop = "Wheat"
plt.figure()
wheat_plot = sns.catplot(x=x, y=y, \
                 data=pd.read_csv(temp_loc),\
                     order = order)
wheat_plot.set(title='{}'.format("Wheat"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)')
    

    
    



ylim=(-100, 100)
#####PLOTS FOR HYV CATEGOTY PLOT MAGNITUDE DATA

xlabel= "Rainfall Magnitude (t-1)"
temp_loc = '{}/HYV_{}_Reg_data.csv'.format(out_hyv_reg_loc,crop) 

crop ="Rice"
hyv_rice_plot  = sns.catplot(x="Magnitude", y="YoY", \
                 data=pd.read_csv(temp_loc),\
                 order=order)
hyv_rice_plot.set(title='HYV {}'.format("Rice"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)')

crop = "Maize"    
hyv_maize_plot = sns.catplot(x="Magnitude", y="YoY", \
                 data=pd.read_csv(temp_loc),\
                 order=order)
    
hyv_maize_plot.set(title='HYV {}'.format("Maize"),\
              xlabel='Magnitude of Rainfall Shock in Previous Year',\
              ylabel='YoY (pp)')

crop = "Bajra"
hyv_bajra_plot = sns.catplot(x="Magnitude", y="YoY", \
                 data=pd.read_csv(temp_loc),\
                 order=order)

hyv_bajra_plot.set(title='HYV {}'.format("Bajra"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)')   

crop = "Wheat"
hyv_wheat_plot = sns.catplot(x="Magnitude", y="YoY", \
                 data=pd.read_csv(temp_loc),\
                 order=order)
    
hyv_wheat_plot.set(title='HYV {}'.format("Wheat"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)')   

    
####Plots for the regular regression results

#Rice, Wheat, Maize , Bajra 
xlabel = "Total Rainfall (t-1, mm)"



rice_plot  = sns.catplot(x="Magnitude", y="YoY", \
                 data=pd.read_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,"Rice")),\
                 order=order)
rice_plot.set(title='{}'.format("Rice"),\
              xlabel='Magnitude of Rainfall Shock in Previous Year',\
              ylabel='YoY (pp)',ylim=ylim)

maize_plot = sns.catplot(x="Magnitude", y="YoY", \
                 data=pd.read_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,"Maize")),\
                 order=order)
    
maize_plot.set(title='{}'.format("Maize"),\
              xlabel='Magnitude of Rainfall Shock in Previous Year',\
              ylabel='YoY (pp)',ylim=ylim)

bajra_plot = sns.catplot(x="Magnitude", y="YoY", \
                 data=pd.read_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,"Bajra")),\
                 order=order)

bajra_plot.set(title='{}'.format("Bajra"),\
              xlabel='Magnitude of Rainfall Shock in Previous Year',\
              ylabel='YoY (pp)',ylim=ylim)    

wheat_plot = sns.catplot(x="Magnitude", y="YoY", \
                 data=pd.read_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,"Wheat")),\
                 order=order)

wheat_plot.set(title='{}'.format("Wheat"),\
              xlabel='Magnitude of Rainfall Shock in Previous Year',\
              ylabel='YoY (pp)',ylim=ylim)    

  
    
    
#####Plots for the rainfall regression of the normal crops   
    
#Rice, Wheat, Moong , Bajra 

plt.figure()
rainfall_rice_plot  = sns.scatterplot(x="Total_Rainfall", y="YoY", \
                 data=pd.read_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,"Rice")))
    
rainfall_rice_plot.set(title='{}'.format("Rice"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)',ylim=ylim)
plt.figure()
rainfall_maize_plot = sns.scatterplot(x="Total_Rainfall", y="YoY", \
                 data=pd.read_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,"Maize")))
    
rainfall_maize_plot.set(title='{}'.format("Maize"),\
               xlabel=xlabel,\
              ylabel='YoY (pp)',ylim=ylim)
plt.figure()
rainfall_bajra_plot = sns.scatterplot(x="Total_Rainfall", y="YoY", \
                 data=pd.read_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,"Bajra")))

rainfall_bajra_plot.set(title='{}'.format("Bajra"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)',ylim=ylim)  
plt.figure()
rainfall_wheat_plot = sns.scatterplot(x="Total_Rainfall", y="YoY", \
                 data=pd.read_csv('{}/{}_Reg_Data.csv'.format(norm_crop_reg_loc,"Wheat")))

rainfall_wheat_plot.set(title='{}'.format("Wheat"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)',ylim=ylim)     

    
#PLots for the HYV TOTAL RAINFALL DATA  
plt.figure()
rainfall_hyv_rice_plot  = sns.scatterplot(x="Total_Rainfall", y="YoY", \
                 data=pd.read_csv('{}/HYV_{}_Reg_data.csv'.format(out_hyv_reg_loc,"Rice")))
    
rainfall_hyv_rice_plot.set(title='{}'.format("HYV Rice"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)',ylim=ylim)
plt.figure()
rainfall_hyv_maize_plot = sns.scatterplot(x="Total_Rainfall", y="YoY", \
                 data=pd.read_csv('{}/HYV_{}_Reg_data.csv'.format(out_hyv_reg_loc,"Maize")))
    
rainfall_hyv_maize_plot.set(title='{}'.format("HYV Maize"),\
               xlabel=xlabel,\
              ylabel='YoY (pp)',ylim=ylim)
plt.figure()
rainfall_hyv_bajra_plot = sns.scatterplot(x="Total_Rainfall", y="YoY", \
                 data=pd.read_csv('{}/HYV_{}_Reg_data.csv'.format(out_hyv_reg_loc,"Bajra")))

rainfall_hyv_bajra_plot.set(title='{}'.format("HYV Bajra"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)',ylim=ylim)  
plt.figure()
rainfall_hyv_wheat_plot = sns.scatterplot(x="Total_Rainfall", y="YoY", \
                 data=pd.read_csv('{}/HYV_{}_Reg_data.csv'.format(out_hyv_reg_loc,"Wheat")))

rainfall_hyv_wheat_plot.set(title='{}'.format("HYV Wheat"),\
              xlabel=xlabel,\
              ylabel='YoY (pp)',ylim=ylim)     



    
    
    
print("CONGRATS!!!We are Done Now")
    

    




