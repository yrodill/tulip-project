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

# The updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views

# The pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the "Run script " button.

# The runGraphScript(scriptFile, graph) function can be called to launch
# another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call (in the form [a-zA-Z0-9_]+.py)

# The main(graph) function must be defined 
# to run the script on the current graph

#Part 1 : Previsualization

#function for the preprocessing of the labels
def preprocessing_label(graph,Locus,viewLabel,viewSize):
  for n in graph.getNodes():
    viewLabel[n] = Locus[n]
    viewSize[n] = tlp.Size(5,5,1)

#function used to color the edges of the graph using his
#negative and positive property 
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
      
#function used to draw the graph
#closing all views from Tulip first and creating a new one with no interpolate
#then applaying a tree radial algorithm with edge bundling and bezier curve format to the edges
def draw(graph,viewShape):
  tlpgui.closeAllViews()
  test = tlpgui.createView("Node Link Diagram view", graph, dataSet={}, show=True)
  gui = test.getRenderingParameters()
  gui.setEdgeColorInterpolate(False)
  graph.applyLayoutAlgorithm("Tree Radial")
  graph.applyAlgorithm('Edge bundling')
  for e in graph.getEdges():
    viewShape[e]=tlp.EdgeShape.BezierCurve

#Part 2 : Interaction network drawing

#function used to create the hierarchical tree using the graph of the genes interactions
#builds the hierarchical tree using a recursive call function
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

#function used to color the nodes of a graph using their tpX_s values
#using the BiologicalHeatMap colorScale inverted
def colorNodes(graph,tpX_s,viewColor):
  tpX_sValues=[]
  for n in graph.getNodes():
    tpX_sValues.append(tpX_s[n])
  highestTpX_sValue = max(tpX_sValues)
  colorScale=tlpgui.ColorScalesManager.getColorScale("BiologicalHeatMap")

  for n in graph.getNodes():
    color=colorScale.getColorAtPos(1-(tpX_s[n]/highestTpX_sValue))
    viewColor[n]=color

#function used to color the nodes of a graph using doubleProperties argument
def colorNodes2(graph,prop,viewColor):
  mini = prop.getNodeMin()
  maxi = prop.getNodeMax()
  colorScale=tlp.ColorScale([])
  colorScale.setColorAtPos(mini,tlp.Color.Aquamarine)
  colorScale.setColorAtPos(maxi,tlp.Color.ChartreuseGreen)

  for n in graph.getNodes():
    color=colorScale.getColorAtPos(prop[n])
    viewColor[n]=color 
    
#Question2.4
def calcNodesDepth(tree,metric):
  root=tree.getSource()
  depth=0
  calcNodesDepthRec(tree,metric,depth,root)

def calcNodesDepthRec(tree,metric,depth,root):
  metric[root]=depth
  depth+=1
  for n in root.getNodes():
    calcNodesDepthRec(tree,metric,depth,n)
  
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
  if graph.getSubGraph("hierarchical_tree"):
    graph.delSubGraph(graph.getSubGraph("hierarchical_tree"))
  graph.addSubGraph("hierarchical_tree")
  g=graph.getSubGraph("hierarchical_tree")
  gi=graph.getSubGraph("Genes interactions")
  create_hierarchical_tree(g,gi)
  g.applyLayoutAlgorithm("Tree Radial")
  colorNodes(g,tp1_s,viewColor)
  calcNodesDepth(g,viewMetric)
