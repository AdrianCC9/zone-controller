"""Local tools; default commands never operate relays or connect to a controller."""

import argparse
import json
from pathlib import Path

import yaml

from zone_controller.points import load_database
from zone_controller.simulation import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, default=Path("config"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("points")
    sim = sub.add_parser("simulate")
    sim.add_argument("--days", type=int, default=7)
    sim.add_argument("--output", type=Path, default=Path("runtime/week.json"))
    args = parser.parse_args()
    db = load_database(args.config_dir / "points.yaml")
    if args.command == "validate":
        print(f"Validated {len(db['points'])} points; hardware/protocols not commissioned.")
    elif args.command == "points":
        for name, p in db["points"].items():
            print(f"{name:16} {p['units']:26} {p['description']}")
    else:
        schedule = yaml.safe_load((args.config_dir / "schedule.yaml").read_text())
        result = run(db, schedule, args.days)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Synthetic {args.days}-day run saved to {args.output}")
        print(f"Fan runtime: {result['fan_runtime_h']} hours (simulation only)")


if __name__ == "__main__":
    main()
