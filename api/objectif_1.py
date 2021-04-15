import overpy
from geopy.geocoders import Nominatim


def find_city_way(api, lat, lon):
    ''' Find way: Finds all ways around the radius {radius}, 
    reduce it when we find more than one and increase it when we find nothing

    :param lat: The latitude of the tree
    :param lon: The longitude of the tree
    :return : The way and the city where it's found

    '''

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
    road_found = False
    while not(road_found):
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
            nb_road_found = 0
            indice = 0
            while nb_road_found < 2 and indice < nb_way:
                if 'name' in r.ways[indice].tags.keys():
                    nb_road_found += 1
                    way = r.ways[indice]
                indice += 1
            if nb_road_found == 2:
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
            elif nb_road_found == 0:
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
                road_found = True

        nb_way = len(r.ways)

    return way, addr


def inner_product(vect1, vect2):
    ''' Finds the inner product of vect1 and vect2 

    :param vect1: The coordinates of the first vector
    :param vect2: The coordinates of the second vector
    :return : The inner product of vect1 and vect2

    '''

    lat1, lon1 = vect1
    lat2, lon2 = vect2
    return lat1 * lat2 + lon1 * lon2


def norm(vect):
    ''' Finds the norm of vect

    :param vect: coordinates of vect
    :return: norm of vect

    '''
    return inner_product(vect, vect)


def find_nearest_section(nodes):
    """ Finds the segment of the road which has the shortest orthogonal distance to the tree

    :param nodes: The list of all nodes of the way
    :return: The indice of the beginning node of the section in the list nodes

     """

    distance_min = 10000
    indice_min = 0
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

    return indice_min


def find_intersection(api, nodes, indice, direction, name):
    ''' Since every segment of the road is not an intersection, this function spans the segment found with
    find_nearest_section

    :param nodes:The list of all nodes of the way
    :param indice: The indice of the beginning node of the section in the list nodes
    :param direction: The orientation of the segment
    :param name: The name of the road
    :return: The indice of the intersection in the list of nodes

    '''

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
            if "name" in ways[i].tags.keys() and ways[i].tags["name"] != name:
                return ways[i].tags["name"]
    if indice + direction < 0:
        return "debut de route"
    elif indice + direction >= len(nodes):
        return "fin de route"
    else:
        return find_intersection(api, nodes, indice + direction, direction, name)


def give_location(api, nodes, name, adrr):
    ''' Gives the full location of the tree

    :param nodes: The list of all nodes of the road
    :param name: The name of the road
    :param addr: The location of the tree in lattitude and longitude
    :return: A printed text showing the said full location

    '''

    indice_min = find_nearest_section(nodes)
    print('indice_min:', indice_min)
    intersection1, intersection2 = (
        find_intersection(api, nodes, indice_min, -1, name),
        find_intersection(api, nodes, indice_min + 1, 1, name),
    )
    print(addr)
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


if __name__ == '__main__':
    # The api which will execute all the requests on the online map
    api = overpy.Overpass()

    # get coords
    lat = 48.89227652
    lon = 2.253773690

    way, addr = find_city_way(api, lat, lon)
    print('way:', way, 'addr:', addr)
    give_location(api, way.get_nodes(
        resolve_missing=True), way.tags['name'], addr)
