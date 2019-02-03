"""
Powered by Python 2.7

Implemented by :
Benoît Bothorel & Julien Denou

Project Tulip with M.Bourqui
"""


from tulip import *
import urllib.request
import re
import codecs
import webbrowser


"""
Part 1 : Previsualization
"""

"""
Function for the preprocessing of the labels:
Takes a graph and 3 of his properties and modify them for
each nodes of the graph.
"""
def preprocessingLabels(graph,Locus,viewLabel,viewSize):
  for n in graph.getNodes():
    viewLabel[n] = Locus[n]
    viewSize[n] = tlp.Size(5,5,1)

"""
Function used to color the edges of the graph using his
Negative and Positive properties. The negative and positive values
correspond to the type of regulation of a given gene.
Regulation - : red
Regulation + : green
Regulation + & - : blue
No regulation : black
"""
def coloringEdges(graph,viewColor,Negative,Positive):
  for e in graph.getEdges():
    if Negative[e] == True and Positive[e] == False:
      viewColor[e]=tlp.Color.Red
    elif Negative[e] == False and Positive[e] == True:
      viewColor[e]=tlp.Color.Green
    elif Negative[e] == False and Positive[e] == False:
      viewColor[e]=tlp.Color.Black
    else:
      viewColor[e] = tlp.Color.Blue

"""
Function to draw the graph using the shape of the edges in parameter and the graph
1st : Closing all views from Tulip first and creating a new one with no interpolate
2nd: Applying a tree radial algorithm with edge bundling and bezier curve format to the edges
3rd: Also open automatically open a Spreadsheet view
"""
def drawPreview(graph,viewShape):
  #tlpgui.closeAllViews()
  view = tlpgui.createView("Node Link Diagram view", graph, dataSet={}, show=True)
  #tlpgui.createView("Spreadsheet view", graph, dataSet={}, show=True)
  gui = view.getRenderingParameters()
  gui.setEdgeColorInterpolate(False)
  graph.applyLayoutAlgorithm("Tree Radial")
  graph.applyAlgorithm('Edge bundling')
  for e in graph.getEdges():
    viewShape[e]=tlp.EdgeShape.BezierCurve

"""
Part 2 : Interaction network drawing
"""

"""
Function used to create the hierarchical tree using the graph of the genes interactions.
Builds the hierarchical tree using a recursive call function
"""

def createHierarchicalTree(hierarchicalTree,gene_interact_graph):
  root = hierarchicalTree.addNode()
  call(hierarchicalTree,gene_interact_graph,root)

def call(hierarchical_tree,genes_interactions_tree,root):
  if genes_interactions_tree.numberOfSubGraphs() >0:
    for subg in genes_interactions_tree.getSubGraphs():
      currentNode = hierarchical_tree.addNode()
      hierarchical_tree.addEdge(root,currentNode)
      call(hierarchical_tree,subg,currentNode)
  else:
    for n in genes_interactions_tree.getNodes():
      hierarchical_tree.addNode(n)
      hierarchical_tree.addEdge(root,n)


"""
Function used to color the nodes of a graph using their tpX_s values
and the BiologicalHeatMap colorScale inverted
"""
def colorNodes(graph,tpX_s,viewColor):
  tpX_sValues=[]
  for n in graph.getNodes():
    tpX_sValues.append(tpX_s[n])
  highestTpX_sValue = max(tpX_sValues)
  colorScale=tlpgui.ColorScalesManager.getColorScale("BiologicalHeatMap")
  for n in graph.getNodes():
    color=colorScale.getColorAtPos(1-(tpX_s[n]/highestTpX_sValue))
    viewColor[n]=color

"""
Question2.4
"""

"""
Function used to fill a list with all the nodes
encountered from one node to the root
"""
def getAscendantNode(tree, node):
  fullPath = []
  return getPathToRoot(tree, node, fullPath)

