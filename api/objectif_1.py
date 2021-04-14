import overpy
from geopy.geocoders import Nominatim

# get coords
lat = 48.89227652
lon = 2.253773690

api = overpy.Overpass()


def find_city_way(lat, lon):

    # retrieve city and way
    locator = Nominatim(user_agent="myGeocoder")
    coordinates = "{}, {}".format(lat, lon)
    location = locator.reverse(coordinates)
    addr = location.address
    addr = addr.split(",")

    # init du radius
    radius = 1

    # query

    r = api.query(
        """
    <query type="way">
    <around lat="{}" lon="{}" radius="{}"/>
    </query>
    <print />
    """.format(
            lat, lon, radius
        )
    )

    nb_way = len(r.ways)
    route_trouvee = False
    while not(route_trouvee):
        if nb_way == 0:
            radius = 2 * radius
            r = api.query(
                """
            <query type="way">
            <around lat="{}" lon="{}" radius="{}"/>
            </query>
            <print />
            """.format(
                    lat, lon, radius
                )
            )
        else:
            nb_route_nommees = 0
            indice = 0
            while nb_route_nommees < 2 and indice < nb_way:
                if 'name' in r.ways[indice].tags.keys():
                    nb_route_nommees += 1
                    way = r.ways[indice]
                indice += 1
            if nb_route_nommees == 2:
                radius = 3 / 4 * radius
                r = api.query(
                    """
                <query type="way">
                <around lat="{}" lon="{}" radius="{}"/>
                </query>
                <print />
                """.format(
                        lat, lon, radius
                    )
                )
            elif nb_route_nommees == 0:
                radius = 2 * radius
                r = api.query(
                    """
                <query type="way">
                <around lat="{}" lon="{}" radius="{}"/>
                </query>
                <print />
                """.format(
                        lat, lon, radius
                    )
                )
            else:
                route_trouvee = True

        nb_way = len(r.ways)

    return way, addr


def prod_scalaire(vect1, vect2):
    lat1, lon1 = vect1
    lat2, lon2 = vect2
    return lat1 * lat2 + lon1 * lon2


def norme_carre(vect):
    return prod_scalaire(vect, vect)


def find_nearest_section(nodes):

    # trouver le segment le plus proche de l'arbre
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


def trouver_intersection(nodes, indice, direction, nom_route):

    lat = float(nodes[indice].lat)
    lon = float(nodes[indice].lon)
    result = api.query(
        """
        <query type="way">
        <around lat="{}" lon="{}" radius="0"/>
        </query>
        <print />
        """.format(
            lat, lon
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


def give_location(nodes, name, adrr):
    indice_min = find_nearest_section(nodes)
    print('indice_min:', indice_min)
    intersection1, intersection2 = (
        trouver_intersection(nodes, indice_min, -1, name),
        trouver_intersection(nodes, indice_min + 1, 1, name),
    )
    # print(addr)
    print('intersection 1:', intersection1,
          'intersection 2:', intersection2)
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


way, addr = find_city_way(lat, lon)
print('way:', way, 'addr:', addr)
give_location(way.get_nodes(resolve_missing=True), way.tags['name'], addr)
