import overpy
from geopy.geocoders import Nominatim

api = overpy.Overpass()
# Inputs

coordinates = [(48.89535, 2.24697), (48.89529, 2.24705), (48.89518, 2.2472)]

lat, lon = coordinates[0]


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


def find_nearest_section(nodes, coordinates):

    indices = []
    for i in range(len(coordinates)):
        lat, lon = coordinates[i]
        # trouver le segment le plus proche de l'arbre
        distance_min_carre = 10000
        indice_min = 0
        latH = 0
        lonH = 0
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

        indices.append((indice_min, i, latH, lonH))
    return indices


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


def give_location2(nodes, name, adrr, coordinates):

    indices = find_nearest_section(nodes, coordinates)

    # find intersections

    indice_min = indices[0][0]

    print('indice_min:', indice_min)

    intersection1, intersection2 = (
        trouver_intersection(nodes, indice_min, -1, name),
        trouver_intersection(nodes, indice_min + 1, 1, name),
    )

    print('intersection trouvée')

    # Define order

    indices.sort()
    groupes = []
    numerotation = dict()
    for element in indices:
        if groupes == [] or groupes[-1][0] != element[0]:
            groupes.append([element])
        else:
            groupes[-1].append(element)
    compteur = 1

    for groupe in groupes:
        distances = []
        for element in groupe:
            distances.append((norme_carre(
                (element[2]-nodes[element[0]].lat, element[3]-nodes[element[0]].lon)), element[1]))
        distances.sort()
        dernier_compteur = compteur
        for _, j in distances:
            numerotation[j] = compteur
            compteur += 1

    print(
        "Les arbres se trouvent sur "
        + name
        + " entre "
        + intersection1
        + " et "
        + intersection2
        + " dans la ville de "
        + addr[-7]
    )
    for j in len(coordinates):
        if j == 0:
            print("Le {}er arbre est".format(
                numerotation[j]), coordinates[j][0], coordinates[j][1])
        else:
            print("Le {}ème arbre est".format(
                numerotation[j]), coordinates[j][0], coordinates[j][1])


way, addr = find_city_way(lat, lon)
print('way:', way, 'addr:', addr)
give_location(way.get_nodes(resolve_missing=True),
              way.tags['name'], addr, coordinates)
