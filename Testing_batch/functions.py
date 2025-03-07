# import os
# import numpy as np
#
# def dat_to_csv(dat_file: str, generic_file: str, csv_file: str):
#     """
#     Convert BESA .dat + .generic to a single CSV file with columns:
#       Time, Chan1, Chan2, ...
#     """
#     if not os.path.exists(dat_file) or not os.path.exists(generic_file):
#         raise FileNotFoundError(f"Missing {dat_file} or {generic_file}")
#
#     # Parse .generic to find nChannels, nSamples, sRate
#     header_info = {}
#     with open(generic_file, "r") as f:
#         for line in f:
#             if "=" in line:
#                 key, val = line.strip().split("=", 1)
#                 header_info[key.strip()] = val.strip()
#
#     n_channels = int(header_info.get("nChannels", 0))
#     n_samples  = int(header_info.get("nSamples", 0))
#     s_rate     = float(header_info.get("sRate", 500.0))
#
#     # Read the float32 data
#     raw_data = np.fromfile(dat_file, dtype=np.float32)
#     if raw_data.size != (n_channels * n_samples):
#         raise ValueError("Mismatch reading .dat: expected "
#                          f"{n_channels*n_samples} floats, got {raw_data.size}.")
#
#     raw_data = raw_data.reshape((n_channels, n_samples))
#     time_axis = np.arange(n_samples) / s_rate
#
#     # Write CSV
#     with open(csv_file, "w") as out_f:
#         headers = ["Time"] + [f"Chan{i+1}" for i in range(n_channels)]
#         out_f.write(",".join(headers) + "\n")
#
#         for idx in range(n_samples):
#             row_vals = [f"{time_axis[idx]:.5f}"] + [
#                 f"{val:.5f}" for val in raw_data[:, idx]
#             ]
#             out_f.write(",".join(row_vals) + "\n")
#
#
# def create_simbat_for_mod(mod_file: str,
#                           output_dir: str,
#                           simbat_filename: str = "generated.simbat") -> str:
#     """
#     Write a .simbat file to load 'mod_file' into BESA,
#     produce a single epoch (samples/interval/baseline), and
#     save to 'EEG_Output.dat' + 'EEG_Output.generic' in 'output_dir'.
#     """
#
#     # Basic defaults:
#     npoints  = 250   # total samples
#     interval = 2.0   # ms
#     baseline = 50    # baseline samples
#
#     # If your .mod has "npoints" / "interval" in line 1, parse them:
#     with open(mod_file, "r", encoding="utf-8") as f:
#         first_line = f.readline().strip().split()
#     # e.g. "V4 start 100 npoints 333 interval 2"
#     for i, token in enumerate(first_line):
#         t_low = token.lower()
#         if t_low == "npoints" and i+1 < len(first_line):
#             npoints = int(first_line[i+1])
#         elif t_low == "interval" and i+1 < len(first_line):
#             interval = float(first_line[i+1])
#
#     # Build simbat commands
#     script_lines = [
#         "Logging off",
#         f"Settings samples={npoints}",
#         f"Settings interval={interval}",
#         f"Settings baselinesamples={baseline}",
#         "HeadModel default",
#         "Constraints x=-1 1 y=-1 1 z=0 1 ecc=0.1 0.9",
#         "ModelClear noquery",
#         f'ModelLoad "{os.path.abspath(mod_file).replace("\\", "/")}"',
#         f'Settings currentrawfolder="{os.path.abspath(output_dir).replace("\\", "/")}"',
#         # Actually produce .dat / .generic (DataSave "EEG_Output" gen):
#         'DataSave "EEG_Output" gen'
#     ]
#
#     # Write .simbat
#     simbat_path = os.path.join(output_dir, simbat_filename)
#     with open(simbat_path, "w", encoding="utf-8") as f:
#         f.write("\n".join(script_lines))
#     return simbat_path
import os
import numpy as np

def create_simbat_for_mod(mod_file: str,
                          simbat_filename: str = "generated.simbat",
                          sensor_file: str = None) -> str:
    """
    1) Load the custom .elp if provided
    2) Clear and load the .mod
    3) Save data as EEG_Output.dat/.generic in the working directory
    Returns the .simbat path.
    """

    # We'll fix the samples & interval for demonstration:
    n_samples = 250
    interval_ms = 2.0
    baseline_samples = 50

    lines = [
        "Logging off",
        # 1) Load the 12-channel ELP first, if provided
        (f'SensorsLoad "{sensor_file}"' if sensor_file else "; No custom sensor file loaded"),
        # 2) Basic simulator settings
        f"Settings samples={n_samples}",
        f"Settings interval={interval_ms}",
        f"Settings baselinesamples={baseline_samples}",
        "HeadModel default",
        "ModelClear noquery",
        f'ModelLoad "{os.path.abspath(mod_file).replace("\\", "/")}"',
        # 3) Write data as 'EEG_Output.dat'/'EEG_Output.generic' in working dir
        'DataSave "EEG_Output" gen'
    ]

    simbat_path = os.path.join(os.path.dirname(mod_file), simbat_filename)
    with open(simbat_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return simbat_path


def dat_to_csv(dat_file: str, generic_file: str, csv_file: str):
    """
    Convert the .dat + .generic into a single CSV.
    Looks in the working directory for .dat/.generic.
    """
    import numpy as np
    import os

    if not os.path.exists(dat_file) or not os.path.exists(generic_file):
        raise FileNotFoundError(f"Missing {dat_file} or {generic_file} in the working dir")

    # Parse .generic
    header_info = {}
    with open(generic_file, "r") as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                header_info[key.strip()] = val.strip()

    n_channels = int(header_info.get("nChannels", 0))
    n_samples = int(header_info.get("nSamples", 0))
    s_rate = float(header_info.get("sRate", 500.0))

    # Read float32 data
    raw_data = np.fromfile(dat_file, dtype=np.float32)
    if raw_data.size != (n_channels * n_samples):
        raise ValueError("Mismatch in .dat vs .generic size")

    raw_data = raw_data.reshape((n_channels, n_samples))
    time_axis = np.arange(n_samples) / s_rate

    # Write CSV
    with open(csv_file, "w") as out_f:
        headers = ["Time"] + [f"Chan{i+1}" for i in range(n_channels)]
        out_f.write(",".join(headers) + "\n")

        for idx in range(n_samples):
            row = [f"{time_axis[idx]:.5f}"] + [f"{val:.5f}" for val in raw_data[:, idx]]
            out_f.write(",".join(row) + "\n")
