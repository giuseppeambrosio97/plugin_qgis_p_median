import os # This is is needed in the pyqgis console also

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

import numpy as np

from qgis import processing

from qgis.PyQt.QtCore import QVariant

from qgis.analysis import *

import random
import math

from .Street import *
from .Zone import *
from .Client import *
from .Solution_F import *
from .handle_layer_util import *

from .util import *

import re

import networkx as nx

def get_all_dict_clients(vlayers, param):
    """

    """
    all_clients = {}
    
    i = 0
    for vlayer in vlayers:
        layer_name = vlayer.name()
        for fet in vlayer.getFeatures():
            field_weight = param[layer_name]['weight']
            if field_weight=="":
                weight = 1
            else:    
                weight = fet[field_weight]
                if weight == NULL:
                    weight = 1
                elif not isinstance(weight, (int, float)):
                    raise ValueError("The field {} is not numeric".format(field_weight))

            if fet.geometry().wkbType() ==  QgsWkbTypes.Point:
                geometry = fet.geometry().asPoint()
            elif fet.geometry().isMultipart() and len(fet.geometry().asMultiPoint())==1:
                geometry = fet.geometry().asMultiPoint()[0]
            
            key = fet[param[layer_name]['key']]

            all_clients[str(key) + " " + layer_name] = Client(i, weight, geometry)
            i+=1
      
    return all_clients

def get_all_dict_zones(vlayers, param):
    """
        
    """
    all_zones = {}
    
    i = 0
    for vlayer in vlayers:
        layer_name = vlayer.name()
        for fet in vlayer.getFeatures():
            if fet.geometry().wkbType() ==  QgsWkbTypes.Point:
                geometry = fet.geometry().asPoint()
            elif fet.geometry().isMultipart() and len(fet.geometry().asMultiPoint())==1:
                geometry = fet.geometry().asMultiPoint()[0]
                
            key = fet[param[layer_name]]
            
            all_zones[str(key) + " " + layer_name] = Zone(i, geometry)

            i+=1

    return all_zones

def get_all_dot_list(vlayers):

    all_dot = []

    for vlayer in vlayers:
        for fet in vlayer.getFeatures():
            if fet.geometry().wkbType() ==  QgsWkbTypes.Point:
                geometry = fet.geometry().asPoint()
            elif fet.geometry().isMultipart() and len(fet.geometry().asMultiPoint())==1:
                geometry = fet.geometry().asMultiPoint()[0]

            all_dot.append(geometry)

                
    return all_dot

# def get_all_dicts_clients(vlayers, param):
#     """

#     """
#     all_clients = {}
    
#     i = 0
#     for vlayer in vlayers:
#         client = {}
#         layer_name = vlayer.name()
#         for fet in vlayer.getFeatures():
#             field_weight = param[layer_name]['weight']
#             if field_weight=="":
#                 weight = 1
#             else:    
#                 weight = fet[field_weight]
#                 if weight == NULL:
#                     weight = 1

#             if fet.geometry().wkbType() ==  QgsWkbTypes.Point:
#                 geometry = fet.geometry().asPoint()
#             elif fet.geometry().isMultipart() and len(fet.geometry().asMultiPoint())==1:
#                 geometry = fet.geometry().asMultiPoint()[0]
            
#             key = fet[param[layer_name]['key']]
        
#             client[str(key)] = Client(i, weight, geometry)
#             i+=1

#         all_clients[layer_name] = client
            
#     return all_clients



# def get_all_dicts_zone(vlayers, param):
#     """
        
#     """
#     all_zones = {}
    
#     i = 0
#     for vlayer in vlayers:
#         zone = {}
#         layer_name = vlayer.name()
#         for fet in vlayer.getFeatures():
#             if fet.geometry().wkbType() ==  QgsWkbTypes.Point:
#                 geometry = fet.geometry().asPoint()
#             elif fet.geometry().isMultipart() and len(fet.geometry().asMultiPoint())==1:
#                 geometry = fet.geometry().asMultiPoint()[0]
                
#             key = fet[param[layer_name]]
            
#             zone[str(key)] = Zone(i, geometry)
            
