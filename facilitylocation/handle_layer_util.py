from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsPoint,
    QgsProject,
    NULL,
    QgsDistanceArea,
    QgsWkbTypes
)

from qgis.PyQt.QtCore import QVariant

from qgis.analysis import *

from qgis import processing

from shapely.geometry import Point, LineString

import math

def load_layer(path_layer, name_layer, load_in_project = False):
    vlayer = QgsVectorLayer(path_layer, name_layer, "ogr")
    if not vlayer.isValid():
        print("Layer failed to load!")
    elif load_in_project:
        QgsProject.instance().addMapLayer(vlayer)
    return vlayer

def load_layers(layer_dict, load_in_project = False):
    vlayers = []
    for key, value in layer_dict.items():
        vlayers.append(load_layer(key, value, load_in_project))
    return vlayers

def output_line_feature(dict_facility, dict_client, nome_layer = "LINE TO FACILITY",load_in_project = False):
    """
        A partire da dict_facility e dict_client costruisce un layer di tipo vettoriale che contiene tanti segmenti
        quanti sono i clienti. Un segmento associato ad un determinato cliente ha come estremi le coordinate del cliente 
        e le coordinate della facility in cui il cliente di approvvigiona

        Parameters:
            dict_facility (dict): dizionario contente le facility come valore
            dict_client (dict): dizionario contente i clienti come valore
            nome_layer (string): nome del layer di tipo vettoriale che conterrà i segmenti
            load_in_project (bool): True sse si vuole caricare nel progetto il layer 
    """
    if nome_layer == "":
        nome_layer = "LINE TO FACILITY"


    v_layer = QgsVectorLayer("LineString", nome_layer, "memory")
    pr = v_layer.dataProvider()
    
    for _, client in dict_client.items():
        seg = QgsFeature()
        line_start = dict_facility[client.zone].geometry
        line_end = client.geometry
        seg.setGeometry(QgsGeometry.fromPolylineXY([line_start, line_end]))
        pr.addFeatures( [ seg ] )
        v_layer.updateExtents()
    
    if load_in_project:
        QgsProject.instance().addMapLayers([v_layer])

# def output_street_with_line_referencing(streets_layer, segment, load_in_project = False):
#     streets_layer_with_segment = QgsVectorLayer(streets_layer.source(), streets_layer.name(), streets_layer.providerType())
#     pr = streets_layer_with_segment.dataProvider()
#     for segment in line_referencing:
#         seg = QgsFeature()
#         seg.setGeometry(QgsGeometry.fromPolylineXY([segment[0], segment[1]]))
#         pr.addFeatures( [ seg ] )
#         streets_layer_with_segment.updateExtents()
    
#     if load_in_project:
#         QgsProject.instance().addMapLayers([streets_layer_with_segment])

def output_street_with_line_referencing(streets,nome_layer = "STREETS WITH LINE REFERENCING", load_in_project = False):
    # dict_campi = {     
    #     # "id" : QVariant.Int,
    #     #"chiave + nome layer" :  QVariant.String,
    # }

    #streets_layer_with_segment = build_layer(dict_campi, "multilinestring", nome_layer, load_in_project = False)

    if nome_layer == "":
        nome_layer = "STREETS WITH LINE REFERENCING"

    streets_layer_with_segment = QgsVectorLayer("multilinestring", nome_layer, "memory")
    pr = streets_layer_with_segment.dataProvider()

    for street in streets:
        fet = QgsFeature()
        fet.setGeometry(get_qgs_poliline(list(street.coords)))
        pr.addFeatures( [ fet ] )
        streets_layer_with_segment.updateExtents()

    # for fet in segment_layer.getFeatures():
    #     pr.addFeatures( [ fet ] )
    #     streets_layer_with_segment.updateExtents()

    if load_in_project:
        QgsProject.instance().addMapLayers([streets_layer_with_segment])
    
    return streets_layer_with_segment

