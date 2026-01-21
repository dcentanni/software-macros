import os
import sys
import re
from collections import defaultdict

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

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-b", "--brick", dest="brickID", help="Brick ID format RWB", type=int, required=True)
parser.add_argument("-m", "--mic", dest="mic", help="Microscope name", type=int, required=True)
parser.add_argument("--lab", dest="labname", help="labName (NA, BO, CR, SA)", type=str, required=True)
args = parser.parse_args()

labDict = {'NA': 'Napoli', 'BO': 'Bologna', 'CR': 'CERN', 'SA': 'Santiago'}
brickID = args.brickID%100
run = int(args.brickID/100)
wall = int(brickID/10)
brick = brickID%10

rawdata_prepath = '/eos/experiment/sndlhc/emulsionData/'
raw_data_path_dict = {'NA':f'{labDict[args.labname]}/SND/mic{args.mic}/RUN{run}_W{wall}_B{brick}/', 'CR':f'{labDict[args.labname]}/SND_mic{args.mic}/RUN{run}/RUN{run}_W{wall}_B{brick}/', 'BO':f'{labDict[args.labname]}/mic{args.mic}/RUN{run}_W{wall}_B{brick}/', 'SA':f'{labDict[args.labname]}/mic{args.mic}/RUN{run}/RUN{run}_W{wall}_B{brick}/'}

rawdata_path = rawdata_prepath+raw_data_path_dict[args.labname]
if args.mic == 1 and args.labname == 'CR':
  rawdata_path = rawdata_prepath+raw_data_path_dict[args.labname].replace('SND_mic1', 'SND')

found_files = []

expected_folders = {f"P{num:02d}" for num in range(1, 58)}
if args.labname == 'CR':
   expected_folders = {f"P{num:02d}" for num in range(1, 58)}

pattern = re.compile(r"^P\d{3}(_rescan\d+)?$")
existing_folders = {f for f in os.listdir(rawdata_path) if os.path.isdir(os.path.join(rawdata_path, f)) or pattern.match(f)}

for folder in sorted(existing_folders):
    file_path = os.path.join(rawdata_path, folder, "tracks.raw.root")
    if os.path.exists(file_path):
        found_files.append(file_path)

"""rescan_re = re.compile(r'^(P\d{2})(?:_rescan(\d*)?)?$')
if args.labname == 'CR':
    rescan_re = re.compile(r'^(P\d{3})(?:_rescan(\d*)?)?$')"""
rescan_re = re.compile(r'^(P\d+)(?:_rescan(\d*)?)?$')

grouped_files = defaultdict(lambda: {
    "main": None,
    "rescans": defaultdict(list)
})

for path in found_files:
    folder = os.path.basename(os.path.dirname(path))

    m = rescan_re.match(folder)
    if not m:
        continue

    plate, rescan_num = m.groups()

    if rescan_num is None:
        # main (non-rescan) file
        grouped_files[plate]["main"] = path
    else:
        # rescan file
        rescan = int(rescan_num) if rescan_num != "" else 1
        grouped_files[plate]["rescans"][rescan].append(path)


"""for plate, data in grouped_files.items():
    print(f"\nPlate {plate}")
    print("  Main:", data["main"])

    for r, files in sorted(data["rescans"].items()):
        for f in files:
            print(f"  Rescan {r}: {f}")"""

plate_numbers = [int(k[1:]) for k in grouped_files.keys()]
pmin = min(plate_numbers)
pmax = max(plate_numbers)
print(f"\n✅ Found files for plates from P{pmin:02d} to P{pmax:02d}\n, launching emthickness")
emthickness_file = f'launch_emthickness_{args.labname}.sh'
if args.labname == 'CR': emthickness_file = f'launch_emthickness.sh'
scriptdir = '/eos/home-s/snd2cern/emu_reco_plots/' 
os.system(f'cp {scriptdir}/{emthickness_file} {scriptdir}/temp_{args.labname}_{args.brickID}_{emthickness_file}')
emthickness_file = f'temp_{args.labname}_{args.brickID}_{emthickness_file}'
content_dict = {5:  f'MIC={args.mic}',
              6:  f'BRICK={brickID}',
              7:  f'RUN={run}'
              }
for line, content in content_dict.items():
    modify_line_in_file(f'{scriptdir}/{emthickness_file}', line, content)
os.system(f'source {scriptdir}/{emthickness_file} {pmax} {pmin} 0')

print('\n Launching emthickness for rescans\n')
for plate, data in grouped_files.items():
    for r, files in sorted(data["rescans"].items()):
        for f in files:
            os.system(f'source {scriptdir}/{emthickness_file} {int(plate[1:])} {int(plate[1:])} {r}')
print('\n✅ Emthickness processing completed, removing temporary files.\n')
os.system(f'rm {scriptdir}/{emthickness_file}')