"""
Function used to find recursively, all the nodes from one node
to the root of the tree
"""
def getPathToRoot(tree, node, path):
  for parent_node in tree.getInNodes(node):
    path.append(parent_node)
    getPathToRoot(tree, parent_node, path)
  return path

"""
Function thats finds the shortest path between two nodes
given in parameters.
Return a list containing all the nodes between the two nodes
which will be used to make the control points
"""
def shortestPathBetweenTwoNodes(tree, node1, node2):
  src = getAscendantNode(tree, node1)
  tgt = getAscendantNode(tree, node2)
  tgt.pop(len(tgt)-1)

  for srcnode in src:
    for tgtnode in tgt:
      if (srcnode == tgtnode):
        srclast = src.pop(len(src)-1)#get the last elements from both lists
        tgtlast = tgt.pop(len(tgt) -1)
        while(srclast!=srcnode and tgtlast!=tgtnode ):
          srclast = src.pop(len(src)-1)
          tgtlast = tgt.pop(len(tgt) -1)
        if srclast != tgtlast: 
          src.append(srcnode)
          tgt.append(tgtnode)
  tgt.reverse()#reverse the target path to complement the source path
  shortestPath = src + tgt
  return shortestPath

"""
Function that modify the edges layout (control points)
and applying a Cubic B-Spline Curve to the edges
"""
def modifyEdges(path,layout,edge,shape):
  edgeLayout=[]
  for n in path:
    edgeLayout.append(layout[n])
  layout[edge]=edgeLayout
  shape[edge]=tlp.EdgeShape.CubicBSplineCurve

"""
Main function that compute all the bundle edges from the tree
"""
def createBundles(hierarchical_tree,gi,viewLayout,viewShape):
  for e in gi.getEdges():
    u,v=gi.ends(e)
    path=shortestPathBetweenTwoNodes(hierarchical_tree,u,v)
    modifyEdges(path,viewLayout,e,viewShape)

"""
Part 3 : Small multiples build
"""

"""
Function used to create all the smallMultiple subgraphs
according to their name from the original project
"""
def createSmallMultiples(smallMultiples,gi):
  viewTime=graph.getIntegerProperty("Time")
  for i in range(1,18):
    name="tp"+str(i)+"_s"
    words=name.split("_")
    tpX_s=words[0]+" "+words[1]
    subgraph=smallMultiples.addSubGraph(name)
    tlp.copyToGraph(subgraph,gi)
    metric=subgraph.getLocalDoubleProperty("viewMetric")
    original_metric=gi.getDoubleProperty(tpX_s)
    metric.copy(original_metric)
    viewColor=subgraph.getColorProperty("viewColor")
    colorNodes(subgraph,metric,viewColor)
    setStepOfTime(subgraph,viewTime,i)


"""
Function using the computeBoudningBox method to place the subgraphs from
the SmallMultiple subgraph on a virtual grid
The number of column is used to determine how many subgraphs are placed in one row
"""
def createGrid(smallMultiples,layout,nbColumn):
  box=tlp.computeBoundingBox(smallMultiples)
  coord_X=0
  coord_Y=0
  width=box.width()
  height=box.height()
  for subgraph in smallMultiples.getSubGraphs():
    for n in subgraph.getNodes():
        layout[n]+=tlp.Vec3f((width*coord_X),(height*coord_Y),0) #modifying the layout from the nodes
    for e in subgraph.getEdges():
      newlayout=[]
      for vector in layout[e]:
        vector += tlp.Vec3f((width*coord_X),(height*coord_Y),0) #modifying the layout from all the edges
        newlayout.append(vector)
      layout[e]=newlayout
    if coord_X < nbColumn-1:
      coord_X+=1 #shift to the right while coord_X < number of columns -1 (-1 because we start at 0 and not 1)
    else: #else shift to the bottom and start back with coord_X to 0
      coord_X=0
      coord_Y-=1

"""
Part 4 : Analysis
"""

"""
Function used to find the protein and keggID from each node(gene)
from a txt file representing the gene database for E.coli.
The function parses the txt file to get the informations needed and for each locus value from
the nodes in the graph associate a viewProtein and viewKeggID value.
"""

