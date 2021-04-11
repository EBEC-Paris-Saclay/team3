import overpy

if __name__ == "__main__":

    # get coords
    lat = 48.89525193
    lon = 2.247122897

    # wrap the query

    # query
    api = overpy.Overpass()
    r = api.query(
        """
    <query type="way">
    <around lat="48.89525193" lon="2.247122897" radius="5"/>
    </query>
    <print />
    """
    )

    # query output processing
    way = r.ways[0]
    print(way.tags["name"])
    # print(r.ways)
