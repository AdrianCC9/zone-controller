# Proposed network riser

Design only. No IP addresses assigned, bus framing verified, or devices commissioned.

```mermaid
flowchart TD
    PC[Windows engineering laptop / future YABE] --- LAN[Home LAN]
    LAN --- PI[zc-1 Raspberry Pi 4 / reserved IP pending]
    PI --- I2C[I²C zone sensor and proposed CO₂ sensor]
    PI --- W1[1-Wire supply and return probes]
    PI --- USB[USB RS-485 adapter]
    USB --- RTU[XY-MD02 / configuration unverified]
    PI --- IO[Isolated relay and independent fan feedback]
```

Record IP/subnet/gateway, adapter identity, bus topology, grounding and termination
after the physical survey. Do not expose building protocols directly to the internet.
