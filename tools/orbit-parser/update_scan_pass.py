import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MISSION_DATA_FILE = PROJECT_ROOT / "apps" / "dashboard" / "data" / "mission-data.json"


def load_mission_data() -> dict:
    with MISSION_DATA_FILE.open("r") as file:
        return json.load(file)


def save_mission_data(mission_data: dict) -> None:
    with MISSION_DATA_FILE.open("w") as file:
        json.dump(mission_data, file, indent=2)


def create_event(event_type: str, message: str, target_name: str | None = None) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "target_name": target_name,
        "message": message,
    }


def update_coverage(target: dict) -> tuple[dict, list[dict]]:
    events = []
    coverage = target["coverage"]
    target_name = target["name"]

    previous_percent = coverage["mapped_percent"]

    if coverage["mapped_percent"] >= 100:
        coverage["mapped_percent"] = 100
        coverage["status"] = "Complete"

        events.append(
            create_event(
                "coverage_complete",
                f"{target_name} is already fully mapped.",
                target_name,
            )
        )

        return target, events

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

    events.append(
        create_event(
            "scan_pass",
            (
                f"Scan pass completed over {target_name}. "
                f"Coverage increased from {previous_percent}% "
                f"to {coverage['mapped_percent']}%."
            ),
            target_name,
        )
    )

    return target, events


def update_mission_status(mission_data: dict) -> tuple[dict, list[dict]]:
    events = []
    targets = mission_data["target_regions"]

    previous_status = mission_data["spacecraft"]["status"]

    completed_targets = [
        target
        for target in targets
        if target["coverage"]["mapped_percent"] >= 100
    ]

    if len(completed_targets) == len(targets):
        mission_data["spacecraft"]["status"] = "Mapping Complete"
    else:
        mission_data["spacecraft"]["status"] = "Simulating"

    new_status = mission_data["spacecraft"]["status"]

    if new_status != previous_status:
        events.append(
            create_event(
                "mission_status",
                f"Mission status changed from {previous_status} to {new_status}.",
            )
        )

    return mission_data, events


def main() -> None:
    mission_data = load_mission_data()

    mission_data.setdefault("event_log", [])

    updated_targets = []
    new_events = []

    for target in mission_data["target_regions"]:
        updated_target, target_events = update_coverage(target)
        updated_targets.append(updated_target)
        new_events.extend(target_events)

    mission_data["target_regions"] = updated_targets

    mission_data, status_events = update_mission_status(mission_data)
    new_events.extend(status_events)

    mission_data["event_log"] = new_events + mission_data["event_log"]
    mission_data["event_log"] = mission_data["event_log"][:20]

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

    print(f"Logged {len(new_events)} new mission events.")


if __name__ == "__main__":
    main()