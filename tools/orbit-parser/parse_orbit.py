import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "tools" / "orbit-parser" / "sample_gmat_output.csv"
OUTPUT_FILE = PROJECT_ROOT / "apps" / "dashboard" / "data" / "sample-orbit.json"


def parse_orbit_csv(input_file: Path) -> list[dict]:
    orbit_points = []

    with input_file.open("r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            orbit_points.append(
                {
                    "time": int(row["time"]),
                    "x": float(row["x"]),
                    "y": float(row["y"]),
                    "z": float(row["z"]),
                }
            )

    return orbit_points


def write_orbit_json(orbit_points: list[dict], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w") as file:
        json.dump(orbit_points, file, indent=2)


def main() -> None:
    orbit_points = parse_orbit_csv(INPUT_FILE)
    write_orbit_json(orbit_points, OUTPUT_FILE)

    print(f"Converted {len(orbit_points)} orbit points")
    print(f"Wrote dashboard data to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()