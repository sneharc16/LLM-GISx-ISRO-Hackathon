from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment="GeoSolarX System Architecture", format="png")
dot.attr(rankdir='LR', fontsize='12')

# Data stores box
with dot.subgraph(name='cluster_data') as data:
    data.attr(label='Data Stores', style='rounded,filled', color='lightgrey', fillcolor='white')
    data.node('STAC', 'Satellite images\n(STAC APIs)', style='filled', fillcolor='lightblue')
    data.node('GIS', 'GIS layers\n(local database)', style='filled', fillcolor='lightblue')
    data.node('BYO', 'Bring your own data\n(Satellite image)', style='filled', fillcolor='lightblue')

# Chain of Thought box
with dot.subgraph(name='cluster_reasoning') as reasoning:
    reasoning.attr(label='Chain of thought reasoning model', style='rounded,filled', color='lightgrey', fillcolor='white')
    reasoning.node('Reader', 'Data reader', style='filled', fillcolor='lavender')
    reasoning.node('GeoLibs', 'Geoprocessing\nLibraries', style='filled', fillcolor='lavender')
    reasoning.node('RenderAPI', 'Mapping rendering APIs', style='filled', fillcolor='lavender')

# UI box
with dot.subgraph(name='cluster_ui') as ui:
    ui.attr(label='Interactive visualization interface', style='rounded,filled', color='lightgrey', fillcolor='white')
    ui.node('Map', 'Map rendering', style='filled', fillcolor='lightblue')
    ui.node('Chat', 'Chat window', style='filled', fillcolor='lightblue')
    ui.node('Graph', 'Graph plotting\n(Optional)', style='filled', fillcolor='lightblue')

# Knowledgebase box
dot.node('Docs', 'Knowledgebase from API documentation of\ngeoprocessing APIs such as PyQGIS/GDAL or equivalent',
         shape='box', style='rounded,filled', fillcolor='lightgrey')

# Connections
dot.edge('STAC', 'Reader')
dot.edge('GIS', 'Reader')
dot.edge('BYO', 'Reader')

dot.edge('Docs', 'Reader')
dot.edge('Docs', 'GeoLibs')
dot.edge('Docs', 'RenderAPI')

dot.edge('Reader', 'GeoLibs')
dot.edge('GeoLibs', 'RenderAPI')
dot.edge('RenderAPI', 'Map')
dot.edge('RenderAPI', 'Chat')
dot.edge('RenderAPI', 'Graph')

# Save and render
dot.render('geosolarx_architecture', view=True)
