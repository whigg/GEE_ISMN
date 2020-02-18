import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from ismn import readers as ismn
from GEE_ISMN import earthengine as ee
from GEE_ISMN import setup_pkg as pkg


user_input = pkg.setup_pkg()

#############

test_dict = {}
test_file = "./data/ISMN_Filt/HOBE_HOBE_1.01_sm_0.000000_0.050000_Decagon" \
            "-5TE-C_20140401_20191015.stm"

data = ismn.read_data(test_file)

test_dict[data.network + "-" + data.sensor + "-" + data.station] = [
    data.latitude, data.longitude, data.data]

test_dict["HOBE-Decagon-5TE-C-1.01"]

#############

# Import and process location data
geo = gpd.read_file('./data/coordinates_2.geojson')
ee_geo = ee.process_geojson(geo, user_input)


# Import land cover data and filter the locations
ee_geo_filt = ee.lc_filter(ee_geo)


# Load and filter Sentinel-1 image collection
img_coll = ee.get_image_collection(ee_geo_filt)


# Extract backscatter data for each location
stations = pd.read_csv("./data/stations.csv")
stations

def ts_to_dict(img_collection, geo_list_filt):
    out_dict = {}

    stations = pd.read_csv("./data/stations.csv")


# Point
for key in img_coll.keys():
    s1_data = ee.time_series_of_a_point(img_coll[key][1], img_coll[key][0])
    s1_data.reset_index().plot(x='Dates', y='VH')
    #plt.savefig("./figs/" + str(key) + ".png")
    #plt.close()

# Region
for key in img_coll.keys():
    s1_data = ee.time_series_of_a_region(img_coll[key][1], img_coll[key][0])
    s1_data.reset_index().plot(x='Dates', y='VV')
    plt.savefig("./figs/" + str(key) + "_sq50.png")
    plt.close()

s1_data = ee.time_series_of_a_point(img_coll["geo_1"][1], img_coll["geo_1"][0])
s1_data

#s1_data.reset_index().plot(x='Dates', y='VH')
#plt.show()