import overpy

if __name__ == "__main__":

    # get coords
    lat = 48.89525193
    lon = 2.247122897

    #init du radius
    radius = 1
    # wrap the query

    # query
    api = overpy.Overpass()
    r = api.query(
        """
    <query type="way">
    <around lat="{}" lon="{}" radius="{}"/>
    </query>
    <print />
    """.format(lat,lon,radius)
    )

    nb_way=len(r.ways)
    while nb_way!=1:
        if nb_way==0:
            radius = 2*radius
            r = api.query(
            """
            <query type="way">
            <around lat="{}" lon="{}" radius="{}"/>
            </query>
            <print />
            """.format(lat,lon,radius)
            )
        else:
            radius = 3/4*radius
            r = api.query(
            """
            <query type="way">
            <around lat="{}" lon="{}" radius="{}"/>
            </query>
            <print />
            """.format(lat,lon,radius)
            )
        nb_way=len(r.ways)

    # query output processing
    way = r.ways[0]
    print(way.get_nodes(resolve_missing=True))
    # print(r.ways)

    # way.tags["name"],

