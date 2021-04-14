import overpy
from geopy.geocoders import Nominatim

if __name__ == "__main__":
    """
    TO DO
    - debug all the locations
    - other objectives
    - get lat and lon as parameters
    """
 
    
    # get coords
    lat_arbre_1 =   48.897121406 
    lon_arbre_1 =   2.2479852324

    lat_arbre_2 =   48.89627806 
    lon_arbre_2 =   2.248657510

    # lat =   48.89394122 
    # lon =   2.247959188 
    
    # lat = 48.89525193
    # lon = 2.247122897
    # retrieve city and way
    locator = Nominatim(user_agent="myGeocoder")
    coordinates = "{}, {}".format(lat_arbre_1, lon_arbre_1)
    location = locator.reverse(coordinates)
    addr = location.address
    addr = addr.split(",")

    # init du radius
    radius = 1

    # query
    api = overpy.Overpass()
    r = api.query(
        """
    <query type="way">
    <around lat="{}" lon="{}" radius="{}"/>
    </query>
    <print />
    """.format(
            lat_arbre_1, lon_arbre_1, radius
        )
    )

    nb_way = len(r.ways)
    route_trouvee = False
    while not(route_trouvee):
        if nb_way == 0:
            radius = 3/2 * radius
            r = api.query(
                """
            <query type="way">
            <around lat="{}" lon="{}" radius="{}"/>
            </query>
            <print />
            """.format(
                    lat_arbre_1, lon_arbre_1, radius
                )
            )
        else:
            nb_route_nommees=0
            indice=0
            while nb_route_nommees<2 and indice<nb_way:
                if 'name' in r.ways[indice].tags.keys():
                    nb_route_nommees+=1
                    way=r.ways[indice]
                indice+=1
            if nb_route_nommees==2:
                radius = 5 / 6 * radius
                r = api.query(
                    """
                <query type="way">
                <around lat="{}" lon="{}" radius="{}"/>
                </query>
                <print />
                """.format(
                        lat_arbre_1, lon_arbre_1, radius
                    )
                )
            elif nb_route_nommees==0:
                radius = 3/2 * radius
                r = api.query(
                    """
                <query type="way">
                <around lat="{}" lon="{}" radius="{}"/>
                </query>
                <print />
                """.format(
                        lat_arbre_1, lon, radius
                    )
                )
            else:
                route_trouvee=True

            
        nb_way = len(r.ways)

    def prod_scalaire(vect1, vect2):
        lat1, lon1 = vect1
        lat2, lon2 = vect2
        return lat1 * lat2 + lon1 * lon2

    def norme_carre(vect):
        return prod_scalaire(vect, vect)

    # query output processing
    # way = r.ways[0]
    nom = way.tags["name"]
    # ville = way.tags["addr:city"]
    nodes = way.get_nodes(resolve_missing=True)
    # print(list(map(lambda node: node.id,nodes)))
    # verification que way a bien un seul element

    # trouver le segment le plus proche de l'arbre
    def trouver_indice_min(lat,lon):
        distance_min_carre = 10000
        indice_min = 0
        for indice in range(len(nodes) - 1):
            lat1 = float(nodes[indice].lat)
            lon1 = float(nodes[indice].lon)
            lat2 = float(nodes[indice + 1].lat)
            lon2 = float(nodes[indice + 1].lon)
            t = prod_scalaire(
                (lat - lat1, lon - lon1), (lat2 - lat1, lon2 - lon1)
            ) / norme_carre((lat2 - lat1, lon2 - lon1))
            t = min(max(0, t), 1)
            latH = lat1 + (lat2 - lat1) * t
            lonH = lon1 + (lon2 - lon1) * t
            distance = norme_carre((lat - latH, lon - lonH))
            if distance_min_carre > distance:
                distance_min_carre = distance
                indice_min = indice
        return indice_min
    
    indice_min_1 = trouver_indice_min(lat_arbre_1,lon_arbre_1)
    indice_min_2 = trouver_indice_min(lat_arbre_2,lon_arbre_2)

    def trouver_intersection(nodes, indice, direction, nom_route):
        lat_node = float(nodes[indice].lat)
        lon_node = float(nodes[indice].lon)
        result = api.query(
            """
            <query type="way">
            <around lat="{}" lon="{}" radius="0"/>
            </query>
            <print />
            """.format(
                lat_node, lon_node
            )
        )
        ways = result.ways
        if len(ways) > 1:
            for i in range(len(ways)):
                if "name" in ways[i].tags.keys() and ways[i].tags["name"] != nom_route:
                    return ways[i].tags["name"]
        if indice + direction < 0:
            return "debut de route"
        elif indice + direction >= len(nodes):
            return "fin de route"
        else:
            return trouver_intersection(nodes, indice + direction, direction, nom_route)

    if indice_min_1<indice_min_2:
        intersection1=trouver_intersection(nodes, indice_min_1, -1, nom)
        intersection2=trouver_intersection(nodes, indice_min_2+1, 1, nom)
    else :
        intersection1=trouver_intersection(nodes, indice_min_2, -1, nom)
        intersection2=trouver_intersection(nodes, indice_min_1+1, 1, nom)

    

    # print(addr)
    print(
        "Sur la "
        + nom
        + " entre la "
        + intersection1
        + " et la "
        + intersection2
        + " dans la ville de"
        + addr[-7]
    )
