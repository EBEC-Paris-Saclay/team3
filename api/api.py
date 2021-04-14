import overpy

if __name__ == "__main__":

    # get coords
    lat = 48.89525193
    lon = 2.247122897

    #init du radius
    radius = 5
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
    # while nb_way!=1:
    #     if nb_way==0:
    #         radius = 2*radius
    #         r = api.query(
    #         """
    #         <query type="way">
    #         <around lat="{}" lon="{}" radius="{}"/>
    #         </query>
    #         <print />
    #         """.format(lat,lon,radius)
    #         )
    #     else:
    #         radius = 3/4*radius
    #         r = api.query(
    #         """
    #         <query type="way">
    #         <around lat="{}" lon="{}" radius="{}"/>
    #         </query>
    #         <print />
    #         """.format(lat,lon,radius)
    #         )
    #     nb_way=len(r.ways)

    def prod_scalaire(vect1,vect2):
        lat1,lon1=vect1
        lat2,lon2=vect2
        return(lat1*lat2+lon1*lon2)

    def norme_carre(vect):
        return(prod_scalaire(vect,vect))

    areas = api.query("""
    
    is_in({},{});
    area;
    """.format(lat,lon))
            
    print(areas.areas)
    # query output processing
    way = r.ways[0]
    nom = way.tags["name"]
    # ville = way.tags["addr:city"]
    nodes = way.get_nodes(resolve_missing=True)
    # verification que way a bien un seul element
    
    # trouver le segment le plus proche de l'arbre
    distance_min_carre=10000
    indice_min=0
    for indice in range(len(nodes)-1):
        lat1 = float(nodes[indice].lat)
        lon1 = float(nodes[indice].lon)
        lat2 = float(nodes[indice+1].lat)
        lon2 = float(nodes[indice+1].lon)
        t=prod_scalaire((lat-lat1,lon-lon1),(lat2-lat1,lon2-lon1))/norme_carre((lat2-lat1,lon2-lon1))
        t = min( max ( 0, t), 1)
        latH=lat1+(lat2-lat1)*t
        lonH=lon1+(lon2-lon1)*t
        distance=norme_carre((lat-latH,lon-lonH))
        if distance_min_carre>distance:
            distance_min_carre=distance
            indice_min=indice
    
    def trouver_intersection(nodes,indice,direction,nom_route):
        lat=float(nodes[indice].lat)
        lon=float(nodes[indice].lon)
        result=api.query(
        """
            <query type="way">
            <around lat="{}" lon="{}" radius="0"/>
            </query>
            <print />
            """.format(lat,lon)
        )
        ways=result.ways
        if len(ways)>1:
            if "name" in ways[0].tags.keys() and ways[0].tags["name"]!=nom_route:
                return ways[0].tags["name"]
            elif "name" in ways[1].tags.keys() and ways[1].tags["name"]!=nom_route:
                return ways[1].tags["name"]
        if indice+direction<0 :
            return "debut de route"
        elif indice+direction>=len(ways):
            return 'fin de route'
        else:
            return trouver_intersection(nodes,indice+direction,direction,nom_route)
        
    intersection1,intersection2 = (trouver_intersection(nodes,indice_min,-1,nom),trouver_intersection(nodes,indice_min+1,1,nom))
    
    print("Sur la " + nom + " entre la " + intersection1 + " et la " + intersection2 + " dans la ville de " )



        


    # print(indice_min,distance_min_carre)
    # print(r.ways)

    # way.tags["name"],

