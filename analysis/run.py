import os
import os,subprocess,ROOT,time,multiprocessing,socket

    
unit30_Nm  = 470661   
unit30_Pm  = 485965
muons_down = 182525

def muonDisProd(Ncycle = 1):
 nucleon = 'p+'
 if Ncycle>4: nucleon = 'n'
 for cycle in range(Ncycle,1+Ncycle):
  for run in range(1,11):
   dN = int(unit30_Nm/10.)
   S = dN*(run-1)
   os.system("python muonDis.py -f unit30_Nm.root -c make -n "+str(dN)+" -s "+str(S)+" -r "+str(run+cycle*100)+" -x 10 --nucleon "+nucleon+" &")
   while 1>0:
     if count_python_processes('muonDis')<ncpus: break
     time.sleep(10)
  for run in range(1,11):
   dN = int(unit30_Pm/10.)
   S = dN*(run-1)
   os.system("python muonDis.py -f unit30_Pm.root -c make -n "+str(dN)+" -s "+str(S)+" -r "+str(1000+run+cycle*100)+" -x 10 --nucleon "+nucleon+" &")
   while 1>0:
     if count_python_processes('muonDis')<ncpus: break
     time.sleep(10)
  print("end of cycle ",cycle)

def makeSpecificRun(cycle,run):
   dN = int(unit30_Nm/10.)
   S = dN*(run-1)
   os.system("python ../muonDis.py -f unit30_Nm.root -c make -n "+str(dN)+" -s "+str(S)+" -r "+str(run+cycle*100)+" -x 10 &")
   dN = int(unit30_Pm/10.)
   S = dN*(run-1)
   os.system("python ../muonDis.py -f unit30_Pm.root -c make -n "+str(dN)+" -s "+str(S)+" -r "+str(1000+run+cycle*100)+" -x 10 &")


           
def muonDisGeant4(cycle=0,ecut=0,strippedEvents=False,runStart=1,runEnd=11):
      """ 
      - cycle : 1 for mu -> p
                6 for mu -> n 
      - run :   1 - 10 using each muonDis_XX.root
      - job :   0 - 199 for parallel processing

      """
      cmd = "python  $SNDSW_ROOT/macro/run_simScript.py -F --MuDIS --shiplhc --firstEvent III --output OOO -n NNN -f FFF --eMin "+str(ecut) + " &"
      for run in range(runStart,runEnd):
        prod = str(run+cycle*100)
        if strippedEvents: fn = "/eos/experiment/sndlhc/MonteCarlo/Pythia6/MuonDIS/muonDis_"+prod+"_stripped.root"
        else:              fn = "/eos/experiment/sndlhc/MonteCarlo/Pythia6/MuonDIS/muonDis_"+prod+".root"
        tmp = ROOT.TFile(fn)
        N = tmp.DIS.GetEntries()
        #N = 5
        tmp.Close()
        NsubJobs = 200
        #NsubJobs = 5
        dN =  int(N/NsubJobs)
        for subjob in range(NsubJobs):    
          S = dN*subjob
          out = "/eos/user/d/dannc/emulsionactive/ecut"+str(ecut)+"/run_"+prod+"_"+str(subjob)
          if ecut >0: out = "/eos/user/d/dannc/emulsionactive/ecut"+str(ecut)+"/ecut"+str(ecut)+"_run_"+prod+"_"+str(subjob)
          command = cmd.replace('FFF',fn).replace('III',str(S)).replace('OOO',out).replace('NNN',str(dN))           
          os.system(command)

def HTCondor_muonDisGeant4(cycle=0,ecut=0,procID=0):
      """ 
      - cycle : 1 for mu -> p
                6 for mu -> n 
      - run :   1 - 10 using each muonDis_XX.root
      - job :   0 - 199 for parallel processing

      """
      run = int(procID/200) +1
      cmd = "/cvmfs/sndlhc.cern.ch/SNDLHC-2021/June/15/sw/slc7_x86-64/Python/v3.6.8-local1/bin/python3  $SNDSW_ROOT/shipLHC/run_simSND.py --MuDIS --firstEvent III --output OOO -n NNN -f FFF --eMin "+str(ecut)
      prod = str(run+cycle*100)
      fn = "/eos/experiment/sndlhc/MonteCarlo/Pythia6/MuonDIS/muonDis_"+prod+".root"
      tmp = ROOT.TFile(fn)
      N = tmp.DIS.GetEntries()
      tmp.Close()
      NsubJobs = 200
      subjob = int(procID%200)
      dN =  int(N/NsubJobs) 
      S = dN*subjob
      out = "/eos/user/d/dannc/emulsionactive/ecut"+str(ecut)+"/run_"+prod+"_"+str(subjob)
      if ecut >0: out = "/eos/user/d/dannc/emulsionactive/ecut"+str(ecut)+"/ecut"+str(ecut)+"_run_"+prod+"_"+str(subjob)
      command = cmd.replace('FFF',fn).replace('III',str(S)).replace('OOO',out).replace('NNN',str(dN))           
      os.system(command)


