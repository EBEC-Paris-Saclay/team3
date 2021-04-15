import overpy
from geopy.geocoders import Nominatim
from method import*





if __name__ == '__main__':
    # The api which will execute all the requests on the online map
    api = overpy.Overpass(url='http://138.195.138.151/api/interpreter')
    
    # get coords
    lat = 42.408796
    lon = 8.984383

    way = find_way(api, lat, lon)
    addr = find_addr(lat, lon)
    give_location(api, way.get_nodes(
        resolve_missing=True), way.tags['name'], addr,lat,lon)
