import math

def cartesian_to_besa_spherical(x, y, z):
    """
    Convert Cartesian (x,y,z) -> BESA-like spherical angles (theta, phi).
    BESA typically wants:
      theta in -180..+180  (like atan2(y, x))
      phi   in  -90..+90   (like arcsin(z/r))
    """
    r = math.sqrt(x*x + y*y + z*z)
    if r < 1e-12:
        return 0.0, 0.0  # can't define angles

    # Theta = atan2(y,x) in degrees
    theta_deg = math.degrees(math.atan2(y, x))

    # Phi = arcsin(z/r) in degrees
    phi_deg = math.degrees(math.asin(z / r))

    return theta_deg, phi_deg

def parse_line(line):
    """
    Attempt to parse lines in the format:
       index label x y z
    e.g. "1  F3  0.6730  0.5450  0.5000"
    Return (label, x, y, z) or None if unparseable.
    """
    # Skip lines containing '='
    if '=' in line:
        return None

    parts = line.strip().split()
    if len(parts) != 5:
        return None

    # e.g. "1", "F3", "0.6730", "0.5450", "0.5000"
    try:
        _idx = int(parts[0])  # we don't actually need to store it
        label = parts[1]
        x = float(parts[2])
        y = float(parts[3])
        z = float(parts[4])
        return (label, x, y, z)
    except (ValueError, IndexError):
        return None

def main():
    input_file = "extracted_12chan.elp"
    output_file = "converted.elp"

    n_parsed = 0
    with open(input_file, "r", encoding="utf-8") as fin, \
         open(output_file, "w", encoding="utf-8") as fout:

        for line in fin:
            line = line.strip()
            if not line:
                continue

            parsed = parse_line(line)
            if not parsed:
                print(f"Warning: Could not parse => {line}")
                continue

            label, x, y, z = parsed
            theta, phi = cartesian_to_besa_spherical(x, y, z)
            fout.write(f"EEG {label} {theta:.4f} {phi:.4f} 1\n")
            n_parsed += 1

    if n_parsed == 0:
        print("No lines were successfully parsed. Output is empty!")
    else:
        print(f"Done. Parsed {n_parsed} lines -> {output_file}")

if __name__ == "__main__":
    main()
