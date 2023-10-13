import os
import sys
from argparse import ArgumentParser

def modify_line_in_file(file_path, line_number, new_content):
    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Check if the line_number is valid
        if line_number < 1 or line_number > len(lines):
            print("Invalid line number")
            return

        # Modify the content of the specified line
        lines[line_number - 1] = new_content + '\n'

        # Open the file in write mode to overwrite it with the modified content
        with open(file_path, 'w') as file:
            file.writelines(lines)

        print(f"Line {line_number} modified successfully.")
    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

parser = ArgumentParser()
parser.add_argument("-run", dest="run", required=True)
options = parser.parse_args()

redo_print = False

datarunprint_comm = 'source /afs/cern.ch/work/d/dannc/public/MuonBackground/muonDis_sim/datarunPrinter.sh '+str(options.run).zfill(6)+' 2023'
if not os.path.exists('/afs/cern.ch/work/d/dannc/public/MuonBackground/muonDis_sim/DATARUNPRINTS/printrun_'+str(options.run).zfill(6)+'.dat'):
    os.system(datarunprint_comm)
else:
    print('Datarun print for run',options.run, 'exists, skipping')

dagman_file = '/afs/cern.ch/work/d/dannc/public/MuonBackground/muonDis_sim/condor_DISfilter/DISfilter_dagman.dag'
#dagman_file = '/afs/cern.ch/work/d/dannc/public/MuonBackground/muonDis_sim/condor_DISfilter/DISfilter_dagman_skip1.dag'
line_numbers =[i for i in range(6, 10)]
letters = [chr(letter) for letter in range(ord('A'), ord('D')+1)]
#line_numbers =[i for i in range(5, 8)]
#letters = [chr(letter) for letter in range(ord('C'), ord('E')+1)]

for line_number, letter  in zip(line_numbers, letters):
  content = 'VARS '+letter+' RUN="'+str(options.run)+'"'
  modify_line_in_file(dagman_file, line_number, content)

dagman_dirname= '/afs/cern.ch/work/d/dannc/public/MuonBackground/muonDis_sim/condor_DISfilter/run_'+str(options.run).zfill(5)+'_dagfiles'
if not os.path.exists(dagman_dirname):
    os.system('mkdir '+dagman_dirname)
os.system('cd '+dagman_dirname)
os.system('cp '+dagman_file+' '+dagman_dirname)
os.system('rm '+dagman_dirname+'/DISfilter_dagman.dag.*')
condor_comm = 'condor_submit_dag -outfile_dir '+dagman_dirname+' '+dagman_dirname+'/DISfilter_dagman.dag'
os.system(condor_comm)
