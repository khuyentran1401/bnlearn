Topological sort
========================

Topological sort or topological ordering of a directed graph is a linear ordering of its vertices and only possible if and only if the graph has no directed cycles, that is, if it is a directed acyclic graph (DAG).
Any DAG has at least one topological ordering. Topological sorting has many applications especially in ranking problems such as feedback arc set. The vertices of the graph may represent the tasks to be performed, and the edges may represent constraints that one task must be performed before another.
A topological ordering is, simply said, just a valid sequence for the tasks. In ``bnlearn`` we can also derive the topological ordering of the graph.


Lets create the underneath DAG and examine the topological ordering of 1. the entire graph, and 2. using a starting point in the graph.

.. _fig_topological_graph_example:

.. figure:: ../figs/topological_graph_example.png


**Topological ordering example 1**

.. code-block:: python
    
    # Import bnlearn
    import bnlearn as bn

    # Set Edges in graph
    edges = [('1', '2'),
         ('1', '3'),
         ('2', '4'),
         ('2', '3'),
         ('3', '4'),
         ('3', '5'),
         ]
    
    # Make the actual Bayesian DAG
    DAG = bn.make_DAG(edges, verbose=0)

    # Plot
    bn.plot(DAG)

    # Topological ordering of the entire graph
    bn.topological_sort(DAG)

    #>['1', '2', '3', '4', '5']

    # Topological ordering using starting point in graph
    bn.topological_sort(DAG, '2')

    #>['2', '3', '5', '4']


It is also possible to examine the topological ordering of your learned DAG using structure learning. 

**Topological ordering example 2**

.. code-block:: python

    # Import bnlearn
    import bnlearn as bn
    
    # Import DAG
    DAG = bn.import_DAG('sprinkler')
    # Generate data using the DAG
    df = bn.sampling(DAG, n=1000, verbose=0)
    # Structure learning
    model = bn.structure_learning.fit(df, methodtype='chow-liu', root_node='Wet_Grass')
    G = bn.plot(model)
    # Topological ordering of the entire graph
    bn.topological_sort(model)