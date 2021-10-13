def print_dict(d):
    for key,value in d.items():
        print("key ", key)
        print("value ", value)

import math

def euclidean_distance(p1,p2):
    return math.sqrt( ( (p1[0]-p2[0])*(p1[0]-p2[0]) ) + ( (p1[1]-p2[1])*(p1[1]-p2[1]) ) )


def len_of_dict_in_dict(dict_dict):
    """
        dict_dict (dict): dict_dict è un dizionario in cui ogni valore è a sua volta un dizionario

        Return:
            Ritorna la somma del numero di elementi di ogni dizionario presente come valore in dict_dict
    """
    return sum(len(item) for _,item in dict_dict.items())

def merge_dict(dict_dict):
    """
        dict_dict (dict): dict_dict è un dizionario in cui ogni valore è a sua volta un dizionario

        Return:
            Ritorna la somma del numero di elementi di ogni dizionario presente come valore in items
    """
    all_items = {}
    for key_dict,value_dict in dict_dict.items():
        for key_item,value_item in value_dict.items():
            new_key = key_item + " " + key_dict
            all_items[new_key] = value_item
    return all_items

def get_matrix(row,col,default_value=0):
    OD = []
    for i in range(row):
        row = []
        for j in range(col):
            row.append(default_value)
        OD.append(row)
    return OD