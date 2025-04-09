from argparse import ArgumentParser
import os

### FUNCTIONS PART ###
def change_sh_file(file):
   content_dict = {3:  'RUN=$1',
              4:  'BRICKID=$2',
              9:  'SNDBUILD_DIR='+SNDSW_ROOT,
              12: 'source '+FEDRA_SETUP,
              15: 'cd '+reco_data_path}
   for line, content in content_dict.items():
      modify_line_in_file(file, line, content)
def change_sub_file(file, shfile, tag):
   content_dict = {1:  'executable = '+shfile,
              2:  'arguments = $(RUN) $(BRICKID) $(PLATENUMBER)',
              3:  'output = '+CONDOR_WORK_DIR+'/logs/output/'+tag+'.$(ClusterId).$(PLATENUMBER).out',
              4:  'error = '+CONDOR_WORK_DIR+'/logs/error/'+tag+'.$(ClusterId).$(PLATENUMBER).err',
              5:  'log = '+CONDOR_WORK_DIR+'/logs/log/'+tag+'.$(ClusterId).log'}
   for line, content in content_dict.items():
      modify_line_in_file(file, line, content)
def modify_line_in_file(file_path, line_number, new_content):
    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Check if the line_number is valid
        if line_number < 1 or line_number > len(lines):
          lines.append('\n')
						#print("Invalid line number")
          	#return

        # Modify the content of the specified line
        lines[line_number - 1] = new_content + '\n'

        # Open the file in write mode to overwrite it with the modified content
        with open(file_path, 'w') as file:
            file.writelines(lines)

        #print(f"Line {line_number} modified successfully.")
    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
########################


parser = ArgumentParser()
parser.add_argument("-p", nargs='+', dest="plates", help="plates files", required=False)
parser.add_argument("--mic", dest="microscope", help="microscope", type=int, required=False)
parser.add_argument("--lab", dest="labname", help="labName (NA, BO, CE)", type=str, required=True)
parser.add_argument("--run", dest="run", help="Emulsion run", type=str, required=True)
parser.add_argument("--brickID", dest="brickID", help="brickID", type=int, required=True)
parser.add_argument("-r", nargs='+', dest="rplates", help="plates rescan", required=False)
parser.add_argument("--mos", dest="mos", required=False, default=False, action='store_true')
parser.add_argument("--createlink", dest="createl", required=False, default=False, action='store_true')
parser.add_argument("--vsa", dest="vsa", required=False, default=False, action='store_true')
parser.add_argument("--beam", dest="beam", required=False, default=False, action='store_true')
parser.add_argument("--moslink", dest="moslink", required=False, default=False, action='store_true')
args = parser.parse_args()

#####  SET PERSONAL PATHS HERE #############
CONDOR_WORK_DIR = '/afs/cern.ch/work/d/dannc/public/emu_reconstruction/'
RECO_DATA_PREPATH = '/eos/experiment/sndlhc/users/dancc/emureco/Napoli/'
SNDSW_ROOT = '/afs/cern.ch/user/d/dannc/sw'
FEDRA_SETUP='/afs/cern.ch/user/d/dannc/setup_fedrarelease.sh'
RECO_REPOSITORY= CONDOR_WORK_DIR
##########################


labDict = {'NA': 'Napoli', 'BO': 'Bologna', 'CE': 'CERN'}
brID = args.brickID
wall = int(brID/10)
brick = brID%10
brickfolder = str(brID).zfill(6)
if args.mos:
  brickfolder = str(brID+100).zfill(6)

rawdata_prepath = '/eos/experiment/sndlhc/emulsionData/2022/'
raw_data_path_dict = {'NA': labDict[args.labname]+'/SND/mic'+str(args.microscope)+'/RUN'+args.run+'_W'+str(wall)+'_B'+str(brick)+'/', 'BO': labDict[args.labname]+'/'+args.run+'_W'+str(wall)+'_B'+str(brick)+'/', 'CE':labDict[args.labname]+'/SND_mic'+str(args.microscope)+'/RUN'+args.run+'/'+'RUN'+args.run+'_W'+str(wall)+'_B'+str(brick)+'/'}
reco_data_path = RECO_DATA_PREPATH+'RUN'+args.run+'/b'+str(brickfolder)+'/'

def setMyCondorScripts():
  """
  python emureco_utils.py --vsa --brick 33 --run 2
  """
  if args.vsa:
    print('Set up condor script for VSA')
    condor_shfile = CONDOR_WORK_DIR+'/mosaic/condor_vsa.sh'
    condor_subfile = CONDOR_WORK_DIR+'/mosaic/condor_vsa.sub'
    change_sh_file(condor_shfile)
    change_sub_file(condor_subfile, condor_shfile, 'vsa')
  elif args.beam:
    print('Set up condor script for Beam')
    condor_shfile = CONDOR_WORK_DIR+'/beam/condor_ab0.sh'
    condor_subfile = CONDOR_WORK_DIR+'/beam/condor_ab0.sub'
    change_sh_file(condor_shfile)
    change_sub_file(condor_subfile, condor_shfile, 'ab0')
  elif args.moslink:
    print('Set up condor script for Linking')
    condor_shfile = CONDOR_WORK_DIR+'/linking/condor_mln.sh'
    condor_subfile = CONDOR_WORK_DIR+'/linking/condor_mln.sub'
    change_sh_file(condor_shfile)
    change_sub_file(condor_subfile, condor_shfile, 'mln')
  else:
    raise Exception('No available condor tag found!')


def create_link():
  """
  Usage: python emureco_utils.py --createlink -p firstplate lastplate -r rescan plates --mic micname --lab labname --run runnumber --brickID bricknumber
  """
  if len(args.plates) > 2:
    raise Exception('Too many plate number given, 2 are needed')

  rawplatedict = {}
  platedict = {}

  for plate in range(int(args.plates[1]), int(args.plates[0])+1):
    rawplatedict[plate] = 'P'+str(plate).zfill(2)
    platedict[plate] = 'p'+str(plate).zfill(3)

  for rplate in args.rplates:
    if args.labname == 'CE':
      rawplatedict[rplate] = 'P'+str(rplate).zfill(2)+'_rescan'
    else:
      rawplatedict[int(rplate)] = 'P'+str(rplate).zfill(2)+'_RESCAN'


  for plate in platedict.keys():
    os.system('mkdir -p '+reco_data_path+platedict[plate])
    os.system('ln -s '+rawdata_prepath+raw_data_path_dict[args.labname]+'/'+rawplatedict[plate]+'/tracks.raw.root '+reco_data_path+'/'+platedict[plate]+'/'+str(brID)+'.'+str(plate)+'.0.0.raw.root')
    print('created link ', platedict[plate],'to folder', raw_data_path_dict[args.labname]+'/'+rawplatedict[plate])
  
  os.system('cp /eos/experiment/sndlhc/users/dancc/emureco/emureco_scripts/*.sh ', reco_data_path)
  os.system('cp /eos/experiment/sndlhc/users/dancc/emureco/emureco_scripts/*.rootrc ', reco_data_path)


if args.createl: create_link()
if args.vsa or args.beam or args.moslink: setMyCondorScripts()



