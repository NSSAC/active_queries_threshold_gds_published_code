# Code for "Using Active Queries to Infer Symmetric Node Functions of Graph Dynamical Systems," Adiga et al.
Contact: Abhijin Adiga (abhijin@virginia.edu, abhijin@gmail.com)

## Outline
All implementations are in Python 2.7 and 3.8. Part of the work was performed
on a HPC clusters using QSUB or SLURM workload manager. Code corresponding
to HPC commands can be easily replaced by regular shell commands. All files
are in the ``scripts/`` folder.

## Method 1 scripts
```
compaction.sh
compaction_interval_random_threshold.py
compaction_threshold_algorithm_greedy.py
```

## Method 2 scripts
```
threshold_algorithm_greedy.py
interval_random_threshold.py
```

## Networks and their properties
```
generate_networks.py
network_properties.py
```

## Experiment design and plotting results
```
master_experiments.sh
master_plot.sh
```
