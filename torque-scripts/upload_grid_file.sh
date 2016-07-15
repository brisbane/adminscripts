#!/bin/bash
fname=$1
if ! [[ $fname ]]; then
   fname=testgfn
fi
#All moved to myGridEnv
#. /usr/libexec/grid-env.sh
#export LCG_GFAL_VO=vo.southgrid.ac.uk
#export LFC_HOST=`lcg-infosites  --vo ${LCG_GFAL_VO}  lfc`
#export X509_USER_PROXY=/home/brisbane/.gridProxy
#export LFC_HOME=lfn://grid/vo.southgrid.ac.uk/sean
. $HOME/myGridEnv
#lcg-ls lfn://grid/

if ! [[ $PBS_JOBID ]];then
  PBS_JOBID=tester
fi
lcg-cr ${fname} -l $LFC_HOME/${fname}_${PBS_JOBID}1 -d srm://t2se01.physics.ox.ac.uk/dpm/physics.ox.ac.uk/home/vo.southgrid.ac.uk/sean/${fname}_${PBS_JOBID}1



