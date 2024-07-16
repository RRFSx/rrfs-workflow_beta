# Build
`git clone --recursive git@github.com:NOAA-GSL/rrfs2.git`

Build from source codes and this will take a very long time:    
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
cp samples/exp/exp_setting exp_setting
  # you may replace the first `exp_setting` with `exp_jet_reservation` if you would like to use the jet reservations
  # modfiy exp_setting for your situation (especially the first 3 variables)
./setup_exp.py exp_setting
```
Go to the expdir, use `./run_rocoto.sh` to run the experiment
