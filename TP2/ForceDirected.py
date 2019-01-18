# Powered by Python 2.6

# To cancel the modifications performed by the script
# on the current graph, click on the undo button.

# Some useful keyboards shortcuts : 
#   * Ctrl + D : comment selected lines.
#   * Ctrl + Shift + D  : uncomment selected lines.
#   * Ctrl + Space  : run script.
#   * Ctrl + F  : find selected text.
#   * Ctrl + R  : replace selected text.
import random
from tulip import *
from math import *
from time import sleep
# the updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views

# the pauseScript() function can also be called to pause the script execution.

# To resume the script execution, you will have to click on the "Run script " button.

# the main(graph) function must be defined 
# to run the script on the current graph
MAX_REPULSIVE= 2.;
MAX_ATTRACTIVE= 5.;
EDGE_LENGTH = 10.;
GRAVITY = 0.05;
CENTER = tlp.Coord(0,0,0);


#calcul de la force de gravite exercee sur le sommet v
def computeGravity(layout,graph,v,bary):
	fGrav = GRAVITY * (bary - layout[v])
	return fGrav
	
#calcul de la force d'attraction exercee sur le sommet v
def computeAttractive(layout,graph,v) :
	fAttr = tlp.Coord()
	dist = 0
	diffPos = 0
	for u in graph.getOutNodes(v):
		dist = layout[v].dist(layout[u])
		diffPos = layout[u]-layout[v]
		fAttr += (dist/EDGE_LENGTH)*diffPos
	norm = fAttr.norm()
	if(norm >= MAX_ATTRACTIVE):
		fAttr = (fAttr/norm)*MAX_ATTRACTIVE
	return fAttr

#calcul de la force de repulsion exercee sur le sommet v
def computeRepulsive(layout,graph, v) :
	fRepul = tlp.Coord()
	dist = 0
	diffPos = 0
	for u in graph.getNodes():
		if u == v:
			continue
		dist = layout[v].dist(layout[u])
		diffPos = layout[v]-layout[u]
		if(fabs(dist) > 0.001):
			fRepul += ((EDGE_LENGTH*EDGE_LENGTH)/(dist*dist))*diffPos
	norm = fRepul.norm()
	if(norm >= MAX_REPULSIVE):	
		fRepul = (fRepul/norm)*MAX_REPULSIVE
	return fRepul
	
#calcul des forces totales exercee sur le sommet v
def computeForces(layout,graph, v, bary) :
	return computeAttractive(layout,graph,v)+computeRepulsive(layout,graph,v)+computeGravity(layout,graph,v,bary)

#deplacement du sommet par translation de vecteur move
def displace(layout, v, disp) :
	layout[v] += disp
	return layout[v]

#initialisation du dessin
def initLayout(layout, graph):
	for n in graph.getNodes():
		pos = tlp.Coord(0,0,0)
		p = random.random() * 20. - 10.
		pos[0] = p
		p = random.random() * 20. - 10.
		pos[1] = p
		layout[n] = pos
	somPosition = tlp.Coord()
	for u in graph.getNodes():
		somPosition += layout[u]
	bary = somPosition/graph.numberOfNodes()
	return bary

def intelligentInitLayout(layout, graph):
	for v in graph.getNodes():
		baryNeighbour = tlp.Coord()
		for u in graph.getOutNodes(v):
			baryNeighbour += layout[u]
		baryNeighbour = baryNeighbour / (graph.numberOfNodes()-1)
		layout[v] += baryNeighbour
	
#fonction principale
def main(graph) : 
	layoutResult =  graph.getLayoutProperty("viewLayout")
	barycenter = initLayout(layoutResult, graph)
	intelligentInitLayout(layoutResult, graph)
	moves = {}
	updateVisualization(True)
	#boucle principale
	for n in range(graph.numberOfNodes()):
		print('Tour {}'.format(n))
		updateVisualization(True)
		for v in graph.getNodes():
			fTot = computeForces(layoutResult,graph,v,barycenter)
			barycenter = (barycenter*graph.numberOfNodes()) - layoutResult[v]
			layoutResult[v] = displace(layoutResult,v,fTot)
			barycenter = (barycenter + layoutResult[v])/graph.numberOfNodes()
			

			
	#	for v in graph.getNodes():
	#		layoutResult[v] = moves[v.id]
	#		print("================================================")
	#		print ("Updated Coord Node{} : {}".format(v.id,layoutResult[v]))
	#		print("================================================")
	#		sleep(1)
	#		updateVisualization(True)
	#	return graph
