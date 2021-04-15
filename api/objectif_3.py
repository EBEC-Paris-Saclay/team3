"""
objective 3 : two points on two consecutive sections
"""

import overpy
from geopy.geocoders import Nominatim
from method import *


def give_location3(api, nodes, name, addr,lat1,lon1,lat2,lon2):
    ''' Give the full location

    :param nodes: The list of all nodes of the road
    :param name: The name of the road
    :param addr: The whole loaction of the tree
    :return:?

    '''

    indice_min_1 = find_nearest_section(nodes,lat1,lon1)
    indice_min_2 = find_nearest_section(nodes,lat2,lon2)

    if indice_min_1 < indice_min_2:
        intersection1 = find_intersection(api, nodes, indice_min_1, -1, name)
        intersection2 = find_intersection(api, nodes, indice_min_2 + 1, 1, name)
    else:
        intersection1 = find_intersection(api, nodes, indice_min_2, -1, name)
        intersection2 = find_intersection(api, nodes, indice_min_1 + 1, 1, name)

    print(
        "Sur "
        + name
        + " entre "
        + intersection1
        + " et "
        + intersection2
        + " dans la ville de "
        + addr[-7]
    )

if __name__ == "__main__":
    api = overpy.Overpass()
    # get coords
    lat_arbre_1 = 48.897121406
    lon_arbre_1 = 2.2479852324

    lat_arbre_2 = 48.89627806
    lon_arbre_2 = 2.248657510
    
    

    
    addr = find_addr(lat_arbre_1, lon_arbre_1)
    way = find_way(api, lat_arbre_1, lon_arbre_1, addr)
    give_location3(api, way.get_nodes(
        resolve_missing=True), way.tags['name'], addr,lat_arbre_1,lon_arbre_1,lat_arbre_2,lon_arbre_2)
