# pip install pytest
# pytest tests\test_bn.py

from pgmpy.factors.discrete import TabularCPD
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pgmpy.estimators import TreeSearch
from pgmpy.models import BayesianModel
import networkx as nx
from pgmpy.inference import VariableElimination
from pgmpy.estimators import BDeuScore, K2Score, BicScore
import bnlearn as bn


def test_import_DAG():
    import bnlearn as bn
    DAG = bn.import_DAG('Sprinkler')
    # TEST 1: check output is unchanged
    assert [*DAG.keys()]==['model', 'adjmat']
    # TEST 2: Check model output is unchanged
    assert DAG['adjmat'].sum().sum()==4
    # TEST 3:
    assert 'pgmpy.models.BayesianModel.BayesianModel' in str(type(DAG['model']))
    # TEST 4:
    DAG = bn.import_DAG('alarm', verbose=0)
    assert [*DAG.keys()]==['model', 'adjmat']
    DAG = bn.import_DAG('andes', verbose=0)
    assert [*DAG.keys()]==['model', 'adjmat']
    DAG = bn.import_DAG('asia', verbose=0)
    assert [*DAG.keys()]==['model', 'adjmat']


def test_make_DAG():
    import bnlearn as bn
    edges = [('Cloudy', 'Sprinkler')]
    methodtypes = ['bayes', 'naivebayes']
    for methodtype in methodtypes:
        DAG = bn.make_DAG(edges, methodtype=methodtype)
        # TEST 1
        if methodtype=='bayes':
            assert 'pgmpy.models.BayesianModel.BayesianModel' in str(type(DAG['model']))
        else:
            assert 'pgmpy.models.NaiveBayes.NaiveBayes' in str(type(DAG['model']))
    # TEST 2
    cpt_cloudy = TabularCPD(variable='Cloudy', variable_card=2, values=[[0.3], [0.7]])
    cpt_sprinkler = TabularCPD(variable='Sprinkler', variable_card=2, values=[[0.4, 0.9], [0.6, 0.1]], evidence=['Cloudy'], evidence_card=[2])
    assert bn.make_DAG(DAG, CPD=[cpt_cloudy, cpt_sprinkler], checkmodel=True)
    # TEST 3
    assert np.all(np.isin([*DAG.keys()], ['adjmat', 'model', 'methodtype', 'model_edges']))


def test_make_DAG():
    import bnlearn as bn
    # TEST 1:
    df = bn.import_example()
    assert df.shape==(1000, 4)


def test_sampling():
    import bnlearn as bn
    # TEST 1:
    model = bn.import_DAG('Sprinkler')
    n = np.random.randint(10, 1000)
    df = bn.sampling(model, n=n)
    assert df.shape==(n, 4)


def test_to_undirected():
    import bnlearn as bn
    # TEST 1:
    randdata=['sprinkler', 'alarm', 'andes', 'asia', 'sachs']
    n = np.random.randint(0, len(randdata))
    DAG = bn.import_DAG(randdata[n], CPD=False, verbose=0)
    assert (DAG['adjmat'].sum().sum() *2)==bn.to_undirected(DAG['adjmat']).sum().sum()


def test_compare_networks():
    import bnlearn as bn
    DAG = bn.import_DAG('Sprinkler', verbose=0)
    G = bn.compare_networks(DAG, DAG, showfig=False)
    assert np.all(G[0]==[[12, 0], [0, 4]])


def test_adjmat2vec():
    import bnlearn as bn
    DAG = bn.import_DAG('Sprinkler', verbose=0)
    out = bn.adjmat2vec(DAG['adjmat'])
    assert np.all(out['source']==['Cloudy', 'Cloudy', 'Sprinkler', 'Rain'])


def test_vec2adjmat():
    import bnlearn as bn
    DAG = bn.import_DAG('Sprinkler', verbose=0)
    out = bn.adjmat2vec(DAG['adjmat'])
    # TEST: conversion
    assert bn.vec2adjmat(out['source'], out['target']).shape==DAG['adjmat'].shape


