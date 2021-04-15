# -*- coding: utf-8 -*-
import overpy
from geopy.geocoders import Nominatim
from method import*





if __name__ == '__main__':
    # The api which will execute all the requests on the online map
    api = overpy.Overpass()
    # get coords
    lat = 48.89525193 
    lon = 2.247122897
    
    

    
    addr = find_addr(lat, lon)
    way = find_way(api, lat, lon, addr)
    give_location(api, way.get_nodes(
        resolve_missing=True), way.tags['name'], addr,lat,lon)

# url='http://138.195.139.20/api/interpreter'