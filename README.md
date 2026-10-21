# Zone Controller

A single-zone home BAS edge controller for a Raspberry Pi 4. The project addresses
upstairs temperature imbalance with documented points, control sequences and
eventual low-voltage field integration. The original build guide is preserved in
[docs/build-guide-source.txt](docs/build-guide-source.txt).

**Status: software foundation and deterministic simulation. No hardware is connected
or commissioned. BACnet, Modbus, MQTT, camera detection and historian services are
not implemented yet.** No measured house results or completed resume claims exist.

## Run locally

Python 3.11 or later. Run from the repository root so configuration paths resolve.

```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\zone-controller validate
.venv\Scripts\zone-controller points
.venv\Scripts\zone-controller simulate --days 7 --output runtime/week.json
.venv\Scripts\python -m pytest -q
.venv\Scripts\ruff check .
```

On Linux use `python3 -m venv .venv` and `.venv/bin/` for the executables.
If Windows has no `py` launcher, use the absolute path to an installed Python.
Simulation writes only synthetic data beneath ignored `runtime/` and never
operates GPIO, furnace calls, network protocols or a camera.

## Architecture

`config/points.yaml` defines 20 planned points, object identifiers, engineering
units, drivers, tags, trends and setpoint defaults. It uses JSON syntax, which is
valid YAML, to make types explicit. `config/schedule.yaml` holds local schedules.
`src/zone_controller/` contains the point model, input-driver contract, explicit
mode sequence and RC simulation. Protocol and service packages are reserved for
later implementation. Internal priority arbitration is tested; it is not yet a
BACnet server. Read the [points list](docs/points-list.md) and
[sequence](docs/sequence-of-operations.md) before modifying code.

## First commissioning milestone

1. Prepare Pi OS Lite 64-bit, SSH keys, storage and a reserved IP; record actual values.
2. Enable I²C and 1-Wire, inventory exact sensor models and device IDs.
3. Implement and bench-test one SHT4x driver plus one DS18B20 input, including faults.
4. Verify independent fan feedback and the low-voltage relay output on the bench.
5. Record point-to-point measurements and initials; do not sign simulated results.
6. Begin 1–2 weeks of monitoring-only baseline before commissioning actuation.

Keep constructed controls at 24 V or below. Furnace W/Y/G sensing remains read-only
through suitable isolation; do not drive appliance calls. Electrical work and
equipment safety follow the scope in the source guide.

## Privacy and evidence

The planned camera service processes frames in memory, stores no images and
publishes only a smoothed count. That service is not yet implemented. Keep home IPs,
credentials, camera data, raw packet captures and local runtime data out of Git.
Use real commissioning records and measured baseline comparisons for portfolio
claims. [Deficiencies](docs/deficiency-list.md) track remaining work.

## Roadmap and acceptance

- [x] Repository foundation, 20-point database and generated points list
- [x] Written sequence, priority model and software simulation tests
- [ ] Pi deployment, 14+ live points and signed point-to-point commissioning
- [ ] Modbus RTU integration with vendor-verified register map and fault injection
- [ ] BACnet/IP discovery, read/write/relinquish from an external client
- [ ] Physical sequence acceptance and full simulated-week acceptance
- [ ] Camera occupancy service and schedule fallback validation
- [ ] MQTT, historian retention/downsampling and two Grafana views
- [ ] Five FDD rules, acknowledged alarm history and off-device routing
- [ ] Haystack model export and completed as-built package
- [ ] 30-day unattended run, power-cut recovery, measured improvement and demo

BACnet MS/TP is an unverified stretch goal requiring a separately validated stack
and adapter. Do not assume the BACpypes3 IP implementation provides MS/TP support.

