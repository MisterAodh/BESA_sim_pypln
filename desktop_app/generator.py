import os
import time
import random
import subprocess
import threading
import numpy as np
import webview
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from functions import dat_to_csv  # your helper function

app = Flask(__name__)

UPLOAD_FOLDER = r"C:\Users\PHELANLE\PycharmProjects\Data_Generator\uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BESA_EXE = r"C:\Program Files (x86)\BESA\Simulator\BesaSimulator.exe"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        output_dir = request.form.get("output_dir", "")
        num_outputs_str = request.form.get("num_outputs", "0")

        try:
            num_outputs = int(num_outputs_str)
        except ValueError:
            return "Number of outputs must be an integer!", 400

        if not file or not output_dir or num_outputs <= 0:
            return "Invalid input (missing file/output_dir or non-positive num_outputs)!", 400

        # Save the uploaded .mod file
        filename = secure_filename(file.filename)
        mod_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(mod_path)

        # Ensure BESA EXE exists
        if not os.path.exists(BESA_EXE):
            return f"BESA exe not found at: {BESA_EXE}", 500

        # Make output folder
        os.makedirs(output_dir, exist_ok=True)

        # Build a single .simbat with repeated blocks
        loop_block = []
        for i in range(1, num_outputs + 1):
            noise_level = round(random.uniform(0.1, 0.5), 2)
            loop_block.append(f"""
For var=i start={i} end={i} step=1
  ModelClear noquery
  ModelLoad "{mod_path.replace('\\', '/')}"
  Settings currentrawfolder="{os.path.abspath(output_dir).replace('\\', '/')}"
  RawData target="temp_{i}.dat"
  RawData RMSnoise={noise_level}
  RawData alpha=0.5
  RawData ntrigs=10 trigID=11
  RawData interval=1 intervalvar=0
  RawData go
EndFor
""")

        simbat_script = f"""
Logging off
Settings width=700
{''.join(loop_block)}
"""
        simbat_file = os.path.join(UPLOAD_FOLDER, "combined_loop.simbat")
        with open(simbat_file, "w") as sf:
            sf.write(simbat_script.strip())

        # Run BESA Simulator without failing on error
        cmd = [BESA_EXE, simbat_file]
        print("Running BESA with command:", cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # We won't wait on returncode, we just let BESA run.

        # Instead, let's wait a bit, then proceed to check for .dat files
        time.sleep(5)  # small buffer for BESA to start writing files

        generated_files = []
        for i in range(1, num_outputs + 1):
            dat_file = os.path.join(output_dir, f"temp_{i}.dat")
            gen_file = os.path.join(output_dir, f"temp_{i}.generic")
            csv_file = os.path.join(output_dir, f"EEG_{i}.csv")

            # Wait up to ~30 seconds for each .dat to appear
            attempts = 0
            while not os.path.exists(dat_file) and attempts < 30:
                time.sleep(1)
                attempts += 1

            # If still not found, we skip or show a warning
            if not os.path.exists(dat_file):
                print(f"Warning: {dat_file} not created. We'll skip iteration {i}")
                continue

            # Convert to CSV
            try:
                dat_to_csv(dat_file, gen_file, csv_file)
                generated_files.append(csv_file)
            except Exception as e:
                print(f"Failed to convert {dat_file}: {e}")

            # Clean leftover
            for ext in [".dat", ".generic", ".evt", ".elp", ".bsa"]:
                leftover = os.path.join(output_dir, f"temp_{i}{ext}")
                if os.path.exists(leftover):
                    os.remove(leftover)

        # Remove simbat & the .mod, or keep the .mod if you want to reuse it
        if os.path.exists(simbat_file):
            os.remove(simbat_file)
        # If you want to remove the .mod too:
        # if os.path.exists(mod_path):
        #     os.remove(mod_path)

        return render_template("results.html", output_dir=output_dir, generated_files=generated_files)
    else:
        return render_template("index.html")


@app.route("/results")
def results():
    return render_template("results.html")


def start_server():
    app.run(port=5000)


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    webview.create_window("BESA Synthetic EEG Generator", "http://127.0.0.1:5000")
    webview.start()