def getLocusInformations(file,locus):
  list_genes=[]
  list_locus=[]
  list_functions=[]
  with open(file,"r") as f:
    for line in f.readlines():
      if line[0] != "#":
        list_locus.append(line.split("\t")[0])
        list_genes.append(line.split("\t")[1])
        list_functions.append(line.split("\t")[6])
        
  for i in range(len(list_genes)):
    newName=list_genes[i].replace("(",":").replace(")","")
    list_genes[i]=newName

  
  Locus = graph.getStringProperty("Locus")
  viewFunction=graph.getStringProperty("viewProtein")
  viewKeggID=graph.getStringProperty("viewKeggID")
  for n in graph.getNodes():
    locus=Locus[n]
    for i in range(len(list_locus)):
      if list_locus[i] == locus:
        viewFunction[n]=list_functions[i]
        viewKeggID[n]=list_genes[i]

"""
Function that gives the step of time for each subgraph of the smallMultiple in a new metric
this can be used to compare (visually with the spreadsheet view) the genes expressions at different time for the same gene
"""
def setStepOfTime(subgraph,viewTime,i):
  for n in subgraph.getNodes():
      viewTime[n]=i
      
"""
Fucntion that finds the genes or the enzymes implicated in the desired process
using an URL from biocyc.org
Examples at : https://biocyc.org/web-services.shtml
In our case we are looking for the genes and the enzymes implicated in the glycolysis
and in the lactose degradation (pathway=BGALACT-PWY)
Returns a list of strings
"""      
def findGenesOrEnzymesImplicatedInAGivenProcessus(biocycURL):
  contents = urllib.request.urlopen(biocycURL).read()
  file = contents.decode() #transform from bytes to string
  result = re.findall("<common-name datatype='string'>(.+)</common-name>\n",file) #match anything between common-name tag
  return result
  
def ecocycRequests():
  genesFromGlycolysis=findGenesOrEnzymesImplicatedInAGivenProcessus("https://websvc.biocyc.org/apixml?fn=genes-of-pathway&id=ECOLI:GLYCOLYSIS")
  print (genesFromGlycolysis,"\n")
  
  enzymesFromGlycolysis=findGenesOrEnzymesImplicatedInAGivenProcessus("https://websvc.biocyc.org/apixml?fn=enzymes-of-pathway&id=ECOLI:GLYCOLYSIS")
  print (enzymesFromGlycolysis,"\n")
  
  genesFromLD=findGenesOrEnzymesImplicatedInAGivenProcessus("https://websvc.biocyc.org/apixml?fn=genes-of-pathway&id=ECOLI:BGALACT-PWY")
  print (genesFromLD,"\n")
  
  enzymesFromLD=findGenesOrEnzymesImplicatedInAGivenProcessus("https://websvc.biocyc.org/apixml?fn=enzymes-of-pathway&id=ECOLI:BGALACT-PWY")
  print (enzymesFromLD,"\n")

