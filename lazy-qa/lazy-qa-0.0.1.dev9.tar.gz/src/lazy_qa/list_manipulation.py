import random


# ---------------------------------------------------------------------------------------------------------------------#
#                                       Functions to manipulate List                                                   #
# ---------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------------- List Functions ---------------------------------------------------#


def union_list_without_duplicate_item(list_a, list_b):
    result_list = list(list_a)
    result_list.extend(x for x in list_b if x not in result_list)


def intersection_list(list_a, list_b):
    result_list = [list(filter(lambda x: x in list_a, sublist)) for sublist in list_b]
    return result_list


def remove_item_from_list(list, item):
    result_list = list.remove(item)
    return result_list


def get_random_item_from_list(list, item):
    selected_item = random.choice(list)
    return selected_item


def get_different_random_item_from_list(list, item):
    result_list = list.remove(item)
    selected_item = random.choice(result_list)
    return selected_item


# -----------------------------------------------------------------------------------------------------------------#
# GET_LIST_FROM_SOURCE is a function use to load a data from a source archive. It's useful to get all information  #
# from a collection. For example, if you need to POST the same .json and the data don't need to be changed, the    #
# data source can emulate the .json.                                                                               #
# This function needs 2 arguments: the dict's name and the collection's name:                                      #
#   Example:                                                                                                       #
#       DATA_SOURCE ={                     payload = get_list_from_source(DATA_SOURCE, 'valid_data')               #
# 	        "valid_data" :[{               print("Payload is: ", payload)                                          #
# 	                 "key_1" : "value1",                                                                           #
#      	             "key_2" : "value2"                                                                            #
#      	     }],                           output:  Payload is:   "valid_data" :[{                                 #
#           "invalid_data" :[{                                           "key_1" : "value1",                       #
# 	                "key_1" : "value1",                                  "key_2" : "value2"                        #
#      	            "key_2" : "value2"                                   }]                                        #
#      	            }]                                                                                             #
# }                                                                                                                #                                                                          #
# -----------------------------------------------------------------------------------------------------------------#


def get_list_from_source(source, data):
    """Get a list of arguments named as 'data' on the 'source'."""
    data_args = source.get(data.replace(' ', '_'))
    if data_args is not None:
        # Return the list if not Empty
        return data_args[0]
    else:
        message = "No matching results for parameter data = " + data + " was found in DataPool."
        raise Exception(message)


# -----------------------------------------------------------------------------------------------------------------#
# DATAPOOL_READ is a function use to get a collection of information from a source archive Dictionaries, Hashmaps, #
# and Hash Tables.                                                                                                 #
# This function needs 3 arguments: the dict's name, the collection's name and the key that you searching for.      #
#                                                                                                                  #
#   Example:                                  result = datapool_read(DATA_SOURCE, valid_data, 'key_1')             #
#       DATA_SOURCE ={                        print("Results is: ", result)                                        #
# 	        "valid_data" :[{                                                                                       #
# 	                 "key_1" : "value1",                                                                           #
#      	             "key_2" : "value2"       output:  Results is: value1                                          #
#      	     }],                                                                                                   #
#           "invalid_data" :[{                                                                                     #
# 	                "key_1" : "value1",                                                                            #
#      	            "key_2" : "value2"                                                                             #
#      	            }]                                                                                             #
# }                                                                                                                #                                                                          #
# -----------------------------------------------------------------------------------------------------------------#


def datapool_read(source, data, key):
    """Get a list of arguments named as 'data' on the 'source' and search the 'key' on that list."""
    data_args = source.get(data.replace(' ', '_'))
    dt_key = key.replace(' ', '_')
    if data_args is not None:
        # Search the 'key' on that list ------> for "python data_args[0].get(dt_key)"
        if data_args.get(dt_key) is not None:
            return data_args.get(dt_key)
        else:
            message = "No matching results for parameter data = " + data + " on the key = " + key + "was found in " \
                                                                                                    "DataPool. "
            raise Exception(message)
    else:
        message = "No matching results for parameter data = " + data + " on the key = " + key + "was found in " \
                                                                                                "DataPool. "
        raise Exception(message)


def get_data_from_dict(dict_args, key):
    """Get a dictionary of arguments named as 'dict_args', search the 'key' on that dict and return the value."""
    data_args = dict_args
    if data_args is not None:
        # Search the 'key' on that list
        if data_args.get(key) is not None:
            return data_args.get(key)
    else:
        message = "No matching results for parameter key = " + key + " was found in Dictionary."
        raise Exception(message)
