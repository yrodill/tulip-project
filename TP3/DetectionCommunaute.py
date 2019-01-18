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
from sets import Set
# the updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views

# the pauseScript() function can also be called to pause the script execution.

# To resume the script execution, you will have to click on the "Run script " button.

# the main(graph) function must be defined 
# to run the script on the current graph

def frange(start, stop, step):
	i = start
	while i < stop:
		yield i
		i += step
		
#calcul de la metrique sur l'arete e
def calculer_c3(graph, e):
	nodesEdge = graph.ends(e)
	u = nodesEdge[0]
	v = nodesEdge[1]
	
	u_Neighb = Set(graph.getInOutNodes(u))
	v_Neighb = Set(graph.getInOutNodes(v))
	if len(u_Neighb) > 2 and len(v_Neighb) > 2:
		intersect = u_Neighb.intersection(v_Neighb)
		union = u_Neighb.union(v_Neighb)
		c3 = fabs(len(intersect))
		c3Max = len(union) - 2
		result = fabs(c3)/c3Max
		return result
	
	
#calcul de la metrique pour toutes les aretes et affectation a la propriete metric
def calculer_mesure(graph, metric) :
	for e in graph.getEdges():
		metric[graph.target(e)] = calculer_c3(graph,e)

def colorierGraphe(graph, color, metric):
	p = tlp.getDefaultPluginParameters("Color Mapping", graph)
	p["input property"] = metric
	graph.applyColorAlgorithm("Color Mapping",color, p)
	
#Filtrage des aretes ayant une mesure inferieure a borne (stockee dans metric)
def filtrer_arete(graph, metric, borne):
	for n in graph.getNodes():
		if metric[n] < borne:
			edges = graph.getInOutEdges(n)
			for e in edges:
				graph.delEdge(e)

#calcul des composantes connexes
def calculer_composantes_connexes(graph):
	listListNodes = tlp.ConnectedTest.computeConnectedComponents(graph)
	for g in listListNodes:
		if len(g) >1:
			graph.inducedSubGraph(g,parentSubGraph = graph)
	

#calcul et extractions des communautes
def trouver_groupes(graph, metric, borne):
	filtrer_arete(graph,metric,borne)
	calculer_composantes_connexes(graph)
	
#calcule et retourne la densite interne au graphe g
def densite_intra_c(g):
	edges = g.numberOfEdges()
	nodes = g.numberOfNodes()
	density = (fabs(edges)) / (fabs(nodes)*fabs(nodes-1))
	return density
		
#calcule et retourne la densite interne moyenne des communautes de g
def densite_intra(g):
	result = 0
	if(g.numberOfSubGraphs() == 0):
		return result
	for sub in g.getSubGraphs():
		result += densite_intra_c(sub) 
	result = result/ g.numberOfSubGraphs()
	return result

#calcule et retourne la densite d'aretes entre les communautes g1 et g2
def densite_inter_c1_c2(g1,g2):
	commonEdges = 0
	listNodes1 = []
	listNodes2 = []
	density = 0
	for nodes1 in g1.getNodes():
		listNodes1.append(nodes1)
	for nodes2 in g2.getNodes():
		listNodes2.append(nodes2)
	
	zelda = []
	for node in listNodes1:
		for link in graph.getInOutNodes(node):
			if link not in listNodes1 and link not in zelda:
				zelda.append(link)
	
	for link in zelda:
		for connect in graph.getInOutNodes(link):
			if connect in listNodes2:
				commonEdges += 1
				
	for node1 in g1.getNodes():
		for edge in graph.getInOutEdges(node1):
			if graph.target(edge) in listNodes2:
				commonEdges +=1

		nodes1 = g1.numberOfNodes()
		nodes2 = g2.numberOfNodes()
		density = (fabs(commonEdges)) / (fabs(nodes1*nodes2))
		return density
	
#calcule et retourne la densite externe moyenne des communautes de g
def densite_inter(g):
	result = 0
	for i in range(g.numberOfSubGraphs()-1):
		for j in range(i+1,g.numberOfSubGraphs()):
			g1 = g.getNthSubGraph(i)
			g2 = g.getNthSubGraph(j)
			result += densite_inter_c1_c2(g1,g2)
	if (g.numberOfSubGraphs() > 2):
		result = result / ((g.numberOfSubGraphs()) * (g.numberOfSubGraphs()-1))
		result /= 2
	return result

#calcule et retourne la qualite de la decomposition de g en communautes
def evaluer_qualite(g):
	return densite_intra(g)- densite_inter(g)
#calcule et retourne la borne permettant de maximiser la qualite de la decomposition en communautes du graphe g
def trouver_meilleure_borne(g, metric):
		maximum = 0
		borne = 0
		for value in frange(0,1.025, 0.025):
			sub = g.addCloneSubGraph(name = "sub")
			trouver_groupes(sub,metric,value)
			quality = evaluer_qualite(sub)
			if maximum < quality:
				maximum = quality
				borne = value
			for gr in g.getSubGraphs():
				g.delAllSubGraphs(gr)
		return borne

#fonction principale
def main(graph) :
	for sub in graph.getSubGraphs():
		graph.delAllSubGraphs(sub)
	graphClone = graph.addCloneSubGraph(name = "Clone_{}".format(graph.getName()))
	metric = graphClone.getLocalDoubleProperty("viewMetric") 
	color = graphClone.getLocalColorProperty("viewColor")
	calculer_mesure(graphClone,metric)
	colorierGraphe(graphClone,color,metric)
	borne = trouver_meilleure_borne(graphClone,metric)
	print("Best Borne : {}".format(borne))
	trouver_groupes(graphClone,metric,borne)
	quality = evaluer_qualite(graphClone)
	print("Quality : {}".format(quality))
	return True
