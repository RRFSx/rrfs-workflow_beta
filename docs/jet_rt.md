# An example on deploying a new version of rrfs for Jet Realtime run 
### 1. Clone and build   
```
cd /lfs5/BMC/nrtrr/RRFS
git clone --recursive git@github.com:rrfs2/rrfs-workflow.git 1.0.1
cd 1.0.1/sorc
./build.all
````
### 2. Generate the experiment and the rocoto XML file
```
crontab -e # comment out the old version of the rrfs realtime run
cd 1.0.1/workflow
vi exp/exp.setup_jet_rt  # modify variables, such as VERSION, if needed
./setup_exp.py exp/exp.setup_jet_rt # answer y if asked whether to generate an XML
crontab -e # make sure the new version of the rrfs realtime run is active in the crontab
```

### 3. Go to the expdir to make sure everything works correctly
```
cd /home/role.rtrr/RRFS/1.0.1/conus12km
./run_rocoto.sh
rstat
```
Sometimes, manually rocoto_reboot a cycle may be beneficial. For example, a new version is deployed at 03z. 03z will need lbc from 00z. So one can run the following command to reboot the lbc task at 00z so that 03z cycle can start soon. 
```
rboot 202407190000 lbc
```
