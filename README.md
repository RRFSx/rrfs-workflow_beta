# Build
`git clone --recursive git@github.com:NOAA-GSL/rrfs2.git`

`cd sorc` and run the following command to build the system. This will take a very long time at the moment:    
`build.all`

or you may open 3 terminals, with each terminal running one of the following commands:  

```
./build.wps  | tee ./log.build.wps
./build.mpas | tee ./log.build.mpas
./build.rdas | tee ./log.build.rdas

```

# run
under the rrfs2 top directory, make sure python3 is available in your current enviroment

```
cd workflow
cp config/exp_setup .
vi exp_setup  # modfiy exp_setup for your situation (especially the first 3 variables)
./setup_exp.py exp_setup
vi config/config.jet # or config.hera if on hera. set up your slurm account/queue/partition/reservation, etc
./setup_xml.py ${expdir}
```
Go to the ${expdir}, use `./run_rocoto.sh` to run the experiment

### tips
1. The workflow depends on the environmental variables. If your environment defines and exports rrfs2-workflow environmental variables in an unexpected way or your environment is corrupt, the setup step may fail or generate unexpected results. Check the `rrfs.xml` file before `run_rocoto.sh`. Starting from a fresh terminal will solve the problem.
2. You may export variables as follows to skip step 5 in section 2 (i.e. vi config/config.jet):
```
export RESERVATION="rrfsens"
export ACCOUNT="rtwrfruc"
export QUEUE="rth"
```
