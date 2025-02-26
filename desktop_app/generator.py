import os
import time
import random
import subprocess
import threading
import webview
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from functions import dat_to_csv

# Configuration
UPLOAD_FOLDER = r"C:\temp\besa_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BESA_EXE = r"C:\Program Files (x86)\BESA\Simulator\BesaSimulator.exe"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        mod_file = request.files.get("file")
        output_dir = request.form.get("output_dir", "").strip()
        num_outputs_str = request.form.get("num_outputs", "0").strip()

        # Validate inputs
        if not mod_file or not output_dir or not num_outputs_str:
            return "Missing form inputs!", 400
        try:
            num_outputs = int(num_outputs_str)
            if num_outputs <= 0:
                return "Number of datasets must be a positive integer!", 400
        except ValueError:
            return "Invalid number of datasets!", 400

        if not os.path.exists(BESA_EXE):
            return f"BESA executable not found: {BESA_EXE}", 500

        # Save the uploaded .mod file
        mod_filename = secure_filename(mod_file.filename)
        mod_path = os.path.join(UPLOAD_FOLDER, mod_filename)
        mod_file.save(mod_path)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate .simbat script
        simbat_script = [
            "Logging off",
            "Settings width=700",  # Set epoch width to 700ms
        ]
        for i in range(1, num_outputs + 1):
            noise_level = round(random.uniform(0.1, 0.5), 2)
            simbat_script.extend([
                f"For var=i start={i} end={i} step=1",
                "  ModelClear noquery",
                f"  ModelLoad \"{mod_path.replace('\\\\', '/')}\"",
                f"  Settings currentrawfolder=\"{os.path.abspath(output_dir).replace('\\\\', '/')}\"",
                f"  RawData target=\"temp_{i}.dat\"",
                f"  RawData RMSnoise={noise_level}",
                "  RawData alpha=0.5",
                "  RawData ntrigs=10 trigID=11",
                "  RawData interval=1 intervalvar=0",
                "  RawData go",
                "EndFor"
            ])

        # Write the .simbat file
        simbat_file = os.path.join(UPLOAD_FOLDER, "combined_loop.simbat")
        with open(simbat_file, "w") as f:
            f.write("\n".join(simbat_script))

        # Run BESA Simulator with error tolerance
        try:
            process = subprocess.run(
                [BESA_EXE, simbat_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=60  # Give it up to 60 seconds to complete
            )
            print("BESA Output:", process.stdout)
            if process.stderr:
                print("BESA Errors (continuing anyway):", process.stderr)
        except subprocess.TimeoutExpired:
            print("BESA took too long; forcefully terminated.")
            process.kill()
        except Exception as e:
            print(f"Error launching BESA (continuing anyway): {e}")

        # Process generated files
        generated_files = []
        for i in range(1, num_outputs + 1):
            dat_file = os.path.join(output_dir, f"temp_{i}.dat")
            generic_file = os.path.join(output_dir, f"temp_{i}.generic")
            csv_file = os.path.join(output_dir, f"EEG_{i}.csv")

            # Wait for .dat file to appear (up to 30 seconds)
            attempts = 0
            while not os.path.exists(dat_file) and attempts < 30:
                time.sleep(1)
                attempts += 1

            if not os.path.exists(dat_file):
                print(f"Warning: {dat_file} not created. Skipping dataset {i}.")
                continue

            # Convert to CSV
            try:
                dat_to_csv(dat_file, generic_file, csv_file)
                generated_files.append(csv_file)
            except Exception as e:
                print(f"Error converting {dat_file} to CSV: {e}")
                continue

            # Cleanup temporary files
            for ext in [".dat", ".generic", ".evt", ".elp", ".bsa"]:
                leftover = os.path.join(output_dir, f"temp_{i}{ext}")
                if os.path.exists(leftover):
                    try:
                        os.remove(leftover)
                    except Exception as e:
                        print(f"Failed to remove {leftover}: {e}")

        # Cleanup .simbat file
        if os.path.exists(simbat_file):
            os.remove(simbat_file)

        return render_template("results.html", output_dir=output_dir, generated_files=generated_files)

    return render_template("index.html")

def start_server():
    app.run(port=5000, debug=False)

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    webview.create_window("BESA Synthetic EEG Generator", "http://127.0.0.1:5000")
    webview.start()
