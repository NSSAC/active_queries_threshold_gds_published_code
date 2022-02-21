#!/bin/bash

#SBATCH --time=48:00:00

##SBATCH --nodes=1 --ntasks-per-node=1
##SBATCH --exclusive
##SBATCH --mem=30464
##SBATCH --mem-per-cpu=1904

#SBATCH -p bii
#SBATCH -A biocomplexity

echo "$command"
eval "$command"