def test_structure_learning():
    import bnlearn as bn
    df = bn.import_example()
    model = bn.structure_learning.fit(df)
    assert [*model.keys()]==['model', 'model_edges', 'adjmat', 'config']
    model = bn.structure_learning.fit(df, methodtype='hc', scoretype='bic')
    assert [*model.keys()]==['model', 'model_edges', 'adjmat', 'config']
    model = bn.structure_learning.fit(df, methodtype='hc', scoretype='k2')
    assert [*model.keys()]==['model', 'model_edges', 'adjmat', 'config']
    model = bn.structure_learning.fit(df, methodtype='cs', scoretype='bdeu')
    assert [*model.keys()]==['undirected', 'undirected_edges', 'pdag', 'pdag_edges', 'dag', 'dag_edges', 'model', 'model_edges', 'adjmat', 'config']
    model = bn.structure_learning.fit(df, methodtype='cs', scoretype='k2')
    assert [*model.keys()]==['undirected', 'undirected_edges', 'pdag', 'pdag_edges', 'dag', 'dag_edges', 'model', 'model_edges', 'adjmat', 'config']
    model = bn.structure_learning.fit(df, methodtype='ex', scoretype='bdeu')
    assert [*model.keys()]==['model', 'model_edges', 'adjmat', 'config']
    model = bn.structure_learning.fit(df, methodtype='ex', scoretype='k2')
    assert [*model.keys()]==['model', 'model_edges', 'adjmat', 'config']
    model = bn.structure_learning.fit(df, methodtype='cl', root_node='Cloudy')
    assert [*model.keys()]==['model', 'model_edges', 'adjmat', 'config']
    model = bn.structure_learning.fit(df, methodtype='tan', root_node='Cloudy', class_node='Rain')
    assert [*model.keys()]==['model', 'model_edges', 'adjmat', 'config']

    # Test the filtering
    DAG = bn.import_DAG('asia')
    # Sampling
    df = bn.sampling(DAG, n=1000)
    # Structure learning of sampled dataset
    model = bn.structure_learning.fit(df)
    assert np.all(np.isin(model['adjmat'].columns.values, ['smoke', 'bronc', 'lung', 'asia', 'tub', 'either', 'dysp', 'xray']))

    # hc filter on edges
    model = bn.structure_learning.fit(df, methodtype='hc', white_list=['smoke', 'either'], bw_list_method='nodes')
    assert np.all(model['adjmat'].columns.values==['smoke', 'either'])
    model = bn.structure_learning.fit(df, methodtype='hc', white_list=[('smoke', 'either')], bw_list_method='edges')
    assert np.all(np.isin(model['adjmat'].columns.values, ['smoke', 'bronc', 'lung', 'asia', 'tub', 'either', 'dysp', 'xray']))
    model = bn.structure_learning.fit(df, methodtype='hc', black_list=['smoke', 'either'], bw_list_method='nodes')
    assert np.all(np.isin(model['adjmat'].columns.values, ['bronc', 'lung', 'asia', 'tub', 'dysp', 'xray']))
    model = bn.structure_learning.fit(df, methodtype='hc', scoretype='bic', black_list=['smoke', 'either'], bw_list_method='edges')
    assert np.all(np.isin(model['adjmat'].columns.values, ['smoke', 'bronc', 'lung', 'asia', 'tub', 'either', 'dysp', 'xray']))
    # hc filter on node
    model = bn.structure_learning.fit(df, methodtype='ex', white_list=['smoke', 'either'], bw_list_method='nodes')
    assert np.all(model['adjmat'].columns.values==['either', 'smoke'])
    model = bn.structure_learning.fit(df, methodtype='ex', black_list=['asia', 'tub', 'either', 'dysp', 'xray'], bw_list_method='nodes')
    assert np.all(model['adjmat'].columns.values==['bronc', 'lung', 'smoke'])
    # cs filter
    model = bn.structure_learning.fit(df, methodtype='cs', white_list=['smoke', 'either'], bw_list_method='nodes')
    assert np.all(np.isin(model['adjmat'].columns.values, ['smoke', 'either']))
    model= bn.structure_learning.fit(df, methodtype='cs', black_list=['asia', 'tub', 'either', 'dysp', 'xray'], bw_list_method='nodes')
    assert np.all(np.isin(model['adjmat'].columns.values, ['smoke', 'lung', 'bronc']))
    # cl filter
    model = bn.structure_learning.fit(df, methodtype='cl', white_list=['smoke', 'either'], bw_list_method='nodes', root_node='smoke')
    assert np.all(model['adjmat'].columns.values==['smoke', 'either'])
    # tan
    model = bn.structure_learning.fit(df, methodtype='tan', white_list=['smoke', 'either'], bw_list_method='nodes', root_node='smoke', class_node='either')
    assert np.all(model['adjmat'].columns.values==['smoke', 'either'])
    # naivebayes
    model = bn.structure_learning.fit(df, methodtype='naivebayes', root_node="smoke")
    assert np.all(model['adjmat'].columns.values==['smoke', 'asia', 'tub', 'lung', 'bronc', 'either', 'xray', 'dysp'])

    df=bn.import_example(data='andes')

    # PGMPY
    est = TreeSearch(df)
    dag = est.estimate(estimator_type="tan", class_node='DISPLACEM0')
    bnq = BayesianModel(dag.edges())
    bnq.fit(df, estimator=None)  # None means maximum likelihood estimator
    bn_infer = VariableElimination(bnq)
    q = bn_infer.query(variables=['DISPLACEM0'], evidence={'RApp1': 1})
    print(q)

    # BNLEARN
    model = bn.structure_learning.fit(df, methodtype='tan', class_node='DISPLACEM0', scoretype='bic')
    model_bn = bn.parameter_learning.fit(model, df, methodtype='ml')  # maximum likelihood estimator
    query=bn.inference.fit(model_bn, variables=['DISPLACEM0'], evidence={'RApp1': 1})

    # DAG COMPARISON
    assert np.all(model_bn['adjmat']==model['adjmat'])
    assert list(dag.edges())==list(model['model'].edges())
    assert list(dag.edges())==model['model_edges']

    # COMPARE THE CPDs names
    qbn_cpd = []
    bn_cpd = []
    for cpd in bnq.get_cpds(): qbn_cpd.append(cpd.variable)
    for cpd in model_bn['model'].get_cpds(): bn_cpd.append(cpd.variable)

    assert len(bn_cpd)==len(qbn_cpd)
    assert np.all(np.isin(bn_cpd, qbn_cpd))

    # COMPARE THE CPD VALUES
    nr_diff = 0
    for cpd_bnlearn in model_bn['model'].get_cpds():
        for cpd_pgmpy in bnq.get_cpds():
            if cpd_bnlearn.variable==cpd_pgmpy.variable:
                assert np.all(cpd_bnlearn.values==cpd_pgmpy.values)
                # if not np.all(cpd_bnlearn.values==cpd_pgmpy.values):
                # print('%s-%s'%(cpd_bnlearn.variable, cpd_pgmpy.variable))
                # print(cpd_bnlearn)
                # print(cpd_pgmpy)
                # nr_diff=nr_diff+1
                # input('press enter to see the next difference in CPD.')


