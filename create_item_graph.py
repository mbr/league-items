#!/usr/bin/env python
# coding=utf8

import networkx

from lolitems import ItemGraph
from scrape import item_file_name
G = ItemGraph.from_item_file(item_file_name)

outfilename = 'item-graph.dot'
networkx.write_dot(G, outfilename)
print "wrote",outfilename
