# Open deficiencies — 2026-10-20

| ID | Deficiency | Acceptance evidence |
|---|---|---|
| D01 | Pi, buses, sensor IDs, network and wiring not surveyed | Recorded hardware inventory and as-built drawings |
| D02 | No physical drivers or outputs commissioned | Signed point-to-point checklist including fault tests |
| D03 | Modbus address/function/scaling not verified | Exact vendor manual, register map and known reference reads |
| D04 | BACnet/IP, Modbus TCP and MQTT adapters absent | External discovery/read/write and packet captures |
| D05 | Simulation uses an idealized transfer source | Measured RC parameters, thermal-direction interlock and field acceptance |
| D06 | No camera detector or smoothing service | In-memory detection, sustained-zero and failure tests |
| D07 | Historian, retention/downsampling, dashboards absent | 30 days raw retention, hourly archive and two verified views |
| D08 | Alarm lifecycle and five FDD rules absent | Delay/deadband/ack/history tests and routed alarms |
| D09 | No baseline, actual improvement or video | Monitoring baseline, measured comparison and demo link |
| D10 | No service installation or recovery validation | 30-day run and witnessed power interruption |
| D11 | Haystack-style tags only; model export absent | Validated site/equipment/point export |
| D12 | Command persistence, restart state and sensor quality mapping unimplemented | Conservative startup and power recovery tests |
| D13 | As-built documents are templates | Surveyed network/panel/wiring and real signatures |
| D14 | MS/TP transport feasibility unverified | Document supported stack and hardware before implementation |
