# Sequence of operations — revision A, 2026-10-20

Design and simulation scope; field acceptance pending. This adapts patterns named in
the supplied build guide and does not claim ASHRAE Guideline 36 compliance.

1. Schedule uses America/Toronto local time. Weekdays are occupied 08:00–22:00;
   weekends 09:00–23:00. Start is inclusive; end exclusive. Warm-up starts 30 minutes
   before occupancy and uses occupied setpoints. It does not operate furnace calls.
2. Scheduled occupancy with a good count of zero for 20 minutes enters Standby.
   A positive count restores Occupied. Failed/stale vision falls back to schedule
   and reports an alarm. Out of schedule, occupancy does not extend occupied mode.
3. Heating/cooling pairs are 21.5/24.5 °C Occupied, 20/26 °C Standby, 17/28 °C
   Unoccupied. Values and timers come from points.yaml. A write or relinquishment
   that makes heating exceed cooling minus the 1 °C deadband is rejected atomically.
4. Fan demand starts beyond a 0.5 °C deviation outside the active setpoint pair.
   It ends on return to the pair. Minimum on is 600 seconds and off 300 seconds,
   including startup. Operator overrides also pass through these timers.
5. Internal priorities: sequence 16; operator 8; safety 1. Relinquish with null.
   Safety always stops fan and closes the modeled damper, bypassing minimum on.
   After recovery, the full off timer applies before any restart. The network
   BACnet priority array remains to be implemented and verified externally.
6. Every 120 seconds, temperature above cooling setpoint +0.5 requests +4% damper;
   otherwise trim -2%, clamped 0–100%. This is a single-zone demonstration.
7. CO₂ above 1000 ppm imposes at least 20% ventilation; above 1400 imposes 100%.
   Failed CO₂ falls back to 20% and alarms. Temperature safety overrides ventilation.
8. Supply above 50 °C or invalid zone/supply readings stop fan, close damper and
   alarm. Readings fault at age >=300 seconds, on driver fault, nonfinite values or
   future timestamp. Humidity and return temperature do not drive this initial loop.
9. Every mode transition records previous/new state and reason. Alarms currently
   report active conditions; acknowledgement, delay, latching and durable history
   are phase 7 work. Runtime currently accumulates in memory only.
10. Hardware deployment must first monitor for 1–2 weeks without actuation. A
    transfer fan cannot guarantee heating/cooling without suitable source air;
    validate thermal direction and interlocks before enabling physical outputs.
