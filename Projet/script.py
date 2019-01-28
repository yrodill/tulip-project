"""
Powered by Python 2.7

Implemented by :
Benoît Bothorel & Julien Denou

Project Tulip with M.Bourqui
"""


from tulip import *


"""
Part 1 : Previsualization
"""

"""
Function for the preprocessing of the labels:
Takes a graph and 3 of his properties and modify them for
each nodes of the graph.
"""
def preprocessing_label(graph,Locus,viewLabel,viewSize):
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
def coloring_edges(graph,viewColor,Negative,Positive):
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
def draw(graph,viewShape):
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

def create_hierarchical_tree(hierarchicalTree,gene_interact_graph):
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

"""
Function using the computeBoudningBox method to place the subgraphs from
the SmallMultiple subgraph on a virtual grid
The number of column is used to determine how many subgraphs are placed in one row
"""
def createGrid(smallMultiples,layout,nbColumn):
  box=tlp.computeBoundingBox(smallMultiples)
  a=0
  b=0
  width=box.width()
  height=box.height()
  for subgraph in smallMultiples.getSubGraphs():
    for n in subgraph.getNodes():
        layout[n]+=tlp.Vec3f((width*a),(height*-b),0) #modifying the layout from the nodes
    for e in subgraph.getEdges():
      newlayout=[]
      for vector in layout[e]:
        vector += tlp.Vec3f((width*a),(height*-b),0) #modifying the layout from all the edges
        newlayout.append(vector)
      layout[e]=newlayout
    if a < nbColumn-1:
      a+=1 #shift to the right while a < number of columns -1
    else: #else shift to the bottom and start back with a to 0
      a=0
      b+=1


"""
Main
"""
def main(graph):
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

  #Part 1:
  preprocessing_label(graph,Locus,viewLabel,viewSize)
  coloring_edges(graph,viewColor,Negative,Positive)
  draw(graph,viewShape)

  #Part 2:
  if graph.numberOfSubGraphs() > 2:
    graph.delSubGraph(graph.getSubGraph("hierarchical_tree"))
    graph.delAllSubGraphs(graph.getSubGraph("Small Multiples"))
  
  graph.addSubGraph("hierarchical_tree")
  g=graph.getSubGraph("hierarchical_tree")
  gi=graph.getSubGraph("Genes interactions")
  create_hierarchical_tree(g,gi)
  g.applyLayoutAlgorithm("Tree Radial")
  colorNodes(g,tp1_s,viewColor)
  createBundles(g,gi,viewLayout,viewShape)
  
    
  #Part 3:
  smallMultiple=graph.addSubGraph("Small Multiples")
  createSmallMultiples(smallMultiple,gi)
  createGrid(smallMultiple,viewLayout,5)
  
