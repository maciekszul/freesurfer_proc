from tools import files
import os.path as op
import json
import argparse
import subprocess as sp

json_file = "pipeline_params.json"

# argparse input
des = "pipeline script"
parser = argparse.ArgumentParser(description=des)
parser.add_argument(
    "-f", 
    type=str, 
    nargs=1,
    default=json_file,
    help="JSON file with pipeline parameters"
)

parser.add_argument(
    "-n", 
    type=int, 
    help="id list index"
)

args = parser.parse_args()
params = vars(args)
json_file = params["f"]
subj_index = params["n"]

# read the pipeline params
with open(json_file) as pipeline_file:
    pipeline_params = json.load(pipeline_file)

raw_path = pipeline_params["RAW_PATH"]
t1_path = pipeline_params["T1_PATH"]
fs_path = pipeline_params["FS_PATH"]

raw_subjects = files.get_folders_files(
    raw_path,
    wp=False
)[0]
raw_subjects.sort()

raw_subj = raw_subjects[subj_index]

raw_subj_dir = op.join(
    raw_path,
    raw_subj,
    "scans",
    "2_t1_mprage_sag_iso_1mm"
)

t1_subj_dir = op.join(
    t1_path,
    raw_subj
)

files.make_folder(t1_subj_dir)

def dcm2nii_func(t1_subj_dir, raw_subj_dir):
    dcm2nii = "/cubric/software/mricron/dcm2nii"

    sp.call([
        dcm2nii,
        "-4", "y", 
        "-a", "n", 
        "-c", "n", 
        "-d", "n", 
        "-e", "n", 
        "-f", "n", 
        "-g", "y", 
        "-i", "n", 
        "-o", t1_subj_dir, 
        "-p", "n", 
        "-r", "y", 
        "-v", "y", 
        "-x", "y", 
        raw_subj_dir
    ])

if pipeline_params["t1_conversion"]:
    dcm2nii_func(t1_subj_dir, raw_subj_dir)

t1_file = files.get_files(
    t1_subj_dir,
    "co",
    "nii.gz"
)[2][0]

def recon_all_func(t1_file, fs_path, raw_subj):
    sp.call([
        "recon-all",
        "-i", t1_file,
        "-subjid", raw_subj,
        "-sd", fs_path,
        "-all"
    ])

fs_subj_dir = op.join(
    fs_path,
    raw_subj
)

if not op.exists(fs_subj_dir) and pipeline_params["recon_all"]:
    recon_all_func(t1_file, fs_path, raw_subj)