#             i+=1

#         all_zones[layer_name] = zone
    
#     return all_zones

def distance(p1,p2):
    distance = QgsDistanceArea()
    return distance.measureLine(p1.geometry, p2.geometry)

# def all_street(vlayer):
#     all_street = []

#     i = 0
#     for fet in vlayer.getFeatures():
#         geometry = fet.geometry().asPolyline()
#         all_street.append(Street(i, get_shapely_multistring(geometry)))
#         i+=1
    
#     return all_street

def all_street(vlayer):
    all_street = []

    for fet in vlayer.getFeatures():
        if fet.geometry().wkbType() == QgsWkbTypes.LineString:
            geometry = fet.geometry().asPolyline()
        elif fet.geometry().wkbType() == QgsWkbTypes.MultiLineString:
            geometry = fet.geometry().asMultiPolyline()[0]
        
        all_street.append(get_shapely_multistring(geometry))
    
    return all_street


def OD_matrix_line_distance(dict_clients, dict_zones):
    """
        Parameters:
            clients (dict): dizionario contenente i clienti come valore
            zones (dict): dizionario contenente le zone come valore
        
        Return:
            OD (numpy.array): OD[i,j] = distanza tra il cliente i-esimo e la zona j-esima
    """
    OD = np.zeros((len(dict_clients),len(dict_zones)))
    
    for _,client in dict_clients.items():
        for _,zone in dict_zones.items():
            OD[client.id,zone.id] = distance(client,zone)
    return OD


def create_graph_shapefile(streets):
    H = nx.Graph()
    for street in streets:
        points_street = list(street.coords)
        for i in range(len(points_street)-1):  
            H.add_edge(points_street[i], points_street[i+1])

    return H

def OD_matrix_street_distance_A_star(dict_clients, dict_zones, streets):
    H = create_graph_shapefile(streets)

    nodes_list = list(H.nodes())

    print("nodi ", len(nodes_list))
    print("edge ",len(list(H.edges())))

    # nx.write_shp(H, 'C:\\Users\\Luisa\\Desktop\\') # doctest +SKIP

    nx.set_edge_attributes(H, math.inf, "weight")

    for i in nodes_list:
        for j in nodes_list:
            if H.has_edge(i,j):
                H[i][j]['weight'] = euclidean_distance(i,j)
    #            print(euclidean_distance(node_i,node_j))

    OD_lenght = np.full((len(dict_clients),len(dict_zones)), np.inf)
    OD_path = get_matrix(len(dict_clients),len(dict_zones),default_value=np.inf)

    for _,client in dict_clients.items():
        client_tuple_coord = get_tuple_coord(client.geometry)
        for _,zone in dict_zones.items():
            zone_tuple_coord = get_tuple_coord(zone.geometry)
            # try:
            shortest_path_to_zone = nx.astar_path(H, client_tuple_coord, zone_tuple_coord, heuristic=euclidean_distance, weight="weight")
            OD_path[client.id][zone.id] = shortest_path_to_zone
            OD_lenght[client.id,zone.id] = sum(H[u][v]['weight'] for u, v in zip(shortest_path_to_zone[:-1], shortest_path_to_zone[1:]) )
            # except (nx.NetworkXNoPath, nx.exception.NetworkXError):
            #     pass

    return OD_lenght,OD_path

    
def locate_allocate(client_dict, zone_dict, k, OD_matrix):
    """
        Parameters:
            clients (dict): dizionario contenente i clienti come valore
            zones (dict): dizionario contenente le zone come valore
            k (int): numero facility che si intende costruire
        
        Return:
            facility (dict): soluzione trovata. Dizionario contenente le zone come valore su cui si devono costruire le facility
            cost (float): costo della soluzione trovata
    """    
    solution = Solution_F(client_dict,zone_dict,k,OD_matrix)
    
    if k >= len(zone_dict):
        solution.evaluate_solution()
        return solution.F

    # solution.random_starting_point()
    solution.clustering_starting_point()
    
    while not solution.visite_all_neighbour():
        pass
    
    solution.evaluate_solution()
    return solution.F