def test_parameter_learning():
    import bnlearn as bn
    df = bn.import_example()
    model = bn.import_DAG('sprinkler', CPD=False)
    model_update = bn.parameter_learning.fit(model, df)
    assert [*model_update.keys()]==['model', 'adjmat', 'config', 'model_edges']


def test_inference():
    import bnlearn as bn
    DAG = bn.import_DAG('sprinkler')
    q1 = bn.inference.fit(DAG, variables=['Wet_Grass'], evidence={'Rain': 1, 'Sprinkler': 0, 'Cloudy': 1}, to_df=False, verbose=0)
    assert 'pgmpy.factors.discrete.DiscreteFactor.DiscreteFactor' in str(type(q1))
    assert q1.df is None
    q1 = bn.inference.fit(DAG, variables=['Wet_Grass'], evidence={'Rain': 1, 'Sprinkler': 0, 'Cloudy': 1}, to_df=True, verbose=0)
    assert q1.df is not None


def test_query2df():
    import bnlearn as bn
    DAG = bn.import_DAG('sprinkler')
    query = bn.inference.fit(DAG, variables=['Wet_Grass'], evidence={'Rain': 1, 'Sprinkler': 0, 'Cloudy': 1}, to_df=False, verbose=0)
    df = bn.query2df(query)
    assert df.shape==(2, 2)
    assert np.all(df.columns==['Wet_Grass', 'p'])
    query = bn.inference.fit(DAG, variables=['Wet_Grass', 'Sprinkler'], evidence={'Rain': 1, 'Cloudy': 1}, to_df=False, verbose=0)
    df = bn.query2df(query)
    assert np.all(np.isin(df.columns, ['Sprinkler', 'Wet_Grass', 'p']))
    assert df.shape==(4, 3)

    # Load example mixed dataset
    df_raw = bn.import_example(data='titanic')
    # Convert to onehot
    dfhot, dfnum = bn.df2onehot(df_raw)
    dfnum.loc[0:50, 'Survived'] = 2
    # Structure learning
    # DAG = bn.structure_learning.fit(dfnum, methodtype='cl', black_list=['Embarked','Parch','Name'], root_node='Survived', bw_list_method='nodes')
    DAG = bn.structure_learning.fit(dfnum, methodtype='hc', black_list=['Embarked', 'Parch', 'Name'], bw_list_method='edges')
    # Parameter learning
    model = bn.parameter_learning.fit(DAG, dfnum)
    # Make inference
    q1 = bn.inference.fit(model, variables=['Survived'], evidence={'Sex': True, 'Pclass': True}, verbose=0)
    df = bn.query2df(q1)
    assert np.all(df==q1.df)
    assert df.shape==(3, 2)


