import sys
import csv
import re
import geopy
from geopy import distance
import networkx as nx
import matplotlib.pyplot as plt

input_path = sys.argv[1]
# output_path = sys.argv[2]
# ignore_one_way = (sys.argv[3] == 'true')

# Create new graph
G = nx.DiGraph()
# To grab points from WKT linestring
geopoint_re = re.compile("(-?\d+.\d+) (-?\d+.\d+)")

# Open input csv file
with open(input_path) as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    wkt_string = row['WKT']
    bidirectional = (row['DIR_CODE'] == 'B')
    forward = bidirectional or (row['DIR_CODE'] == 'F')
    points = re.findall(geopoint_re, wkt_string)
    # If r.e. found some points in string
    if points:
        line = [geopy.Point(float(point[1]), float(point[0])) for point in points]
    # If its a reverse line, reverse points in line list
    if (not forward):
      line.reverse()
    # Calc dist between line nodes, and add as weights to edges
    for i in range(len(line)-1):
      dist = distance.distance(line[i], line[i+1]).m
      for x in [0,1]:
        if not (str(line[i+x]) in G):
          G.add_node(str(line[i+x]), geopoint=line[i+x])
      G.add_edge(str(line[i]), str(line[i+1]), weight=dist)
      # IF bidirectional line, add reversed pair
      if bidirectional:
        G.add_edge(str(line[i+1]), str(line[i]), weight=dist)
        


# TODO (gbcowan) pickle results
##################################################
# for n in G:
#   paths = nx.single_source_shortest_path(G,n)
##################################################



# Draw graph
# add pseudo pos for vis. purposes
fp = G.node[G.nodes()[0]]['geopoint']
scale = 100000
for n in G:
  p = G.node[n]['geopoint']
  G.node[n]['pos'] = ((p.longitude - fp.longitude) * scale, (p.latitude - fp.latitude) * scale)
# Grab newly created pos attr. 
pos=nx.get_node_attributes(G,'pos')
# Set up matplotlib plot
plt.figure(figsize=(16,16))
nx.draw_networkx_nodes(G, pos, node_size=8, cmap=plt.cm.Reds_r)
nx.draw_networkx_edges(G, pos, alpha=0.4)
# Set bounds
plt.xlim(-1500,1500)
plt.ylim(-1500,1500)
# Turn off axes and render
plt.axis('off')
plt.show()