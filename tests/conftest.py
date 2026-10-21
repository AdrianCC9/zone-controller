from pathlib import Path

import pytest
import yaml

from zone_controller.control.sequence import Controller
from zone_controller.points import load_database

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def database():
    return load_database(ROOT / "config/points.yaml")


@pytest.fixture
def schedule():
    return yaml.safe_load((ROOT / "config/schedule.yaml").read_text())


@pytest.fixture
def controller(database, schedule):
    return Controller(database, schedule)
