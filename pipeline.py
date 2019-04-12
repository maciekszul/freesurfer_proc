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
json_file = str(params["f"][0])
subj_index = params["n"]

print(json_file)
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
    try:
        t1_file = files.get_files(
            t1_subj_dir,
            "co",
            "nii.gz"
        )[2][0]
        print(raw_subj, op.exists(t1_file), "T1 image exists")
    except:
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

def recon_all_func(fs_path, raw_subj):
    try:
        t1_file = files.get_files(
            t1_subj_dir,
            "co",
            "nii.gz"
        )[2][0]

        sp.call([
            "recon-all",
            "-i", t1_file,
            "-subjid", raw_subj,
            "-sd", fs_path,
            "-all"
        ])
    except:
        print(raw_subj, "No T1 file for this participant")
    

fs_subj_dir = op.join(
    fs_path,
    raw_subj
)

if pipeline_params["recon_all"] and not op.exists(fs_subj_dir):
    recon_all_func(fs_path, raw_subj)

def bem_watershed_func(fs_path, raw_subj):
    sp.call([
        "mne",
        "watershed_bem",
        "-s", raw_subj,
        "-d", fs_path
    ])

if pipeline_params["bem_watershed"] and op.exists(fs_subj_dir):
    bem_watershed_func(fs_path, raw_subj)

def make_scalp_surface_func(fs_path, raw_subj):
    sp.call([
        "mne",
        "make_scalp_surfaces",
        "-s", raw_subj,
        "-d", fs_path,
        "-f", True
    ])

if pipeline_params["make_scalp_surface"] and op.exists(fs_subj_dir):
    make_scalp_surface_func(fs_path, raw_subj)