def output_line_referencing(line_referencing, nome_layer = "LINE REFERENCING SEGMENTS",load_in_project = False):
    """
        A partire da dict_facility e dict_client costruisce un layer di tipo vettoriale che contiene tanti segmenti
        quanti sono i clienti. Un segmento associato ad un determinato cliente ha come estremi le coordinate del cliente 
        e le coordinate della facility in cui il cliente di approvvigiona

        Parameters:
            dict_facility (dict): dizionario contente le facility come valore
            dict_client (dict): dizionario contente i clienti come valore
            nome_layer (string): nome del layer di tipo vettoriale che conterrà i segmenti
            load_in_project (bool): True sse si vuole caricare nel progetto il layer 
    """
    if nome_layer == "":
        nome_layer = "LINE REFERENCING SEGMENTS"

    v_layer = QgsVectorLayer("LineString", nome_layer, "memory")
    pr = v_layer.dataProvider()
    for segment in line_referencing:
        seg = QgsFeature()
        seg.setGeometry(get_qgs_poliline(list(segment.coords)))
        pr.addFeatures( [ seg ] )
        v_layer.updateExtents()
    
    if load_in_project:
        QgsProject.instance().addMapLayers([v_layer])
    
    return v_layer
    



def output_street_from_client_to_zone(dict_facility, dict_client, OD_path,nome_layer="PATH TO FACILITY",load_in_project = False):
    """
        A partire da dict_facility e dict_client costruisce un layer di tipo vettoriale che contiene tanti segmenti
        quanti sono i clienti. Un segmento associato ad un determinato cliente ha come estremi le coordinate del cliente 
        e le coordinate della facility in cui il cliente di approvvigiona

        Parameters:
            dict_facility (dict): dizionario contente le facility come valore
            dict_client (dict): dizionario contente i clienti come valore
            nome_layer (string): nome del layer di tipo vettoriale che conterrà i segmenti
            load_in_project (bool): True sse si vuole caricare nel progetto il layer 
    """

    if nome_layer == "":
        nome_layer = "PATH TO FACILITY"

    streets_layer_with_segment = QgsVectorLayer("multilinestring", nome_layer, "memory")

    pr = streets_layer_with_segment.dataProvider()
    for _, client in dict_client.items():
        zone = dict_facility[client.zone]
        street = QgsFeature()
        street.setGeometry( get_qgs_poliline(OD_path[client.id][zone.id]) )
        pr.addFeatures( [ street ] )
        streets_layer_with_segment.updateExtents()

    if load_in_project:
        QgsProject.instance().addMapLayers([streets_layer_with_segment])

        
def output_layer_feature(dict_campi,dict_facility, nome_layer = "FACILITY",load_in_project = False):
    """
        A partire da dict_facility e dict_client costruisce un layer di tipo vettoriale che contiene tanti segmenti
        quanti sono i clienti. Un segmento associato ad un determinato cliente ha come estremi le coordinate del cliente 
        e le coordinate della facility in cui il cliente di approvvigiona

        Parameters:
            dict_facility (dict): dizionario contente le facility come valore
            dict_client (dict): dizionario contente i clienti come valore
            nome_layer (string): nome del layer di tipo vettoriale che conterrà i segmenti
            load_in_project (bool): True sse si vuole caricare nel progetto il layer 
    """
    if nome_layer == "":
        nome_layer = "FACILITY"

    schema_layer_facility = build_layer(dict_campi, "point", nome_layer, load_in_project)
    # schema_layer_facility = QgsVectorLayer("point", nome_layer, "memory")
    pr = schema_layer_facility.dataProvider()
    index = 0
    
    for key,facility in dict_facility.items():
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(facility.geometry))
        attributes = [key]
            
        attributes.insert(0,index)
        f.setAttributes(attributes)
        pr.addFeature(f)
        index +=1
    
    schema_layer_facility.updateExtents() 
    
    if load_in_project:
        QgsProject.instance().addMapLayer(schema_layer_facility)
    return schema_layer_facility

def build_layer(dict_campi, geometry_type, nome_layer = "temp", load_in_project = False):
    # crs = QgsProject.instance().crs().authid()
    # tipo_layer = geometry_type + "?" + "crs=" + crs
    
    new_layer = QgsVectorLayer(geometry_type, nome_layer, "memory")
    
    pr = new_layer.dataProvider()
    
    pr.addAttributes([QgsField(key,value) for key, value in dict_campi.items()])
    
    new_layer.updateFields()
    if load_in_project:
        QgsProject.instance().addMapLayer(new_layer)
    return new_layer

