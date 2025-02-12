import os
import subprocess
from functions import convert_dat_to_csv

# Path to the BESA Simulator executable
path_to_besa_exe = r"C:\Program Files (x86)\BESA\Simulator\BesaSimulator.exe"

# Path to your BESA .simbat batch script
path_to_batch_file = r"C:\Users\PHELANLE\PycharmProjects\edit_and_run_batch\ex_batch.simbat"

###############################################################################
# 1) Validate Existence of BESA Simulator and Batch Script
###############################################################################
if not os.path.exists(path_to_besa_exe):
    raise FileNotFoundError(f"BESA exe not found: {path_to_besa_exe}")
if not os.path.exists(path_to_batch_file):
    raise FileNotFoundError(f".simbat file not found: {path_to_batch_file}")

###############################################################################
# 2) Run BESA Simulator with the Given Batch Script
###############################################################################
# We capture_stdout/stderr to see if there's any error from BESA itself.
result = subprocess.run(
    [path_to_besa_exe, path_to_batch_file],
    capture_output=True,
    text=True
)

print("==== BESA Simulator Output ====")
print(result.stdout)
print("==== BESA Simulator Errors ====")
print(result.stderr)

###############################################################################
# 3) Check the Return Code
###############################################################################
if result.returncode != 0:
    # BESA returned an error code (non-zero)
    print(f"ERROR: BESA returned exit code {result.returncode}.")
    print("Check the stderr output above. Possibly close BESA or fix any script errors.")
else:
    print("BESA exited successfully (exit code 0).")

###############################################################################
# 4) Confirm That EEG_DATA.dat Was Created; Convert if Present
###############################################################################
dat_file = "EEG_DATA.dat"
if os.path.exists(dat_file) and os.path.getsize(dat_file) > 0:
    # We assume the file is valid if it's non-empty
    print(f"Found {dat_file}; converting to CSV...")
    convert_dat_to_csv(
        dat_file=dat_file,
        csv_output="cleaned_data.csv",
        num_channels=33,
        num_samples=3020
    )
else:
    print(f"WARNING: {dat_file} not found or is empty. No CSV generated.")
