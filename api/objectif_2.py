import overpy
from geopy.geocoders import Nominatim
from objectif_1 import find_city_way, inner_product, norm, find_intersection


def find_nearest_section2(nodes, coordinates):

    indices = []
    for i in range(len(coordinates)):
        lat, lon = coordinates[i]
        # trouver le segment le plus proche de l'arbre
        distance_min = 10000
        indice_min = 0
        latH = 0
        lonH = 0
        for indice in range(len(nodes) - 1):
            lat1 = float(nodes[indice].lat)
            lon1 = float(nodes[indice].lon)
            lat2 = float(nodes[indice + 1].lat)
            lon2 = float(nodes[indice + 1].lon)
            t = inner_product(
                (lat - lat1, lon - lon1), (lat2 - lat1, lon2 - lon1)
            ) / norm((lat2 - lat1, lon2 - lon1))
            t = min(max(0, t), 1)
            latH = lat1 + (lat2 - lat1) * t
            lonH = lon1 + (lon2 - lon1) * t
            distance = norm((lat - latH, lon - lonH))
            if distance_min > distance:
                distance_min = distance
                indice_min = indice

        indices.append((indice_min, i, latH, lonH))
    return indices


def give_location2(api, nodes, name, adrr, coordinates):

    indices = find_nearest_section2(nodes, coordinates)

    # find intersections

    indice_min = indices[0][0]

    print('indice_min:', indice_min)

    intersection1, intersection2 = (
        find_intersection(api, nodes, indice_min, -1, name),
        find_intersection(api, nodes, indice_min + 1, 1, name),
    )

    print('intersections trouvées')

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
            distances.append((norm(
                (element[2]-float(nodes[element[0]].lat), element[3]-float(nodes[element[0]].lon))), element[1]))
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
    for j in range(len(coordinates)):
        if j == 0:
            print("Le {}er arbre est".format(
                numerotation[j]), coordinates[j][0], coordinates[j][1])
        else:
            print("Le {}ème arbre est".format(
                numerotation[j]), coordinates[j][0], coordinates[j][1])


if __name__ == '__main__':
    # The api which will execute all the request on the online map
    api = overpy.Overpass()

    # Inputs

    coordinates = [(48.89535, 2.24697),
                   (48.89529, 2.24705), (48.89518, 2.2472)]

    lat, lon = coordinates[0]

    way, addr = find_city_way(api, lat, lon)
    print('way:', way, 'addr:', addr)
    give_location2(api, way.get_nodes(resolve_missing=True),
                   way.tags['name'], addr, coordinates)
