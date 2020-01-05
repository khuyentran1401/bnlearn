# bnlearn

[![Python](https://img.shields.io/pypi/pyversions/bnlearn)](https://img.shields.io/pypi/pyversions/bnlearn)
[![PyPI Version](https://img.shields.io/pypi/v/bnlearn)](https://pypi.org/project/bnlearn/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/erdogant/bnlearn/blob/master/LICENSE)

* Bnlearn is Python package for learning the graphical structure of Bayesian networks, parameter learning, inference and sampling methods. This work is inspired by the R package (bnlearn.com) that has been very usefull to me for many years. Although there are very good Python packages for probabilistic graphical models, it still can remain difficult (and somethimes unnecessarily) to (re)build certain pipelines. Bnlearn for python (this package) is build on the <a href="https://github.com/pgmpy/pgmpy">pgmpy</a> package and contains the most-wanted pipelines.

## Method overview
Learning a Bayesian network can be split into two problems which are both implemented in this package:
* Structure learning: Given a set of data samples, estimate a DAG that captures the dependencies between the variables.
* Parameter learning: Given a set of data samples and a DAG that captures the dependencies between the variables, estimate the (conditional) probability distributions of the individual variables.

#### The following functions are available:
```python
 .structure_learning()
 .parameter_learning()
 .inference()
  # Based on a DAG, you can sample the number of samples you want.
 .sampling()
  # Load five well known examples to play arround with or load your own .bif file.
 .load_example()
  # Compare 2 graphs
 .compare_networks()
  # Plot graph
 .plot()
  # To make the directed grapyh undirected
 .to_undirected()
 
See below for the exact working of the functions
```

#### The following methods are also included:
* inference
* sampling
* comparing two networks
* loading bif files
* conversion of directed to undirected graphs

## Contents
- [Installation](#-installation)
- [Requirements](#-Requirements)
- [Quick Start](#-quick-start)
- [Contribute](#-contribute)
- [Citation](#-citation)
- [Maintainers](#-maintainers)
- [License](#-copyright)

## Installation
* Install bnlearn from PyPI (recommended). bnlearn is compatible with Python 3.6+ and runs on Linux, MacOS X and Windows. 
* It is distributed under the MIT license.

## Requirements
* It is advisable to create a new environment. 
* Pgmpy requires an older version of networkx and matplotlib.
```python
conda create -n env_BNLEARN python=3.6
conda activate env_BNLEARN
conda install pytorch
pip install sklearn pandas tqdm funcsigs pgmpy statsmodels community
pip install networkx==v1.11
pip install matplotlib==2.2.3
```

## Quick Start
```
pip install bnlearn
```

* Alternatively, install bnlearn from the GitHub source:
```bash
git clone https://github.com/erdogant/bnlearn.git
cd bnlearn
python setup.py install
```  

## Import bnlearn package
```python
import bnlearn as bnlearn
```

## Example: Structure Learning
```python
df = pd.read_csv('https://github.com/erdogant/hnet/blob/master/bnlearn/data/sprinkler_data.csv')
model = bnlearn.structure_learning(df)
G = bnlearn.plot(model)
```

#### df looks like this
```
     Cloudy  Sprinkler  Rain  Wet_Grass
0         0          1     0          1
1         1          1     1          1
2         1          0     1          1
3         0          0     1          1
4         1          0     1          1
..      ...        ...   ...        ...
995       0          0     0          0
996       1          0     0          0
997       0          0     1          0
998       1          1     0          1
999       1          0     1          1
```

<p align="center">
  <img src="https://github.com/erdogant/bnlearn/blob/master/docs/figs/fig_sprinkler_sl.png" width="600" />
</p>

* Choosing various methodtypes and scoringtypes:
```python
model_hc_bic  = bnlearn.structure_learning(df, methodtype='hc', scoretype='bic')
model_hc_k2   = bnlearn.structure_learning(df, methodtype='hc', scoretype='k2')
model_hc_bdeu = bnlearn.structure_learning(df, methodtype='hc', scoretype='bdeu')
model_ex_bic  = bnlearn.structure_learning(df, methodtype='ex', scoretype='bic')
model_ex_k2   = bnlearn.structure_learning(df, methodtype='ex', scoretype='k2')
model_ex_bdeu = bnlearn.structure_learning(df, methodtype='ex', scoretype='bdeu')
```

## Example: Parameter Learning
```python
model = bnlearn.load_example('sprinkler')
model_update = bnlearn.parameter_learning(model)
G = bnlearn.plot(model)
```

## Example: Inference
```python
model = bnlearn.load_example('sprinkler')
q_1 = bnlearn.inference(model, variables=['Rain'], evidence={'Cloudy':1,'Sprinkler':0, 'Wet_Grass':1})
q_2 = bnlearn.inference(model, variables=['Rain'], evidence={'Cloudy':1})
```

## Example: Sampling to create dataframe
```python
model = bnlearn.load_example('sprinkler')
df = bnlearn.sampling(model, n=1000)
```

* Output of the model:
```
[BNLEARN] Model correct: True
CPD of Cloudy:
+-----------+-----+
| Cloudy(0) | 0.5 |
+-----------+-----+
| Cloudy(1) | 0.5 |
+-----------+-----+
CPD of Sprinkler:
+--------------+-----------+-----------+
| Cloudy       | Cloudy(0) | Cloudy(1) |
+--------------+-----------+-----------+
| Sprinkler(0) | 0.5       | 0.9       |
+--------------+-----------+-----------+
| Sprinkler(1) | 0.5       | 0.1       |
+--------------+-----------+-----------+
CPD of Rain:
+---------+-----------+-----------+
| Cloudy  | Cloudy(0) | Cloudy(1) |
+---------+-----------+-----------+
| Rain(0) | 0.8       | 0.2       |
+---------+-----------+-----------+
| Rain(1) | 0.2       | 0.8       |
+---------+-----------+-----------+
CPD of Wet_Grass:
+--------------+--------------+--------------+--------------+--------------+
| Sprinkler    | Sprinkler(0) | Sprinkler(0) | Sprinkler(1) | Sprinkler(1) |
+--------------+--------------+--------------+--------------+--------------+
| Rain         | Rain(0)      | Rain(1)      | Rain(0)      | Rain(1)      |
+--------------+--------------+--------------+--------------+--------------+
| Wet_Grass(0) | 1.0          | 0.1          | 0.1          | 0.01         |
+--------------+--------------+--------------+--------------+--------------+
| Wet_Grass(1) | 0.0          | 0.9          | 0.9          | 0.99         |
+--------------+--------------+--------------+--------------+--------------+
[BNLEARN] Nodes: ['Cloudy', 'Sprinkler', 'Rain', 'Wet_Grass']
[BNLEARN] Edges: [('Cloudy', 'Sprinkler'), ('Cloudy', 'Rain'), ('Sprinkler', 'Wet_Grass'), ('Rain', 'Wet_Grass')]
[BNLEARN] Independencies:
(Cloudy _|_ Wet_Grass | Rain, Sprinkler)
(Sprinkler _|_ Rain | Cloudy)
(Rain _|_ Sprinkler | Cloudy)
(Wet_Grass _|_ Cloudy | Rain, Sprinkler)
```

## Example: Loading DAG from bif files
```python
bif_file= 'sprinkler'
bif_file= 'alarm'
bif_file= 'andes'
bif_file= 'asia'
bif_file= 'pathfinder'
bif_file= 'sachs'
bif_file= 'miserables'
bif_file= 'filepath/to/model.bif'

# Loading example dataset
model = bnlearn.load_example(bif_file)
```

## Example: Comparing networks
```python
# Load asia DAG
model=bnlearn.load_example('asia')
# plot ground truth
G=bnlearn.plot(model)

# Sampling
df=bnlearn.sampling(model, n=10000)
# Structure learning of sampled dataset
model_sl = bnlearn.structure_learning(df, methodtype='hc', scoretype='bic')
# Plot based on structure learning of sampled data
bnlearn.plot(model_sl, pos=G['pos'])

# Compare networks and make plot
bnlearn.compare_networks(model['adjmat'], model_sl['adjmat'], pos=G['pos'])

```
#### Graph of ground truth
<p align="center">
  <img src="https://github.com/erdogant/bnlearn/blob/master/docs/figs/fig2a_asia_groundtruth.png" width="600" />
</p>

#### Graph based on Structure learning
<p align="center">
  <img src="https://github.com/erdogant/bnlearn/blob/master/docs/figs/fig2b_asia_structurelearning.png" width="600" />
</p>

#### Graph comparison ground truth vs. structure learning
<p align="center">
  <img src="https://github.com/erdogant/bnlearn/blob/master/docs/figs/fig2c_asia_comparion.png" width="600" />
  <img src="https://github.com/erdogant/bnlearn/blob/master/docs/figs/fig2d_confmatrix.png" width="400" />
</p>


## Citation
Please cite bnlearn in your publications if this is useful for your research. Here is an example BibTeX entry:
```BibTeX
@misc{erdogant2019bnlearn,
  title={bnlearn},
  author={Erdogan Taskesen},
  year={2019},
  howpublished={\url{https://github.com/erdogant/bnlearn}},
}
```

## References
* http://pgmpy.org
* https://programtalk.com/python-examples/pgmpy.factors.discrete.TabularCPD/
* http://www.bnlearn.com/
* http://www.bnlearn.com/bnrepository/
   
## Maintainers
* Erdogan Taskesen, github: [erdogant](https://github.com/erdogant)

## Contribute
* All kinds of contributions are welcome!

## © Copyright
See [LICENSE](LICENSE) for details.
