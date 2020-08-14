#!/usr/bin/env python
# coding: utf-8

# <h1>Capstone Project-The-Battle-of-Neighborhoods|<h1> <h2>Exploring Chennai, Tamil Nadu, India<h2>

# ![image.png](attachment:image.png)

# <h1>1.1 Introduction: <h1>
# <h3>Chennai, the capital city of Tamil Nadu- India, attracts many visitors either as tourists or as part of its large workforce. The vast majority claim Chennai is one of the best cities in India. We know that Chennai is popular for IIT and for being an IT and industrial hub. The city is also renowned for its passion for music. But, there’s more to the city than you think. From its varied culture and tradition, vibrant festivals, dainty delicacies to its quintessential “Chennai Tamil”, this city doesn’t fail to mesmerize the locals and the outsiders living here.  <h3>
# 
# <h2> 1.1. Business Problem: <h2>
#     
# <h3>The expectation of visitors to Chennai could be stated as follows:
#     
# a. What are the local food/ native cuisine available from restaurants in and around Chennai?
#     
# b. What services or value addition does the stop-over at a restaurant bring him, other than enjoying good food?
#     
# <h3>
# 

# <h2> 1.1 Target Audience: <h2>
# <h3> 1.2.1 The goal of this exercise is to give a simple recommendation to visitors of Chennai, Tamil Nadu: in which area they will find a large number or concentration of which types of restaurants. 
#     
#     
# 1.2.2 The target audience are investors who would like to start a group or chain of restaurants in and around Chennai. This analysis will give an idea, which area is crowded with restaurants and where is it beneficial to open a restaurant around Chennai.
#     
# 1.2.3 Road Travelers, to find reasonable refreshment joint where they can dine and also get along to refresh themselves in an amusement park – rest and refresh during their long road trip. <h3>

# ![image.png](attachment:image.png)

# <h1> 2. Data <h1>
# <h3> I will use foursquare API to collect data about restaurants in Chennai. I need data about different venues around Chennai. 
#     
# In order to gain that information we will use “Foursquare” locational information. Foursquare is a location data provider with information about all manner of venues and events within an area of interest. Such information includes venue names, locations, menus and even photos. As such, the foursquare location platform will be used as the sole data source since all the stated required information can be obtained through the API.
# 
# After finding the list of neighborhoods, we then connect to the Foursquare API to gather information about venues inside each and every neighborhood. 
# 
# The data retrieved from Foursquare contained information of venues within a specified distance of the longitude and latitude of the postcodes. 
#     
# Interactive maps are useful for data exploration and communicating research. Folium package will be used to:
#     a. Create a map centered at an inputted location
#     b. Create marker on the map
#     
# Markers can be extremely useful for storing information about locations on the map such as cross streets, building information, etc.
# 

# <h1> 3. Data Visualization and Exploration  <h1>

# In[2]:


from pandas.io.json import json_normalize  
# tranform JSON file into a pandas dataframe

#import folium 
# map rendering library

# import k-means from clustering stage
from sklearn.cluster import KMeans

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

get_ipython().system('pip install geopy')
get_ipython().system('pip install geocoder')
get_ipython().system('pip install folium')

import numpy as np
import pandas as pd
import json
from geopy.geocoders import Nominatim
import geocoder
import requests
import matplotlib.cm as cm
import matplotlib.colors as colors
from sklearn.cluster import KMeans
import folium
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.io.json import json_normalize
from sklearn.metrics import silhouette_score

get_ipython().run_line_magic('matplotlib', 'notebook')

print('All libraries imported.')


# <h3> 3.1. Using Nominatim to get co-ordinates of Chennai <h3>

# In[3]:


address = 'Chennai,IN'

geolocator = Nominatim()
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate are {}, {}.'.format(latitude, longitude))


# In[4]:


neighborhood_latitude=13.0801721
neighborhood_longitude=80.2838331


# In[5]:


LIMIT = 100 # limit of number of venues returned by Foursquare API
radius = 3000 # define radius
CLIENT_ID = 'P1QGGY5V2CC1LI5S4CIO5LCZD43D2KBV1TLE2RVEHAU2NQMF' # your Foursquare ID
CLIENT_SECRET = 'CJUSKELRYX23BUREM3I03YHD0APWLR0QONPXV43XYW245EAA' # your Foursquare Secret
VERSION = '20180604'
# create URL
url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    neighborhood_latitude, 
    neighborhood_longitude, 
    radius, 
    LIMIT)
url # display URL


# In[6]:


results = requests.get(url).json()
#results


# In[7]:


def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[13]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

nearby_venues.head(100)

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]
# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)
# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.shape
nearby_venues.head()


# <h3> 3.2. Visualizing near by venues using folium<h3>

# In[14]:



map_chn = folium.Map(location=[latitude, longitude], zoom_start=15)

# add markers to map
for lat, lng, label in zip(nearby_venues['lat'], nearby_venues['lng'], nearby_venues['name']):
    label = folium.Popup(label, parse_html=True)
    folium.RegularPolygonMarker(
        [lat, lng],
        number_of_sides=3,
        radius=10,
        popup=label,
        color='blue',
        fill_color='#0f0f0f',
        fill_opacity=0.7,
    ).add_to(map_chn)  
    
