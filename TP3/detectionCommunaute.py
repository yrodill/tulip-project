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

#calcul de la metrique sur l'arete e
def calculer_c3(graph, e):
  res=0
  tup = graph.ends(e)
  u=tup[0]
  v=tup[1]
  u_set = set(graph.getInOutNodes(u))
  v_set = set(graph.getInOutNodes(v))
  if len(u_set) == 1 and len(v_set)==1:
    return 0
  intersect = u_set.intersection(v_set)
  union = u_set.union(v_set)
  c3=len(intersect)  
  c3max = len(union)-2
  #print (len(intersect))
  #print (len(union))
  res = fabs(c3)/c3max
  return res
	
#calcul de la metrique pour toutes les aretes et affectation a la propriete metric
def calculer_mesure(graph, metric):
  for e in graph.getEdges():
    metric[e]=calculer_c3(graph,e)
  return metric
  
def colorierGraphe(graph, color, metric):
	params = tlp.getDefaultPluginParameters('Color Mapping')
	params['input property']=metric
	#resultColor = gr.getColorProperty('color')
	graph.applyColorAlgorithm('Color Mapping',color,params)
	
#Filtrage des aretes ayant une mesure inferieure a borne (stockee dans metric)
def filtrer_arete(g, metric, borne):
  for n in graph.getNodes():
    if metric[n] < borne:
    	for e in graph.getInOutEdges(n):
    		graph.delEdge(e)

#calcul des composantes connexes
def calculer_composantes_connexes(g):
	nodesAlreadySeen=[]
	
	subg=tlp.ConnectedTest.computeConnectedComponents(g)
	for n in subg:
		if len(n)>1:
			g.inducedSubGraph(n, parentSubGraph=g, name="subgraph")

#calcul et extractions des communautes
#def trouver_groupes(g, metric, borne)

#calcule et retourne la densite interne au graphe g
#def densite_intra_c(g):

#calcule et retourne la densite interne moyenne des communautes de g
#def densite_intra(g):

#calcule et retourne la densite d'aretes entre les communautes g1 et g2
#def densite_inter_c1_c2(g1,g2):

#calcule et retourne la densite externe moyenne des communautes de g
#def densite_inter(g):

#calcule et retourne la qualite de la decomposition de g en communautes
#def evaluer_qualite(g):

#calcule et retourne la borne permettant de maximiser la qualite de la decomposition en communautes du graphe g
#def trouver_meilleure_borne(g, metric):
	 

#fonction principale
def main(graph) :
	
	if len(set(graph.getNodes())) <1:
		for n in graph.getNodes():
			graph.delNode(n)
		
		for g in graph.getSubGraphs():
			graph.delAllSubGraphs(g)
			
	graph = tlp.loadGraph("./imdbDeNiro.tlp.gz")
	print (graph)
	updateVisualization(True)
	
	metric = graph.getProperty("viewMetric")
	color= graph.getProperty("viewColor")
	borne=5
	
	calculer_mesure(graph,metric)
	colorierGraphe(graph,color,metric)
	filtrer_arete(graph,metric,borne)
	calculer_composantes_connexes(graph)
	return True

