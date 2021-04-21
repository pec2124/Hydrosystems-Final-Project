#Peter Cruz-Grace pec2124
"""Takes USGS Well Data and creates a dictionary of this form:
    {"Site":(float(Latitude),float(Longitude)),[int(Date measureed(yyyymmdd)),float(Well level in ft)"""

#For the csv use MOF.used.wl13.all.csv because it has all the other csv files added to it
def Make_Dict(csv="MOF.used.wl13.all.csv"):
    file=open(csv,"r")
    

    info_dict={} #Dictionary I want to make

    for line in file:
        try:
            split=line.split(",")
            site=split[2]
            latitude=float(split[5])
            longitude=float(split[6])
            date=int(split[18][:4])
            level=float(split[20])
        
        
            if site in info_dict:
                info_dict[site][1][date]=level
            else:
                info_dict[site]=[(latitude,longitude),{date:level}]
                
        except ValueError:
            pass
    file.close()
    
    return info_dict

#date_level_di can be reached with info_dict.values()[1]
def Average_Well_Height(date_level_di):
    avg_height=sum(date_level_di.values())/len(date_level_di)
    return avg_height

def Change_in_Well_Height(date_level_di):
    from operator import itemgetter

    pairs = list(date_level_di.items())
    #sorted() removes any repeated measurements so there is only one value each year
    sorted_pairs=sorted(pairs,key=itemgetter(0))
    j=0
    yearly_change_di={}
    while j<len(sorted_pairs)-1:
        if len(sorted_pairs[j])<=2:
            year_0=sorted_pairs[j][0]
            year_1=sorted_pairs[j+1][0]
            level_0=sorted_pairs[j][1]
            level_1=sorted_pairs[j+1][1]
            change_ft=(level_1-level_0)/(year_1-year_0)
            change=change_ft*304.8
            yearly_change_di[year_1]=change
            j+=1
        else:
            year_0=sorted_pairs[j][0]
            yearly_change_di[year_0]=sorted_pairs[j][1]
            j+=1
    
    return yearly_change_di

def Find_Change_In_All_Wells():
    from statistics import mean
    csv="MOF.used.wl13.all.csv"
    info_dict=Make_Dict(csv)
    date_level_index=1
    for site in info_dict:
        date_level_di=info_dict[site][date_level_index]
        avg_well_height=Average_Well_Height(date_level_di)
        well_height_change=Change_in_Well_Height(date_level_di)
        if len(well_height_change.values())==0:
            average_well_change=0
        else:
            average_well_change=mean(well_height_change.values())

        complete_dict=info_dict.copy()
        complete_dict[site].append(avg_well_height)
        complete_dict[site].append(well_height_change)
        complete_dict[site].append(average_well_change)
        
        
#complete_dict-->{Site:[(Latitude,Longitude),{Year:float(Well height in ft) for each year starting with latest year},float(average well heght over time),{Year:Change in well height for that year starts with earliest year},float(average well change over period)]}
    return complete_dict

def Year_filter():
    complete_dict=Find_Change_In_All_Wells()
    year_lat={}
    year_long={}
    year_change={}
    for i in complete_dict:
        for j in list(complete_dict[i][3].keys()):
            year=j
            change=complete_dict[i][3][j]
            lat_int=int(complete_dict[i][0][0])
            long_int=int(complete_dict[i][0][1])
            lat_str=str(lat_int)
            long_str=str(long_int)
            if len(long_str) > 6:
                long_deg=-float(long_str[0:3])
                long_min=-float(long_str[3:5])/60
                long_sec=-float(long_str[5:7])/3600
                long_dec=long_deg+long_min+long_sec
            else:
                long_deg=-float(long_str[0:2])
                long_min=-float(long_str[2:4])/60
                long_sec=-float(long_str[4:6])/3600
                long_dec=long_deg+long_min+long_sec
                
            lat_deg=float(lat_str[0:2])
            lat_min=float(lat_str[2:4])/60
            lat_sec=float(lat_str[4:6])/3600
            lat_dec=lat_deg+lat_min+lat_sec
            
            if year in year_lat:
                year_lat[year].append(lat_dec)
                year_long[year].append(long_dec)
                year_change[year].append(change)
            else:
                year_lat[year]=[lat_dec]
                year_long[year]=[long_dec]
                year_change[year]=[change]
                
        
    return (year_lat, year_long, year_change)

def Make_Map(lat_li,long_li,change_li,year):
    font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 24,
        }
    import cartopy.crs as crs
    import cartopy.feature as cfeature
    import matplotlib.pyplot as plt
    
    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(1,1,1, projection=crs.PlateCarree())
    ax.set_extent([-110,-90,30,45], crs.PlateCarree())
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.STATES)
    ax.add_feature(cfeature.LAND,color='lightgrey')
    ax.add_feature(cfeature.LAKES,color='skyblue')
    ax.add_feature(cfeature.RIVERS, edgecolor='blue')

    plt.scatter(x=long_li,y=lat_li,c=change_li, cmap='Spectral',vmin=-1200,vmax=1200,transform=crs.PlateCarree())
    plt.colorbar()
    plt.title('Change in Ogallala Aquifer Wells [mm] in {}'.format(str(year)),fontdict=font)
    
    
    plt.show()
    
def Mapper():
    year_lat,year_long,year_change=Year_filter()
    for i in year_lat:
        year=i
        Make_Map(year_lat[year],year_long[year],year_change[year],year)
    
def csv_writer():
    import csv
    
    complete_dict=Find_Change_In_All_Wells()
    datapoints=[]
    for i in complete_dict:
        for j in complete_dict[i][3]:
            site=i
            lat=complete_dict[i][0][0]
            long=complete_dict[i][0][1]
            year=j
            avg_well_height=complete_dict[i][2]
            well_change=complete_dict[i][3][j]
            datapoints.append({'Site':site,'Year':year,'Lattitude':lat,'Longitude':long,'Well Height Change':well_change, 'Average Well Height':avg_well_height})
    
    with open('yearly_storage_change.csv','w') as csvfile:
        fieldnames=['Site','Year','Lattitude','Longitude','Well Height Change', 'Average Well Height']
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames,extrasaction='raise')

        writer.writeheader()
        writer.writerows(datapoints)

