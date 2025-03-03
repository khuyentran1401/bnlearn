Structure learning
===================

With structure learning we can estimate a DAG that captures the dependencies between the variables in the data set.
However, realize that the search space of DAGs is super-exponential in the number of variables and you may end up in finding a local maxima. Commonly used scoring functions to measure the fit between model and data are Bayesian Dirichlet scores such as BDeu or K2 and the Bayesian Information Criterion (BIC, also called MDL). BDeu is dependent on an equivalent sample size. To learn model structure (a DAG) from a data set, there are three broad techniques:

**Score-based structure learning:**

* Exhaustivesearch
* Hillclimbsearch
* Chow-liu
* Tree-augmented Naive Bayes (TAN)
* NaiveBayes

**Constraint-based structure learning:**

* chi-square test

**Hybrid structure learning:**

* The combination of both techniques (MMHC)


Exhaustivesearch
===================

ExhaustiveSearch can be used to compute the score for every DAG and returns the best-scoring one.
This search approach is only atractable for very small networks, and prohibits efficient local optimization algorithms to always find the optimal structure. Thus, identifiying the ideal structure is often not tractable. Despite these bad news, heuristic search strategies often yields good results. If only few nodes are involved (read: less than 5 or so).


Hillclimbsearch
===================

Once more nodes are involved, one needs to switch to heuristic search. HillClimbSearch implements a greedy local search that starts from the DAG "start" (default: disconnected DAG) and proceeds by iteratively performing single-edge manipulations that maximally increase the score. The search terminates once a local maximum is found.


Constraint-based
===================

A different, but quite straightforward approach to build a DAG from data is to identify independencies in the data set using hypothesis tests, such as chi2 test statistic. The p_value of the test, and a heuristig flag that indicates if the sample size was sufficient. The p_value is the probability of observing the computed chi2 statistic (or an even higher chi2 value), given the null hypothesis that X and Y are independent given Zs. This can be used to make independence judgements, at a given level of significance.

  1. Hypothesis tests
  2. Construct DAG (pattern) according to identified independencies (Conditional) Independence Tests
  3. Independencies in the data can be identified using chi2 conditional independence tests.



Chow-liu
===================

The Chow-Liu Algorithm is a Tree search based approach. The Chow-Liu algorithm finds the maximum-likelihood tree structure where each node has at most one parent. Note that here our score is simply the maximum likelihood, we do not need to penalize the complexity since we are already limiting complexity by restricting ourselves to tree structures[1].

The algorithm has three steps:

	1. Compute the mutual information for all pairs of variables X,U. This function measures how much information U provides about X
	2. Find the maximum weight spanning tree: the maximal-weight tree that connects all vertices in a graph. This can be found using Kruskal or Prim Algorithms
	3. Pick any node to be the root variable, and assign directions radiating outward from this node (arrows go away from it). This step transforms the resulting undirected tree to a directed one.


Tree-augmented Naive Bayes (TAN) 
======================================
Tree augmented naive Bayes or TAN is a semi-naive Bayesian Learning method. It relaxes the naive Bayes attribute independence assumption by employing a tree structure, in which each attribute only depends on the class and one other attribute. A maximum weighted spanning tree that maximizes the likelihood of the training data is used to perform classification [2].

The algorithm has three steps:

	1. Approximate the dependencies among features with a tree Bayes net.
	2. Tree induction algorithm
		* Optimality: Maximum likelihood tree
		* Efficiency: Polynomial algorithm
	3. Robust parameter estimation


NaiveBayes
===================
Naive Bayes is a special case of Bayesian Model where the only edges in the model are from the feature variables to the dependent variable.

The method requires specifying: 

    1. The root node.
    2. Edges should start from the root node.
    3. MaximumLikelihood estimator is the default.


Example to design a DAG with the naivebayes model:

.. code-block:: python

    # Load library
    from pgmpy.factors.discrete import TabularCPD
    import bnlearn as bn
    
    # Create some edges, all starting from the same root node: A
    edges = [('A', 'B'), ('A', 'C'), ('A', 'D')]
    DAG = bn.make_DAG(edges, methodtype='naivebayes')
    
    # Set CPDs
    cpd_A = TabularCPD(variable='A', variable_card=3, values=[[0.3], [0.5], [0.2]])
    cpd_B = TabularCPD(variable='B', variable_card=2, values=[[0.4, 0.9], [0.6, 0.1]], evidence=['A'], evidence_card=[2])
    cpd_C = TabularCPD(variable='C', variable_card=2, values=[[0.4, 0.9], [0.6, 0.1]], evidence=['A'], evidence_card=[2])
    cpd_D = TabularCPD(variable='D', variable_card=2, values=[[0.4, 0.9], [0.6, 0.1]], evidence=['A'], evidence_card=[2])
    
    # Make the DAG
    DAG = bn.make_DAG(DAG, CPD=[cpd_A, cpd_B, cpd_C, cpd_D], checkmodel=True)
    # Plot the CPDs as a sanity check
    bn.print_CPD(DAG, checkmodel=True)
    # Plot the DAG
    bn.plot(DAG)


