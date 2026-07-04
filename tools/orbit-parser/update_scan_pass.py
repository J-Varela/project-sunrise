import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MISSION_DATA_FILE = PROJECT_ROOT / "apps" / "dashboard" / "data" / "mission-data.json"


def load_mission_data() -> dict:
    with MISSION_DATA_FILE.open("r") as file:
        return json.load(file)


def save_mission_data(mission_data: dict) -> None:
    with MISSION_DATA_FILE.open("w") as file:
        json.dump(mission_data, file, indent=2)


def update_coverage(target: dict) -> dict:
    coverage = target["coverage"]

    if coverage["mapped_percent"] >= 100:
        coverage["mapped_percent"] = 100
        coverage["status"] = "Complete"
        return target

    coverage["passes_completed"] += 1

    percent_per_pass = 100 / coverage["passes_required"]
    new_percent = round(coverage["passes_completed"] * percent_per_pass)

    coverage["mapped_percent"] = min(new_percent, 100)

    if coverage["mapped_percent"] >= 100:
        coverage["status"] = "Complete"
    elif coverage["mapped_percent"] >= 50:
        coverage["status"] = "Mid Scan"
    else:
        coverage["status"] = "In Progress"

    return target


def update_mission_status(mission_data: dict) -> dict:
    targets = mission_data["target_regions"]

    completed_targets = [
        target
        for target in targets
        if target["coverage"]["mapped_percent"] >= 100
    ]

    if len(completed_targets) == len(targets):
        mission_data["spacecraft"]["status"] = "Mapping Complete"
    else:
        mission_data["spacecraft"]["status"] = "Simulating"

    return mission_data


def main() -> None:
    mission_data = load_mission_data()

    mission_data["target_regions"] = [
        update_coverage(target) for target in mission_data["target_regions"]
    ]

    mission_data = update_mission_status(mission_data)
    save_mission_data(mission_data)

    print("Completed one simulated scan pass.")
    print(f"Updated: {MISSION_DATA_FILE}")

    for target in mission_data["target_regions"]:
        coverage = target["coverage"]
        print(
            f"{target['name']}: "
            f"{coverage['mapped_percent']}% mapped "
            f"({coverage['passes_completed']}/{coverage['passes_required']} passes)"
        )


if __name__ == "__main__":
    main()