def test_predict():
    import bnlearn as bn
    df = bn.import_example('asia')
    edges = [('smoke', 'lung'),
             ('smoke', 'bronc'),
             ('lung', 'xray'),
             ('bronc', 'xray')]

    # Make the actual Bayesian DAG
    DAG = bn.make_DAG(edges, verbose=0)
    model = bn.parameter_learning.fit(DAG, df, verbose=3)
    # Generate some data based on DAG
    Xtest = bn.sampling(model, n=100)
    out = bn.predict(model, Xtest, variables=['bronc', 'xray'])
    assert np.all(np.isin(out.columns, ['bronc', 'xray', 'p']))
    assert out.shape==(100, 3)
    out = bn.predict(model, Xtest, variables=['smoke', 'bronc', 'lung', 'xray'])
    assert np.all(np.isin(out.columns, ['xray', 'bronc', 'lung', 'smoke', 'p']))
    assert out.shape==(100, 5)
    out = bn.predict(model, Xtest, variables='smoke')
    assert np.all(out.columns==['smoke', 'p'])
    assert out.shape==(100, 2)


def test_topological_sort():
    import bnlearn as bn
    DAG = bn.import_DAG('sprinkler')
    # Check DAG input
    assert bn.topological_sort(DAG, 'Rain')==['Rain', 'Wet_Grass']
    assert bn.topological_sort(DAG)==['Cloudy', 'Sprinkler', 'Rain', 'Wet_Grass']
    # Different inputs
    assert bn.topological_sort(DAG['adjmat'], 'Rain')==['Rain', 'Wet_Grass']
    assert bn.topological_sort(bn.adjmat2vec(DAG['adjmat']), 'Rain')
    # Check model output
    df = bn.import_example('sprinkler')
    model = bn.structure_learning.fit(df, methodtype='chow-liu', root_node='Wet_Grass')
    assert bn.topological_sort(model, 'Rain')==['Rain', 'Cloudy', 'Sprinkler']


