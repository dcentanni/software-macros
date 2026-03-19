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
parser.add_argument("-lab", dest="labname", help="labName (NA, BO, CR, SAN)", type=str, required=False, default='NA')
parser.add_argument("-o", dest="destpath", help="output prepath", type=str, required=False, default='')
parser.add_argument("-r", dest="rescan_file", help="file containing \"plate rescan\" ", type=str, required=False, default=None)

args = parser.parse_args()

labDict = {'NA': 'Napoli', 'BO': 'Bologna', 'CR': 'CERN', 'SAN': 'Santiago'}
brickID = args.brickID%100
run = int(args.brickID/100)
wall = int(brickID/10)
brick = brickID%10

rawdata_prepath = '/eos/experiment/sndlhc/emulsionData/'
CR_mic_prepath = f'/SND_mic{int(args.mic)}/'
if int(args.mic)== 1: CR_mic_prepath = '/SND/'
raw_data_path_dict = {'NA':f'Napoli/SND/mic{args.mic}/RUN{run}_W{wall}_B{brick}/', 'CR':f'CERN/{CR_mic_prepath}/RUN{run}/RUN{run}_W{wall}_B{brick}' }


if not os.path.isdir(args.destpath):
    print(f'Destination pre-path does not exist, creating ..')
    os.makedirs(f'{args.destpath}')

print('Creating brick directory')
os.system(f'mkdir -p {args.destpath}/b{int(args.brickID):06d}/p{{001..057}}/')

rawdata_path = rawdata_prepath+raw_data_path_dict[args.labname]

found_files = []

if args.labname == 'CR':expected_folders = {f"P{num:03d}" for num in range(1, 58)}
else: expected_folders = {f"P{num:02d}" for num in range(1, 58)}

if args.labname == 'CR':
    pattern = re.compile(r"^P\d{3}(_rescan\d*)?$", re.IGNORECASE)
else:
    pattern = re.compile(r"^P\d{2}(_RESCAN\d*)?$", re.IGNORECASE)
    
existing_folders = {f for f in os.listdir(rawdata_path) if os.path.isdir(os.path.join(rawdata_path, f)) and pattern.match(f)}

for folder in sorted(existing_folders):
    file_path = os.path.join(rawdata_path, folder, "tracks.raw.root")
    if os.path.exists(file_path):
        found_files.append(file_path)
    
rescan_re = re.compile(r'^(P\d{2,3})(?:_rescan(\d*)?)?$', re.IGNORECASE)

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
        grouped_files[plate[-2:]]["main"] = path
    else:
        # rescan file
        rescan = int(rescan_num) if rescan_num != "" else 1
        grouped_files[plate[-2:]]["rescans"][rescan].append(path)

plate_files_dict = {}
for plate, data in grouped_files.items():
    print(f"Plate {plate}")
    if data["main"]:
        print("  Main:", data["main"])
        plate_files_dict[plate] = data["main"]
    else: print(f"  ⚠️  No data available for original scan of plate {plate}")

    for r, files in sorted(data["rescans"].items()):
        for f in files:
            print(f"  Rescan {r}: {f}")

plate_numbers = [int(k) for k in grouped_files.keys()]
pmin = min(plate_numbers)
pmax = max(plate_numbers)
print(f"\n✅ Found files for plates from P{pmin:02d} to P{pmax:02d}")


if args.rescan_file:
    rescan_file = args.rescan_file
    print(f'Reading rescan config file at {args.rescan_file}')
    if not os.path.exists(rescan_file): raise Exception(f"Rescan file {rescan_file} does not exist!")
    with open(rescan_file) as f:
        for line in f:
            vals = line.split()
            plate = int(vals[0])
            plate = f"{plate:02d}"
            plate_files_dict[plate] = grouped_files[plate]["rescans"][int(vals[1])][0]

#print(plate_files_dict)

print('Preparing brick ..')
print('Creating links ..')
for plate, path in plate_files_dict.items():
    os.system(f"ln -s -f {path} {args.destpath}/b{args.brickID:06d}/p{int(plate):03d}/{brickID}.{int(plate)}.0.0.0.cp.root")
os.chdir(args.destpath)
os.system(f'source /afs/cern.ch/work/f/falicant/public/emu_reconstruction/make_brick.sh {args.brickID}')
