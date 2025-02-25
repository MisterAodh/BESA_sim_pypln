import os
import numpy as np


def dat_to_csv(dat_file: str, generic_file: str, csv_file: str):
    """
    Reads the BESA-generated .dat and .generic files, then writes a CSV.
    Format:
      Time, Chan1, Chan2, ...
    """
    if not os.path.exists(dat_file) or not os.path.exists(generic_file):
        raise FileNotFoundError(f"Missing .dat or .generic file for:\n"
                                f"  dat_file={dat_file}\n"
                                f"  generic_file={generic_file}")

    # Parse the .generic header to get nChannels, nSamples, sRate
    header_info = {}
    with open(generic_file, "r") as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                header_info[key.strip()] = val.strip()

    n_channels = int(header_info.get("nChannels", 0))
    n_samples = int(header_info.get("nSamples", 0))
    s_rate = float(header_info.get("sRate", 500.0))

    # Read floats from the .dat file
    raw_data = np.fromfile(dat_file, dtype=np.float32)
    if raw_data.size != n_channels * n_samples:
        raise ValueError("Size mismatch reading .dat with provided .generic info. "
                         f"Expected {n_channels*n_samples} floats, got {raw_data.size}.")

    # Reshape (channels, samples)
    raw_data = raw_data.reshape((n_channels, n_samples))
    time_axis = np.arange(n_samples) / s_rate

    # Write CSV
    with open(csv_file, "w") as out_f:
        # Header row
        headers = ["Time"] + [f"Chan{i+1}" for i in range(n_channels)]
        out_f.write(",".join(headers) + "\n")

        # Data rows
        for sample_idx in range(n_samples):
            row_vals = [f"{time_axis[sample_idx]:.5f}"] + [
                f"{val:.5f}" for val in raw_data[:, sample_idx]
            ]
            out_f.write(",".join(row_vals) + "\n")
