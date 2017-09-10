__author__ = 'KeithW'

import random

from .StatEngine import *


# From a specified node get the data value
def xml_get_node_text(node, tag_name : str):

    tag = node.getElementsByTagName(tag_name)

    # If the tag exists then get the data value
    if len(tag) > 0:
        value = tag[0].firstChild.data
    # Else use None
    else:
        value = None

    return value

# From the specified node get the list of stats that are specified and return as a list of BaseStats
def xml_get_stat_list(node):

    # Create an empty list to return the stats that we find
    stat_list = []

    # Get a list of all of the stat elements
    stats = node.getElementsByTagName("stat")

    # For each stat element...
    for stat in stats:

        # Get the name and value of the stat and optional category, randomiser and comparator
        stat_name = xml_get_node_text(stat, "name")
        stat_value = int(xml_get_node_text(stat, "value"))
        stat_description = xml_get_node_text(stat, "description")

        stat_category = xml_get_node_text(stat, "category")
        if stat_category is None:
            stat_category = "RPGCheck"

        stat_randomiser = xml_get_node_text(stat, "random")
        if stat_randomiser is not None:
            stat_value += random.randint(1,int(stat_randomiser))
        else:
            stat_randomiser = 0

        stat_comparator = xml_get_node_text(stat, "comparator")
        if stat_comparator is None:
            stat_comparator = "gte"

        stat_operator = xml_get_node_text(stat, "operator")
        if stat_comparator is None:
            stat_comparator = "eq"

        stat_scope = xml_get_node_text(stat, "global")
        if stat_scope is not None:
            stat_scope = (stat_scope.upper() == "TRUE")
        else:
            stat_scope = False

        check_failure_msg = xml_get_node_text(stat, "failure_msg")

        # Create a BaseStat object and add it to the list
        new_stat = BaseStat(stat_name,stat_category, stat_value)
        new_stat.description = stat_description
        new_stat.randomiser = int(stat_randomiser)
        new_stat.comparator = stat_comparator
        new_stat.operator = stat_operator
        new_stat.scope = stat_scope
        new_stat.failure_msg = check_failure_msg
        stat_list.append(new_stat)

        logging.debug("xml_get_stat_list(): Loaded stat %s.", str(new_stat))

    return stat_list