.. _fig-naivebayes_1:

.. figure:: ../figs/naivebayes_example1.png


Example for structure learning with the naivebayes model:

.. code-block:: python

    # Load library
    import bnlearn as bn
    # Load example
    df = bn.import_example('random')
    # Structure learning
    model = bn.structure_learning.fit(df, methodtype='naivebayes', root_node="B")
    # Plot
    bn.plot(model)


.. _fig-naivebayes_2:

.. figure:: ../figs/naivebayes_example2.png


Examples Structure learning
=====================================

A different, but quite straightforward approach to build a DAG from data is to identify independencies in the data set using hypothesis tests, such as chi2 test statistic. The p_value of the test, and a heuristic flag that indicates if the sample size was sufficient. The p_value is the probability of observing the computed chi2 statistic (or an even higher chi2 value), given the null hypothesis that X and Y are independent given Zs. This can be used to make independence judgements, at a given level of significance.

Example (1)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For this example, we will be investigating the sprinkler data set. This is a very simple data set with 4 variables and each variable can contain value [1] or [0]. The question we can ask: What are the relationships and dependencies across the variables? Note that his data set is already pre-processed and no missing values are present.


Let's bring in our dataset.

.. code-block:: python

  import bnlearn as bn
  df = bn.import_example()
  df.head()


.. table::

  +--------+-----------+------+-------------+
  |Cloudy  | Sprinkler | Rain |  Wet_Grass  |
  +========+===========+======+=============+
  |    0   |      1    |  0   |      1      |
  +--------+-----------+------+-------------+
  |    1   |      1    |  1   |      1      |
  +--------+-----------+------+-------------+
  |    1   |      0    |  1   |      1      |
  +--------+-----------+------+-------------+
  |    ... |      ...  | ...  |     ...     |
  +--------+-----------+------+-------------+
  |    0   |      0    |  0   |      0      |
  +--------+-----------+------+-------------+
  |    1   |      0    |  0   |      0      |
  +--------+-----------+------+-------------+
  |    1   |      0    |  1   |      1      |
  +--------+-----------+------+-------------+

From the *bnlearn* library, we'll need the :class:`~bnlearn.structure_learning.fit` for this exercise:

.. code-block:: python

  model = bn.structure_learning.fit(df)
  G = bn.plot(model)


.. _fig-sl:

.. figure:: ../figs/fig_sprinkler_sl.png

  Learned structure on the Sprinkler data set.
   

We can specificy the method and scoring type. As described previously, some methods are more expensive to run then others. Make the decision on the number of variables, hardware in your machine, time you are willing to wait etc

**Method types:**

* hillclimbsearch or hc (greedy local search if many more nodes are involved)
* exhaustivesearch or ex (exhaustive search for very small networks)
* constraintsearch or cs (Constraint-based Structure Learning by first identifing independencies in the data set using hypothesis test, chi2)

**Scoring types:**

* bic
* k2
* bdeu


.. code-block:: python

  model_hc_bic  = bn.structure_learning.fit(df, methodtype='hc', scoretype='bic')
  model_hc_k2   = bn.structure_learning.fit(df, methodtype='hc', scoretype='k2')
  model_hc_bdeu = bn.structure_learning.fit(df, methodtype='hc', scoretype='bdeu')
  model_ex_bic  = bn.structure_learning.fit(df, methodtype='ex', scoretype='bic')
  model_ex_k2   = bn.structure_learning.fit(df, methodtype='ex', scoretype='k2')
  model_ex_bdeu = bn.structure_learning.fit(df, methodtype='ex', scoretype='bdeu')



Example (2)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Lets learn the structure of a more complex data set and compare it to another one.

.. code-block:: python

  import bnlearn as bn
  # Load asia DAG
  model_true = bn.import_DAG('asia')
  # plot ground truth
  G = bn.plot(model_true)

.. _fig2a_asia_groundtruth:

.. figure:: ../figs/fig2a_asia_groundtruth.png

  True DAG of the Asia data set.

  
.. code-block:: python

  # Sampling
  df = bn.sampling(model_true, n=10000)
  # Structure learning of sampled dataset
  model_learned = bn.structure_learning.fit(df, methodtype='hc', scoretype='bic')

.. _fig2b_asia_structurelearning:

.. figure:: ../figs/fig2b_asia_structurelearning.png

  Learned DAG based on data set.


.. code-block:: python

  # Plot based on structure learning of sampled data
  bn.plot(model_learned, pos=G['pos'])
  # Compare networks and make plot
  bn.compare_networks(model_true, model_learned, pos=G['pos'])

.. _fig2c_asia_comparion:

.. figure:: ../figs/fig2c_asia_comparion.png
.. figure:: ../figs/fig2d_confmatrix.png

  Comparison True vs. learned DAG.


References
1. https://ermongroup.github.io/cs228-notes/learning/structure/
2. https://doi.org/10.1007/978-0-387-30164-8_850
