import numpy as np
import pandas as pd

def convert_dat_to_csv(
    dat_file="EEG_DATA.dat",
    csv_output="cleaned_data.csv",
    num_channels=33,
    num_samples=3020
):
    """
    Loads a BESA .dat file (raw binary floats), reshapes it as [channels, samples],
    transposes to [time, channels], and saves as a CSV.

    - dat_file: Path to .dat file
    - csv_output: CSV filename to write
    - num_channels: Number of EEG channels in the file
    - num_samples: Number of time points per channel
    """
    # Example sensor labels in order (adjust if needed)
    sensor_names = [
        "Fp1", "Fp2", "F9", "F7", "F3", "Fz", "F4", "F8", "F10",
        "FC5", "FC1", "FC2", "FC6", "T9", "T7", "C3", "Cz", "C4",
        "T8", "T10", "CP5", "CP1", "CP2", "CP6", "P9", "P7", "P3",
        "Pz", "P4", "P8", "P10", "O1", "O2"
    ]

    data = np.fromfile(dat_file, dtype='<f4')  # 32-bit little-endian floats
    if data.size != (num_channels * num_samples):
        raise ValueError(
            f"Expected {num_channels*num_samples} floats, found {data.size}. "
            "Check your channel/sample counts or .dat file."
        )

    data = data.reshape((num_channels, num_samples), order='C')
    data_t = data.T  # shape -> (time x channels)

    # Create DataFrame, label columns, and round
    df = pd.DataFrame(data_t, columns=sensor_names)
    df = df.round(5)  # round to 5 decimal places

    df.to_csv(csv_output, index=False)
    print(f"Data from {dat_file} saved to {csv_output} with shape {df.shape}.")
