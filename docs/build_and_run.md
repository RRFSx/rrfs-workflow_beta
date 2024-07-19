# Build
`git clone --recursive git@github.com:guoqing-NOAA/rrfs-workflow.git`

`cd sorc` and run the following command to build the system. This will take a very long time at the moment:    
`build.all`

or you may open 3 terminals, with each terminal running one of the following commands:  

```
./build.wps  | tee ./log.build.wps
./build.mpas | tee ./log.build.mpas
./build.rdas | tee ./log.build.rdas

```

# run
under the rrfs-workflow top directory, make sure python3 is available in your current enviroment

```
cd workflow
vi exp/exp_setup
  # modfiy exp_setup for your situation (especially the first 3 variables)
./setup_exp.py exp/exp_setup
  # answer 'n' when asked and go to ${expdir} to double check config files, edit config.jet (or hera, etc) to set up slurm information
./setup_xml.py ${expdir}
```
Go to ${expdir}, use `./run_rocoto.sh` to run the experiment

### note
The workflow depends on the environmental variables. If your environment defines and exports rrfs-workflow-specific environmental variables in an unexpected way or your environment is corrupt, the setup step may fail or generate unexpected results. Check the `rrfs.xml` file before `run_rocoto.sh`. Starting from a fresh terminal or `module purge` usually solves the problem.
