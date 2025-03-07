# import os
# import subprocess
# import time
# from functions import create_simbat_for_mod, dat_to_csv
#
# def main():
#     BESA_EXE = r"C:\Program Files (x86)\BESA\Simulator\BesaSimulator.exe"
#
#     # 1) .mod file path
#     mod_file = os.path.join(os.path.dirname(__file__), "P1_NormalVision.mod")
#     if not os.path.exists(mod_file):
#         print("Cannot find", mod_file)
#         return
#
#     # 2) Output folder
#     output_dir = os.path.join(os.path.dirname(__file__), "output")
#     os.makedirs(output_dir, exist_ok=True)
#
#     # 3) Generate .simbat
#     simbat_path = create_simbat_for_mod(
#         mod_file=mod_file,
#         output_dir=output_dir,
#         simbat_filename="generated.simbat"
#     )
#     print("Created simbat file:", simbat_path)
#
#     # 4) Run BESA
#     try:
#         proc = subprocess.run(
#             [BESA_EXE, simbat_path],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=60
#         )
#         print("BESA stdout:\n", proc.stdout)
#         if proc.stderr:
#             print("BESA stderr:\n", proc.stderr)
#     except Exception as e:
#         print("Error running BESA:", e)
#         return
#
#     # 5) Check for .dat / .generic in output
#     dat_file     = os.path.join("EEG_Output.dat")
#     generic_file = os.path.join("EEG_Output.generic")
#     csv_file     = os.path.join("EEG_Output.csv")
#
#     if os.path.exists(dat_file) and os.path.exists(generic_file):
#         dat_to_csv(dat_file, generic_file, csv_file)
#         print("Wrote CSV:", csv_file)
#     else:
#         print("Could not find EEG_Output.dat/.generic. Check BESA logs above.")
#
# if __name__ == "__main__":
#     main()
#
# # import os
# # import time
# # import subprocess
# # import numpy as np
# #
# # def create_simbat_for_mod(
# #     mod_file: str,
# #     output_dir: str,
# #     simbat_filename: str = "generated.simbat",
# #     sensor_file: str = None
# # ) -> str:
# #     """
# #     Creates a single .simbat batch script that:
# #       1) (Optionally) Loads a custom sensor file (.elp).
# #       2) Sets basic BESA simulator parameters (samples, interval, baseline).
# #       3) Loads the specified .mod file.
# #       4) Saves the output in Generic format as 'EEG_Output.dat'/'EEG_Output.generic'.
# #
# #     Returns the path to the generated .simbat file.
# #     """
# #
# #     # Example parameters: 250 samples, 2 ms sampling interval, 50 baseline samples
# #     n_samples = 250
# #     interval_ms = 2.0
# #     baseline_samples = 50
# #
# #     lines = []
# #     lines.append("Logging off")
# #     lines.append("HeadModel default")  # default spherical model
# #
# #     # If user provided a custom sensor file (e.g. 12-channel .elp)
# #     if sensor_file and os.path.exists(sensor_file):
# #         # Instruct BESA to load the sensor definitions from that .elp
# #         lines.append(f'SensorsLoad "{sensor_file.replace("\\", "/")}"')
# #     else:
# #         lines.append("; No custom sensor file loaded - using default EEG sensors.")
# #
# #     lines.extend([
# #         f"Settings samples={n_samples}",
# #         f"Settings interval={interval_ms}",
# #         f"Settings baselinesamples={baseline_samples}",
# #         "ModelClear noquery",
# #         f'ModelLoad "{os.path.abspath(mod_file).replace("\\", "/")}"',
# #         f'Settings currentrawfolder="{os.path.abspath(output_dir).replace("\\", "/")}"',
# #         'DataSave "EEG_Output" gen'  # Save to EEG_Output.dat + EEG_Output.generic
# #     ])
# #
# #     simbat_path = os.path.join(output_dir, simbat_filename)
# #     with open(simbat_path, "w", encoding="utf-8") as f:
# #         f.write("\n".join(lines))
# #
# #     return simbat_path
# #
# #
# # def dat_to_csv(dat_file: str, generic_file: str, csv_file: str):
# #     """
# #     Reads BESA .dat + .generic => single CSV with columns:
# #         Time, Chan1, Chan2, ...
# #     """
# #     if not os.path.exists(dat_file):
# #         raise FileNotFoundError(f"Missing .dat file: {dat_file}")
# #     if not os.path.exists(generic_file):
# #         raise FileNotFoundError(f"Missing .generic file: {generic_file}")
# #
# #     # 1) Parse .generic to get nChannels, nSamples, sRate
# #     header_info = {}
# #     with open(generic_file, "r") as gf:
# #         for line in gf:
# #             line = line.strip()
# #             if "=" in line:
# #                 key, val = line.split("=", 1)
# #                 header_info[key.strip()] = val.strip()
# #
# #     n_channels = int(header_info.get("nChannels", 0))
# #     n_samples  = int(header_info.get("nSamples", 0))
# #     s_rate     = float(header_info.get("sRate", 500.0))  # default 500 Hz if missing
# #
# #     # 2) Load float32 data from .dat
# #     raw_data = np.fromfile(dat_file, dtype=np.float32)
# #     expected_size = n_channels * n_samples
# #     if raw_data.size != expected_size:
# #         raise ValueError(
# #             f"Size mismatch reading {dat_file}: "
# #             f"expected {expected_size} floats, got {raw_data.size}."
# #         )
# #
# #     # Reshape => (channels, samples)
# #     raw_data = raw_data.reshape((n_channels, n_samples))
# #
# #     # 3) Create a time axis in seconds
# #     time_axis = np.arange(n_samples) / s_rate
# #
# #     # 4) Write CSV
# #     with open(csv_file, "w", encoding="utf-8") as out_f:
# #         # Header row
# #         headers = ["Time"] + [f"Chan{i+1}" for i in range(n_channels)]
# #         out_f.write(",".join(headers) + "\n")
# #
# #         # Data rows
# #         for idx in range(n_samples):
# #             row_vals = [f"{time_axis[idx]:.5f}"] + [
# #                 f"{val:.5f}" for val in raw_data[:, idx]
# #             ]
# #             out_f.write(",".join(row_vals) + "\n")
# #
# #
# # def main():
# #     # 1) Path to BESA Simulator:
# #     BESA_EXE = r"C:\Program Files (x86)\BESA\Simulator\BesaSimulator.exe"
# #
# #     # 2) Paths to .mod file and optional .elp sensor file
# #     script_dir = os.path.dirname(__file__)  # folder containing this script
# #     mod_file = os.path.join(script_dir, "P1_NormalVision.mod")
# #     sensor_file = os.path.join(script_dir, "extracted_12chan.elp")
# #
# #     # 3) Create an output folder for .dat/.generic and final CSV
# #     output_dir = os.path.join(script_dir, "output")
# #     os.makedirs(output_dir, exist_ok=True)
# #
# #     # 4) Generate the .simbat
# #     simbat_path = create_simbat_for_mod(
# #         mod_file=mod_file,
# #         output_dir=output_dir,
# #         simbat_filename="generated.simbat",
# #         sensor_file=sensor_file  # or None if you don't have a custom .elp
# #     )
# #     print("Created simbat file:", simbat_path)
# #
# #     # 5) Run BESA Simulator with that .simbat
# #     try:
# #         proc = subprocess.run(
# #             [BESA_EXE, simbat_path],
# #             stdout=subprocess.PIPE,
# #             stderr=subprocess.PIPE,
# #             text=True,
# #             timeout=60
# #         )
# #         print("BESA Simulator stdout:\n", proc.stdout)
# #         if proc.stderr:
# #             print("BESA Simulator stderr:\n", proc.stderr)
# #     except subprocess.TimeoutExpired:
# #         print("Error: BESA Simulator timed out after 60s.")
# #         return
# #     except Exception as e:
# #         print("Error launching BESA Simulator:", e)
# #         return
# #
# #     # 6) The script instructs BESA to create "EEG_Output.dat" + "EEG_Output.generic" in output_dir
# #     dat_file = os.path.join(output_dir, "EEG_Output.dat")
# #     generic_file = os.path.join(output_dir, "EEG_Output.generic")
# #     csv_file = os.path.join(output_dir, "EEG_Output.csv")
# #
# #     # Wait up to 10 seconds for them to appear
# #     max_wait_seconds = 10
# #     start_time = time.time()
# #     while time.time() - start_time < max_wait_seconds:
# #         if os.path.exists(dat_file) and os.path.exists(generic_file):
# #             break
# #         time.sleep(0.5)
# #
# #     if not (os.path.exists(dat_file) and os.path.exists(generic_file)):
# #         print("Error: .dat/.generic not found after waiting. Check BESA logs above.")
# #         return
# #
# #     # 7) Convert to CSV
# #     try:
# #         dat_to_csv(dat_file, generic_file, csv_file)
# #         print("Successfully wrote CSV:", csv_file)
# #     except Exception as e:
# #         print("Error converting .dat/.generic to CSV:", e)
# #
# #
# # if __name__ == "__main__":
# #     main()
import os
import subprocess
import time
from functions import create_simbat_for_mod, dat_to_csv