def test_save():
    import bnlearn as bn
    # Load asia DAG
    df = bn.import_example('asia')
    model = bn.structure_learning.fit(df, methodtype='tan', class_node='lung')
    bn.save(model, overwrite=True)
    # Load the DAG
    model_load = bn.load()
    assert model.keys()==model_load.keys()
    for key in model.keys():
        if not key=='model':
            assert np.all(model[key]==model_load[key])

    edges = [('smoke', 'lung'),
             ('smoke', 'bronc'),
             ('lung', 'xray'),
             ('bronc', 'xray')]

    # Make the actual Bayesian DAG
    DAG = bn.make_DAG(edges, verbose=0)
    # Save the DAG
    bn.save(DAG, overwrite=True)
    # Load the DAG
    DAGload = bn.load()
    # Compare
    assert DAG.keys()==DAGload.keys()
    for key in DAG.keys():
        if not key=='model':
            assert np.all(DAG[key]==DAGload[key])

    # Learn its parameters from data and perform the inference.
    model = bn.parameter_learning.fit(DAG, df, verbose=0)
    # Save the DAG
    bn.save(model, overwrite=True)
    # Load the DAG
    model_load = bn.load()
    # Compare
    assert model.keys()==model_load.keys()
    for key in model.keys():
        if not key=='model':
            assert np.all(model[key]==model_load[key])


def test_independence_test():
    import bnlearn as bn
    df = bn.import_example(data='asia')
    # Structure learning of sampled dataset
    model = bn.structure_learning.fit(df)
    # Compute edge weights based on chi_square test statistic
    tests = ['chi_square', 'g_sq', 'log_likelihood', 'freeman_tuckey', 'modified_log_likelihood', 'neyman', 'cressie_read']
    for test in tests:
        model = bn.independence_test(model, df, test=test)
        assert model.get('independence_test', None) is not None
        assert set(model['independence_test'].columns)==set({test, 'dof', 'p_value', 'source', 'stat_test', 'target'})
        assert model['independence_test'].columns[-2]==test
        assert np.any(model['independence_test']['stat_test'])
        assert model['independence_test'].shape[0]>1

    DAG = bn.import_DAG('water', verbose=0)
    # Sampling
    df = bn.sampling(DAG, n=1000)
    # Parameter learning
    model = bn.parameter_learning.fit(DAG, df)
    # Test for independence
    model1 = bn.independence_test(model, df, prune=False)
    # Test for independence
    model2 = bn.independence_test(model, df, prune=True)
    assert model['model_edges']==model1['model_edges']
    assert len(model1['model_edges'])==model1['independence_test'].shape[0]
    assert len(model2['model_edges'])==model2['independence_test'].shape[0]
    assert len(model2['model_edges'])<len(model1['model_edges'])
    assert len(model2['model_edges'])<len(model['model_edges'])


def test_edge_properties():
    import bnlearn as bn
    # Example 1
    edges = [('A', 'B'), ('A', 'C'), ('A', 'D')]
    # Create DAG and store in model
    model = bn.make_DAG(edges)
    edge_properties = bn.get_edge_properties(model)
    # Check availability of properties
    assert edge_properties[('A', 'B')].get('color')
    assert edge_properties[('A', 'B')].get('weight')
    assert edge_properties[('A', 'C')].get('color')
    assert edge_properties[('A', 'C')].get('weight')
    assert edge_properties[('A', 'D')].get('color')
    assert edge_properties[('A', 'D')].get('weight')
    # Make plot
    assert bn.plot(model, edge_properties=edge_properties, interactive=False)
    assert bn.plot(model, interactive=False)

    edges = [('A', 'B'), ('A', 'C'), ('A', 'D')]
    # Create DAG and store in model
    methodtypes=['bayes', 'naivebayes']
    for methodtype in methodtypes:
        model = bn.make_DAG(edges, methodtype=methodtype)
        # Remove methodtype
        model['methodtype']=''
        # Check if it is restored to the correct methodtype
        model = bn.make_DAG(model['model'])
        assert model['methodtype']==methodtype

    # Load asia DAG
    df = bn.import_example(data='asia')
    # Structure learning of sampled dataset
    model = bn.structure_learning.fit(df)
    edge_properties1 = bn.get_edge_properties(model)
    assert np.all(pd.DataFrame(edge_properties1).iloc[1, :]==1)
    # Compute edge weights based on chi_square test statistic
    model = bn.independence_test(model, df, test='chi_square')
    # Get the edge properties
    edge_properties2 = bn.get_edge_properties(model)
    assert np.sum(pd.DataFrame(edge_properties2).iloc[1, :]>1)>len(edge_properties2) -2