map_chn


# In[22]:


def getNearbyVenues(names, latitudes, longitudes):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
        
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
             CLIENT_ID, 
             CLIENT_SECRET, 
             VERSION, 
             lat, 
             lng, 
             radius, 
             LIMIT)
        
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[23]:


chennai_venues = getNearbyVenues(names=nearby_venues['name'],
                                 latitudes=nearby_venues['lat'],
                                 longitudes=nearby_venues['lng'])


# In[24]:


print(chennai_venues.shape)
chennai_venues.head()


# In[25]:


# check how many venues were returned for each neighborhood

chennai_venues.groupby('Neighborhood').count()


# In[26]:


# find out how many unique categories can be curated from all the returned venues

print('There are {} uniques categories.'.format(len(chennai_venues['Venue Category'].unique())))


# In[27]:


# one hot encoding
Chennai_onehot = pd.get_dummies(chennai_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
Chennai_onehot['Neighborhood'] = chennai_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [Chennai_onehot.columns[-1]] + list(Chennai_onehot.columns[:-1])
Chennai_onehot = Chennai_onehot[fixed_columns]

Chennai_onehot.head()


# In[29]:


# examine the new dataframe size.

Chennai_onehot.shape


# In[30]:


# group rows by neighborhood and by taking the mean of the frequency of occurrence of each category

Chennai_grouped = Chennai_onehot.groupby('Neighborhood').mean().reset_index()
Chennai_grouped


# In[31]:


Chennai_grouped.shape


# In[33]:


num_top_venues = 10 # Top common venues needed
for hood in Chennai_grouped['Neighborhood']:
    print("----"+hood+"----")
    temp = Chennai_grouped[Chennai_grouped['Neighborhood'] == hood].T.reset_index()
    temp.columns = ['venue', 'freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending = False).reset_index(drop = True).head(num_top_venues))
    print('\n')


# In[34]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending = False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[36]:


num_top_venues = 10
indicators = ['st', 'nd', 'rd']
# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))
# create a new dataframe
neighbourhoods_venues_sorted = pd.DataFrame(columns=columns)
neighbourhoods_venues_sorted['Neighborhood'] = Chennai_grouped['Neighborhood']
for ind in np.arange(Chennai_grouped.shape[0]):
    neighbourhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(Chennai_grouped.iloc[ind, :], num_top_venues)
neighbourhoods_venues_sorted.head(5)


# In[37]:


Chennai_grouped_clustering = Chennai_grouped.drop('Neighborhood', 1)


# In[38]:


# set number of clusters
kclusters = 5
# run k-means clustering
kmeans = KMeans(n_clusters = kclusters, random_state=0).fit(Chennai_grouped_clustering)
# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10]


# In[48]:


# add clustering labels
#neighbourhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)
chn_merged = nearby_venues
# match/merge SE London data with latitude/longitude for each neighborhood
chn_merged_latlong = chn_merged.join(neighbourhoods_venues_sorted.set_index('Neighborhood'), on = 'name')
chn_merged_latlong.head(5)


# In[60]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=14)
# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]
# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(chn_merged_latlong['lat'], chn_merged_latlong['lng'], chn_merged_latlong['categories'], chn_merged_latlong['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=15,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
display(map_clusters)


# In[61]:


# Cluster 1
chn_merged_latlong.loc[chn_merged_latlong['Cluster Labels'] == 0, chn_merged_latlong.columns[[1] + list(range(5, chn_merged_latlong.shape[1]))]]


# In[62]:


# Cluster 2
chn_merged_latlong.loc[chn_merged_latlong['Cluster Labels'] == 1, chn_merged_latlong.columns[[1] + list(range(5, chn_merged_latlong.shape[1]))]]


# In[63]:


# Cluster 3
chn_merged_latlong.loc[chn_merged_latlong['Cluster Labels'] == 2, chn_merged_latlong.columns[[1] + list(range(5, chn_merged_latlong.shape[1]))]]


# In[64]:


# Cluster 4
chn_merged_latlong.loc[chn_merged_latlong['Cluster Labels'] == 3, chn_merged_latlong.columns[[1] + list(range(5, chn_merged_latlong.shape[1]))]]


# In[65]:


# Cluster 5
chn_merged_latlong.loc[chn_merged_latlong['Cluster Labels'] == 4, chn_merged_latlong.columns[[1] + list(range(5, chn_merged_latlong.shape[1]))]]


# <h1> 4. Results <h1> 
#  <h3> The following are the results that are derived based on the 5 clusters:
# 1. As discussed in the introduction, data also supports the fact that Chennai is famous for food and movie.
# 2. Although, the Clusters have variations, the most common venue is the Indian Restaurants.

# <h1> 5. Discussion and Conclusion <h1>
#  Visitors of Chennai can enjoy Indian cuisine in all the 5 clusters. If the visitor is interested in visiting other venues other than restaurant then cluster 3 is the best suited to enjoy movie with food.    

# In[ ]:




