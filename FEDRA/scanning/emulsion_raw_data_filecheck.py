import os
import ROOT
import fedrarootlogon
import re

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-m", "--mic", dest="mic", help="Microscope name", type=int, required=True)
parser.add_argument("-r", "--run", dest="run", help="emulsion run", type=int, required=True)
parser.add_argument("-b", "--brick", dest="brickID", help="emulsion brickID", type=int, required=True)

args = parser.parse_args()

brID = args.brickID
wall = int(brID/10)
brick = brID%10

tag = '_mic'+str(args.mic)
if args.mic == 1: tag  = ''

rawdata_prepath = '/eos/experiment/sndlhc/emulsionData/'
rawdata_path =  f"{rawdata_prepath}/CERN/SND{tag}/RUN{args.run}/RUN{args.run}_W{wall}_B{brick}/"

import os
import re


expected_folders = {f"P{num:03d}" for num in range(1, 58)}


pattern = re.compile(r"^P\d{3}(_rescan\d+)?$")


existing_folders = {f for f in os.listdir(rawdata_path) if os.path.isdir(os.path.join(rawdata_path, f)) or pattern.match(f)}


missing_folders = sorted(expected_folders - existing_folders)


missing_files = []
found_files = []

for folder in sorted(existing_folders):
    file_path = os.path.join(rawdata_path, folder, "tracks.raw.root")
    if os.path.exists(file_path):
        found_files.append(file_path)
    else:
        missing_files.append(folder)


print(f"\n📂 Total expected folders: {len(expected_folders)}")
print(f"📂 Found folders: {len(existing_folders)}")
print(f"📂 Missing folders: {len(missing_folders)}\n")

if missing_folders:
    print("❌ Missing folders:")
    for f in missing_folders:
        print(f"   ✘ {f}")

print(f"\n✅ File found in {len(found_files)} folders")
for f in found_files:
    print(f"   ✔ {f}")
    #pass

if missing_files:
    print(f"\n⚠️ Missing file in {len(missing_files)} folders:")
    for f in missing_files:
        print(f"   ✘ {f}")
else:
    print("\n✅ All files are present in existing folders.")

existing_main_folders = sorted(set(expected_folders) - set(missing_folders))
print(f"\n")
for folder in existing_main_folders:
    rescan_pattern = re.compile(rf"^{folder}_rescan\d*$")
    frescans = [f for f in os.listdir(rawdata_path) if rescan_pattern.match(f)]
    if not frescans: continue
    latest_file = None
    latest_mtime = 0
    for rescan in frescans:
        rescan_path = os.path.join(rawdata_path, rescan)
        file_path = os.path.join(rescan_path, "tracks.raw.root")
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if file_mtime > latest_mtime:
                latest_mtime = file_mtime
                latest_file = rescan
    if latest_file:
        original_filepath = os.path.join(rawdata_path, folder)
        original_file = os.path.join(original_filepath, "tracks.raw.root")
        print(f"   Latest file for {folder}: {latest_file}")
        if os.path.isfile(original_file):
            originalfile_mtime = os.path.getmtime(original_file)
            if originalfile_mtime >= latest_mtime: print(f"⚠️ Latest modification time for {latest_file} is older or same of {folder}!")
    else:
        print(f"No file found for {folder}")
        




"""expected_dirs = {f"P{plate:03d}": None for plate in range(1, 58)}
found_files = {}

for root, dirs, files in os.walk(rawdata_path):
    folder_name = os.path.basename(root)
    if folder_name.startswith("P") or "_rescan" in folder_name:
        if file_name in files:
            file_path = os.path.join(root, file_name)
            found_files[folder_name] = file_path
        else:
            found_files[folder_name] = None  

for expected_folder in expected_dirs.keys():
    if expected_folder not in found_files or found_files[expected_folder] is None:
        #print(expected_folder, found_files)
        print(f"⚠️ WARNING: File {file_name} not found in the expected folder {expected_folder}")

# print(found_files)
for folder, file_path in found_files.items():
    rescan_files = []
    base_folder = folder.split("_")[0]

    if base_folder in expected_dirs and expected_dirs[base_folder] is None:
        expected_dirs[base_folder] = file_path

    if "_rescan" in folder and base_folder in expected_dirs and expected_dirs[base_folder] is not None:
        rescan_files.append((folder, file_path))

if rescan_files:
    original_mtime = os.path.getmtime(expected_dirs[base_folder])
    for rescan_folder, rescan_file in rescan_files:
        rescan_mtime = os.path.getmtime(rescan_file)
        if rescan_mtime > original_mtime:
            print(f"✅ INFO: {file_name} in {rescan_folder} is newer than its original version ({base_folder}).")
        else:
            print(f"⚠️ WARNING: {file_name} in {rescan_folder} is older or equal to its original version ({base_folder}).")
        break"""