"""
Main
"""
def main(graph):
  viewTime=graph.getIntegerProperty("Time")
  Locus = graph.getStringProperty("Locus")
  Negative = graph.getBooleanProperty("Negative")
  Positive = graph.getBooleanProperty("Positive")
  locus = graph.getStringProperty("locus")
  similarity = graph.getDoubleProperty("similarity")
  tp1_s = graph.getDoubleProperty("tp1 s")
  tp10_s = graph.getDoubleProperty("tp10 s")
  tp11_s = graph.getDoubleProperty("tp11 s")
  tp12_s = graph.getDoubleProperty("tp12 s")
  tp13_s = graph.getDoubleProperty("tp13 s")
  tp14_s = graph.getDoubleProperty("tp14 s")
  tp15_s = graph.getDoubleProperty("tp15 s")
  tp16_s = graph.getDoubleProperty("tp16 s")
  tp17_s = graph.getDoubleProperty("tp17 s")
  tp2_s = graph.getDoubleProperty("tp2 s")
  tp3_s = graph.getDoubleProperty("tp3 s")
  tp4_s = graph.getDoubleProperty("tp4 s")
  tp5_s = graph.getDoubleProperty("tp5 s")
  tp6_s = graph.getDoubleProperty("tp6 s")
  tp7_s = graph.getDoubleProperty("tp7 s")
  tp8_s = graph.getDoubleProperty("tp8 s")
  tp9_s = graph.getDoubleProperty("tp9 s")
  viewBorderColor = graph.getColorProperty("viewBorderColor")
  viewBorderWidth = graph.getDoubleProperty("viewBorderWidth")
  viewColor = graph.getColorProperty("viewColor")
  viewFont = graph.getStringProperty("viewFont")
  viewFontSize = graph.getIntegerProperty("viewFontSize")
  viewIcon = graph.getStringProperty("viewIcon")
  viewLabel = graph.getStringProperty("viewLabel")
  viewLabelBorderColor = graph.getColorProperty("viewLabelBorderColor")
  viewLabelBorderWidth = graph.getDoubleProperty("viewLabelBorderWidth")
  viewLabelColor = graph.getColorProperty("viewLabelColor")
  viewLabelPosition = graph.getIntegerProperty("viewLabelPosition")
  viewLayout = graph.getLayoutProperty("viewLayout")
  viewMetric = graph.getDoubleProperty("viewMetric")
  viewRotation = graph.getDoubleProperty("viewRotation")
  viewSelection = graph.getBooleanProperty("viewSelection")
  viewShape = graph.getIntegerProperty("viewShape")
  viewSize = graph.getSizeProperty("viewSize")
  viewSrcAnchorShape = graph.getIntegerProperty("viewSrcAnchorShape")
  viewSrcAnchorSize = graph.getSizeProperty("viewSrcAnchorSize")
  viewTexture = graph.getStringProperty("viewTexture")
  viewTgtAnchorShape = graph.getIntegerProperty("viewTgtAnchorShape")
  viewTgtAnchorSize = graph.getSizeProperty("viewTgtAnchorSize")
  
  
  #Part 4:
  getLocusInformations("./ecoli.txt",Locus)
        
  #Part 1:
  #preprocessingLabels(graph,Locus,viewLabel,viewSize)
  coloringEdges(graph,viewColor,Negative,Positive)
  drawPreview(graph,viewShape)

  #Part 2:
  graph.addSubGraph("hierarchical_tree")
  g=graph.getSubGraph("hierarchical_tree")
  gi=graph.getSubGraph("Genes interactions")
  createHierarchicalTree(g,gi)
  g.applyLayoutAlgorithm("Tree Radial")
  colorNodes(g,tp1_s,viewColor)
  createBundles(g,gi,viewLayout,viewShape)
  
    
  #Part 3:
  smallMultiple=graph.addSubGraph("Small Multiples")
  createSmallMultiples(smallMultiple,gi)
  createGrid(smallMultiple,viewLayout,5)
  
  
 
  #Part 4(bis):
  ecocycRequests()
  """
  We work on the clone of the initial graph
  Applying a different algorithm (Hierarchical) on the initial graph and using
  the same workflow as previously
  """
  clone=graph.getSubGraph("Clone")
  clone.applyAlgorithm("Hierarchical")
  clone.addSubGraph("hierarchical_tree2")
  h2=clone.getSubGraph("hierarchical_tree2")
  hs=clone.getSubGraph("Hierar Sup")
  createHierarchicalTree(h2,hs)
  h2.applyLayoutAlgorithm("Tree Radial")
  colorNodes(h2,tp1_s,viewColor)
  createBundles(h2,hs,viewLayout,viewShape)
  smallMultiple2=clone.addSubGraph("Small Multiples2")
  createSmallMultiples(smallMultiple2,hs)
  createGrid(smallMultiple2,viewLayout,5)
