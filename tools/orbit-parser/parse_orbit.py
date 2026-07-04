import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "tools" / "orbit-parser" / "sample_gmat_output.csv"
OUTPUT_FILE = PROJECT_ROOT / "apps" / "dashboard" / "data" / "mission-data.json"


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


def build_mission_data(orbit_points: list[dict]) -> dict:
    return {
        "mission_name": "Project Sunrise",
        "mission_version": "0.2.0",
        "central_body": "Moon",
        "spacecraft": {
            "name": "Sunrise Mapper 1",
            "type": "Lunar mapping orbiter",
            "status": "Simulating",
        },
        "objective": (
            "Map permanently shadowed lunar crater regions before robotic "
            "surface explorers enter them."
        ),
        "target_regions": [
            {
                "name": "Shackleton Crater",
                "region": "Lunar South Pole",
                "priority": "High",
                "risk": "Extreme cold, darkness, rough terrain",
            },
            {
                "name": "Cabeus Crater",
                "region": "Lunar South Pole",
                "priority": "Medium",
                "risk": "Possible ice deposits, communication difficulty",
            },
        ],
        "orbit_points": orbit_points,
    }


def write_mission_json(mission_data: dict, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w") as file:
        json.dump(mission_data, file, indent=2)


def main() -> None:
    orbit_points = parse_orbit_csv(INPUT_FILE)
    mission_data = build_mission_data(orbit_points)
    write_mission_json(mission_data, OUTPUT_FILE)

    print(f"Converted {len(orbit_points)} orbit points")
    print(f"Wrote mission data to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()