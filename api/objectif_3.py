"""
objective 3 : two points on two consecutive sections
"""

import overpy
from geopy.geocoders import Nominatim
from method import *

if __name__ == "__main__":

    # get coordinates
    lat_arbre_1 = 48.897121406
    lon_arbre_1 = 2.2479852324

    lat_arbre_2 = 48.89627806
    lon_arbre_2 = 2.248657510

    # retrieve city name
    # two trees need to be on the same way, so we juste need to find the way of the first one
    locator = Nominatim(user_agent="myGeocoder")
    coordinates = "{}, {}".format(lat_arbre_1, lon_arbre_1)
    location = locator.reverse(coordinates)
    addr = location.address
    addr = addr.split(",")

    # radius initialization
    radius = 1

    # query-writing to get the way name
    # first query with a thin radius
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
    # the call of the query is repeated with different values of radius in order to find a query result with only one named way
    # The found way is necessarily the nearest named way of the tree
    while not (route_trouvee):
        # if there is no way in the result of the previuos query, we increase the radius by a factor 3/2
        if nb_way == 0:
            radius = 3 / 2 * radius
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
            nb_route_nommees = 0
            indice = 0
            # if there are ways in the result of the previous query result, we want to know if there is 0, 1 or 2+ named ways in the result
            while nb_route_nommees < 2 and indice < nb_way:
                if "name" in r.ways[indice].tags.keys():
                    nb_route_nommees += 1
                    way = r.ways[indice]
                indice += 1
            # if there is at least two ways, we reduce the radius by a factor 5/6
            if nb_route_nommees == 2:
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
            # if there is no named way in the result, we increase the radius by a factor 3/2
            elif nb_route_nommees == 0:
                radius = 3 / 2 * radius
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
            # if there is only one named way in the result, we end the while.
            else:
                route_trouvee = True

        nb_way = len(r.ways)
    # Now that we have the way , we want to find the segments between to nodes that contains the the trees
    # Beware that in openstreemap a node is not necessarly a intersection between ways but it can be just to fit the curve of the way
    # We consider that, in the scale of a city, the couple of coordinates (lat,lon) defines a Cartesian coordinate system

    # prod_scalaire returns the scalar product of two vectors.
    def prod_scalaire(vect1, vect2):
        lat1, lon1 = vect1
        lat2, lon2 = vect2
        return lat1 * lat2 + lon1 * lon2

    # norme_carre returns the square of the norme of e vector
    def norme_carre(vect):
        return prod_scalaire(vect, vect)

    # get name of the way and the nodes it contains
    nom = way.tags["name"]
    nodes = way.get_nodes(resolve_missing=True)

    # now we want to find the closest segment and the index of its first node in the list nodes
    def trouver_indice_min(lat, lon):
        distance_min_carre = (
            10000  # we initiate the minimum distance at a large value of 10 kilometers
        )
        indice_min = 0
        for indice in range(len(nodes) - 1):
            lat1 = float(nodes[indice].lat)
            lon1 = float(nodes[indice].lon)
            lat2 = float(nodes[indice + 1].lat)
            lon2 = float(nodes[indice + 1].lon)
            # now we calculate the distance between one tree and a segment
            t = prod_scalaire(
                (lat - lat1, lon - lon1), (lat2 - lat1, lon2 - lon1)
            ) / norme_carre((lat2 - lat1, lon2 - lon1))
            t = min(max(0, t), 1)
            latH = lat1 + (lat2 - lat1) * t
            lonH = lon1 + (lon2 - lon1) * t
            distance = norme_carre((lat - latH, lon - lonH))
            # So we update indice_min which is the index of the node at the begining of the closest segment
            if distance_min_carre > distance:
                distance_min_carre = distance
                indice_min = indice
        return indice_min

    # we use trouver_indice_min to find the begining node of each segment
    indice_min_1 = trouver_indice_min(lat_arbre_1, lon_arbre_1)
    indice_min_2 = trouver_indice_min(lat_arbre_2, lon_arbre_2)

    # trouver intersection returns the first intersection at the right (if direction values 1) or left (if it values -1) of a node represented by its index in nodes
    def trouver_intersection(nodes, indice, direction, nom_route):
        lat_node = float(nodes[indice].lat)
        lon_node = float(nodes[indice].lon)
        # this query returns the list of ways the node is in.
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
        # we want to find a node that is an intersection between at least two NAMED ways
        if len(ways) > 1:
            for i in range(len(ways)):
                if "name" in ways[i].tags.keys() and ways[i].tags["name"] != nom_route:
                    return ways[i].tags["name"]
        # It is possible that the tree is at the very last segment or the very first segment of the road and there is not necessarly another way at the end and at the beginning of a way
        if indice + direction < 0:
            return "debut de route"
        elif indice + direction >= len(nodes):
            return "fin de route"
        else:
            return trouver_intersection(nodes, indice + direction, direction, nom_route)

    # depending on the relative position of the two trees in the way, we find the two intersections we need
    if indice_min_1 < indice_min_2:
        intersection1 = trouver_intersection(nodes, indice_min_1, -1, nom)
        intersection2 = trouver_intersection(nodes, indice_min_2 + 1, 1, nom)
    else:
        intersection1 = trouver_intersection(nodes, indice_min_2, -1, nom)
        intersection2 = trouver_intersection(nodes, indice_min_1 + 1, 1, nom)

    # the algorithm print the result in natural language
    print(
        "Sur "
        + nom
        + " entre "
        + intersection1
        + " et "
        + intersection2
        + " dans la ville de"
        + addr[-7]
    )
