# Powered by Python 2.7

# To cancel the modifications performed by the script
# on the current graph, click on the undo button.

# Some useful keyboards shortcuts : 
#   * Ctrl + D : comment selected lines.
#   * Ctrl + Shift + D  : uncomment selected lines.
#   * Ctrl + I : indent selected lines.
#   * Ctrl + Shift + I  : unindent selected lines.
#   * Ctrl + Return  : run script.
#   * Ctrl + F  : find selected text.
#   * Ctrl + R  : replace selected text.
#   * Ctrl + Space  : show auto-completion dialog.

from tulip import *
from collections import deque

# the updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views

# the pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the "Run script " button.

# the runGraphScript(scriptFile, graph) function can be called to launch another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call (in the form [a-zA-Z0-9_]+.py)

# the main(graph) function must be defined 
# to run the script on the current graph

# question 1 : construire une grille reguliere de lignes x colonnes sommets connectes a 
#             leurs voisins (lignes et colonnes precedentes et suivantes)
# nodes : matrice (sommets stockes)
def construireGrille(gr, lignes, colonnes, nodes):
	for l in range(0,lignes):
		nodes.append([])
		for c in range(0,colonnes):
			nodes[l].append(gr.addNode())
	
	for l in range(0,lignes):
		for c in range(0,colonnes):
			if(l != 0):
				gr.addEdge(nodes[l][c],nodes[l-1][c])
			if(c != 0):
				gr.addEdge(nodes[l][c],nodes[l][c-1])
			
			
# question 2	 : 
#    2.1 dessiner le graphe avec un algorithme par modele de force : FM^3 (OGDF)
#    2.2 Definir en utilisant la liste de parametres de l'algorithme la longueur d'arete desiree (ici 2)
def dessinerModeleForce(gr, layout):
	params = tlp.getDefaultPluginParameters('FM^3 (OGDF)')
	params['Unit edge length']=2
	gr.applyLayoutAlgorithm("FM^3 (OGDF)",layout,params)
			
# question 3 : le dessin precedent n'est pas satisfaisant, nous voudrions un dessin regulier (puisque la grille est reguliere)
def dessinerRegulier(nodes, layout, decalageX, decalageY):
	for l in range(0,len(nodes)):
		for c in range(0,len(nodes[l])):
			coord = tlp.Coord(c*decalageX, l*decalageY,0.)
			layout[nodes[l][c]] = coord

# question 4 : calculer pour chaque sommet, sa distance au sommet donne en parametre
def calculerDist(root, gr, dist):
	distInt = gr.getIntegerProperty("dist int")
	tlp.maxDistance(gr,root,distInt,tlp.UNDIRECTED)
	
	for n in gr.getNodes():
		dist[n] = distInt[n]
				
				
				
				


#question 5 : colorier les sommets en fonction d'une mesure
def colorierGraphe(gr, color, metric):
	params = tlp.getDefaultPluginParameters('Color Mapping')
	params['input property']=metric
	#resultColor = gr.getColorProperty('color')
	gr.applyColorAlgorithm('Color Mapping',color,params)
	
#question 6 : modifier la grille afin de la transformer en echiquier
def echiquier(nodes, decalage, size, color):
	size.setAllNodeValue(tlp.Size(decalage,decalage,0))
	#color.setAllNodeValue(tlp.Color(255,255,255,255))
	for l in range(0,len(nodes)):
		for c in range(0,len(nodes[l])):
			n = nodes[l][c]
			if(l%2==c%2):
				black=tlp.Color(0,0,0,255)
				color[n] = black
			if(l%2!= c%2):
				white=tlp.Color(255,255,255,255)
				color[n]=white

#question 7 : fabriquer un sous graphe dont les sommets sont les sommets de l'echiquier et 2 sommets sont connectes si et seulement si un cavalier peut se deplacer d'une case a l'autre
def deplacementCavalier(graph,g, nodes):
	return # stub

#question 10 : idem mais pour la reine
def deplacementReine(graph, reine, nodes):
	return # stub

def main(graph): 
	viewBorderColor = graph.getColorProperty("viewBorderColor")
	viewBorderWidth = graph.getDoubleProperty("viewBorderWidth")
	viewColor = graph.getColorProperty("viewColor")
	viewLayout = graph.getLayoutProperty("viewLayout")
	viewShape = graph.getIntegerProperty("viewShape")
	viewSize = graph.getSizeProperty("viewSize")

	viewShape.setAllNodeValue(4) #des rectangles
	viewBorderWidth.setAllNodeValue(1.) # avec une bordure d'epaisseur 1
	viewBorderColor.setAllNodeValue(tlp.Color(0,0,0))	
	lignes = 8
	colonnes = 8
	nodes = []
	
	for n in graph.getNodes():
		graph.delNode(n)
		
	for g in graph.getSubGraphs():
		graph.delAllSubGraphs(g)
	
	#question 1
	construireGrille(graph, lignes, colonnes, nodes)
		
	#question 2
	#dessinerModeleForce(graph,viewLayout)
	
	#question 3
	decalage = 2
	dessinerRegulier(nodes, viewLayout, decalage, decalage)

	#question 4
	dist = graph.getDoubleProperty("distance")
	dist.setAllNodeValue(0.)
	calculerDist(graph.getOneNode(), graph, dist)
	
	#question 5 : attribuer une couleur en fonction d'une mesure sur les sommets
	colorierGraphe(graph, viewColor, dist)
	
	#question 6
	echiquier(nodes, decalage, viewSize, viewColor)
	
	#question 7 
	cavalier = graph.addSubGraph("cavalier")
	deplacementCavalier(graph,cavalier, nodes)

  #question 8 : Toutes les cases sont elle accessibles par un cavalier ? (etant donne la symetrie de l'echiquier, pas besoin de tester pour les 4, un seul suffit)
        
	#question 9 : Coloier le graphe en fonction du nombre de deplacements pour atteindre chaque case (pour un cavalier)
	
	#question 10 : idem pour une reine