def main():
    # 1) Path to BESA
    BESA_EXE = r"C:\Program Files (x86)\BESA\Simulator\BesaSimulator.exe"

    # 2) The .mod file in the same folder as this script
    mod_file = os.path.join(os.path.dirname(__file__), "EEG_Output.mod")
    if not os.path.exists(mod_file):
        print("Error: Can't find EEG_Output.mod next to script.")
        return

    # 3) The custom .elp with 12 channels (must exist in the working dir)
    sensor_file = os.path.join(os.path.dirname(__file__), "converted.elp")
    if not os.path.exists(sensor_file):
        print("Warning: 'extracted_12chan.elp' not found. Using default sensors.")
        sensor_file = None

    # 4) Generate the .simbat in the same working dir
    simbat_path = create_simbat_for_mod(
        mod_file=mod_file,
        simbat_filename="generated.simbat",
        sensor_file=sensor_file
    )
    print("Created .simbat:", simbat_path)

    # 5) Run BESA
    try:
        result = subprocess.run(
            [BESA_EXE, simbat_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60
        )
        print("BESA stdout:\n", result.stdout)
        if result.stderr:
            print("BESA stderr:\n", result.stderr)
    except Exception as e:
        print("Error running BESA:", e)
        return

    # 6) The final .dat/.generic appear in working dir => "EEG_Output.dat" / "EEG_Output.generic"
    dat_file = "EEG_Output.dat"
    generic_file = "EEG_Output.generic"
    csv_file = "EEG_Output.csv"

    # Wait a bit in case BESA is slow
    max_wait = 5
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if os.path.exists(dat_file) and os.path.exists(generic_file):
            break
        time.sleep(0.2)

    if not (os.path.exists(dat_file) and os.path.exists(generic_file)):
        print("No EEG_Output.dat/.generic found in working dir after waiting.")
        return

    # 7) Convert to CSV
    dat_to_csv(dat_file, generic_file, csv_file)
    print(f"Done! Wrote CSV with {csv_file}")

if __name__ == "__main__":
    main()