def get_all_field(vlayer):
    """
        Parameters:
            vlayer (QgsVectorLayer): layer da cui prendere i nomi dei campi
        Return:
            field_names (string[]): array di stringhe contenente tutti i nomi dei campi di vlayer
    """
    field_names = [field.name() for field in vlayer.fields() ]
    return field_names


# def get_layer_shapely_multistring(street_dict):
#     shapely_streets = []
#     for fet in layers_streets.getFeatures():
#         line = fet.geometry().asMultiPolyline()[0]
#         shapely_streets.append(get_shapely_multistring(line))
#     return shapely_streets

def get_shapely_multistring(qgs_multipoliline):
    return LineString( [(point.x(),point.y()) for point in qgs_multipoliline] )

def get_qgs_poliline(list_of_point):
    return QgsGeometry.fromPolylineXY([QgsPointXY(point[0],point[1]) for point in list_of_point])

def get_shapely_point(qgs_point):
    return Point(qgs_point.x(),qgs_point.y())

def get_qgs_point(shapely_point):
    return QgsPointXY(shapely_point.x,shapely_point.y)

def get_tuple_coord(qgs_point):
    return (qgs_point.x(),qgs_point.y())

def get_tuple_coord_from_shapely(shapely_point):
    return (shapely_point.x,shapely_point.y)


# def line_referencing(all_clients_dict, all_zones_dict,streets):
#     lines_referencing = []

#     all_items_keys = set(all_clients_dict.keys()) | set(all_zones_dict.keys())

#     for key in all_items_keys:
#         if key in all_clients_dict.keys():
#             item = all_clients_dict[key]
#         else: 
#             item = all_zones_dict[key]

#         line_referencing = [item.geometry]
#         shapely_point = get_shapely_point(item.geometry)
#         min_dist = math.inf
#         for street in streets:
#             shapely_point_to_street = street.geometry.interpolate(street.geometry.project(shapely_point))
#             dist = shapely_point.distance(shapely_point_to_street)
#             if dist < min_dist:
#                 min_dist = dist
#                 nearest_point = shapely_point_to_street
#                 nearest_street = street
#         line_referencing.append(get_qgs_point(nearest_point))
#         line_referencing.append(nearest_street)
#         lines_referencing.append(line_referencing)

#         for i in range(len(nearest_street.geometry.coords) - 1):
#             segment_of_street = LineString([nearest_street.geometry.coords[i],nearest_street.geometry.coords[i+1]])

#             if segment_of_street.contains(nearest_point):
#                 nearest_street.geometry.coords.append(i+1,nearest_point)
#                 break   

#     return lines_referencing


def line_referencing(dots_list,streets):
    lines_referencing = []

    for dot in dots_list:
        shapely_point = get_shapely_point(dot)
        min_dist = math.inf
        nearest_point = None
        nearest_street = None
        for street in streets:
            shapely_point_to_street = street.interpolate(street.project(shapely_point))
            dist = shapely_point.distance(shapely_point_to_street)
            if dist < min_dist:
                min_dist = dist
                nearest_point = shapely_point_to_street
                nearest_street = street

        lines_referencing.append(LineString([get_tuple_coord_from_shapely(shapely_point),get_tuple_coord_from_shapely(nearest_point)]))

        nearest_street_coord_list = list(nearest_street.coords)
        min_dist = math.inf
        min_i = 0
        for i in range(len(nearest_street_coord_list) - 1):
            segment_of_street = LineString([nearest_street.coords[i],nearest_street.coords[i+1]])

            dist = segment_of_street.distance(nearest_point)
            if dist < min_dist:
                min_i = i
                min_dist = dist
        
        nearest_street_coord_list.insert(min_i+1,(nearest_point.x,nearest_point.y))
        nearest_street._set_coords(nearest_street_coord_list)


    streets.extend(lines_referencing)
    
    return lines_referencing


