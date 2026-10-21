# Planned points list

Generated from config/points.yaml; all physical points UNCOMMISSIONED.

| Name | Description | Units | Planned BACnet object | Source | Tags |
|---|---|---|---|---|---|
| ZN-T | Zone space temperature | degreesCelsius | analogInput:1 | i2c_sht4x | point, sensor, temp, air, zone |
| ZN-RH | Zone relative humidity | percentRelativeHumidity | analogInput:2 | i2c_sht4x | point, sensor, humidity, air, zone |
| ZN-CO2 | Zone carbon dioxide | partsPerMillion | analogInput:3 | i2c_scd4x | point, sensor, co2, air, zone |
| SA-T | Supply air temperature | degreesCelsius | analogInput:4 | onewire | point, sensor, temp, air, discharge |
| RA-T | Return air temperature | degreesCelsius | analogInput:5 | onewire | point, sensor, temp, air, return |
| OCC-COUNT | Smoothed people count | noUnits | analogInput:6 | vision | point, sensor, occupancy, zone |
| RTU-T | Third-party transmitter temperature | degreesCelsius | analogInput:7 | modbus_rtu | point, sensor, temp, air |
| RTU-RH | Third-party transmitter humidity | percentRelativeHumidity | analogInput:8 | modbus_rtu | point, sensor, humidity, air |
| HTG-SP-OCC | Occupied heating setpoint | degreesCelsius | analogValue:1 | setpoint | point, sp, temp, zone |
| CLG-SP-OCC | Occupied cooling setpoint | degreesCelsius | analogValue:2 | setpoint | point, sp, temp, zone |
| HTG-SP-STBY | Standby heating setpoint | degreesCelsius | analogValue:3 | setpoint | point, sp, temp, zone |
| CLG-SP-STBY | Standby cooling setpoint | degreesCelsius | analogValue:4 | setpoint | point, sp, temp, zone |
| HTG-SP-UNOCC | Unoccupied heating setpoint | degreesCelsius | analogValue:5 | setpoint | point, sp, temp, zone |
| CLG-SP-UNOCC | Unoccupied cooling setpoint | degreesCelsius | analogValue:6 | setpoint | point, sp, temp, zone |
| FAN-CMD | Booster fan command | noUnits | binaryOutput:1 | gpio_relay | point, cmd, fan, zone |
| FAN-STS | Independent fan feedback | noUnits | binaryInput:1 | gpio_input | point, sensor, run, fan, zone |
| DMP-CMD | Proposed ventilation damper command | percent | analogValue:7 | virtual | point, cmd, damper, zone |
| SYS-MODE | Zone operating mode | noUnits | multiStateValue:1 | derived | point, mode, zone |
| FAN-RUNTIME | Fan runtime hours | hours | analogValue:8 | derived | point, his, run, fan |
| ALM-COUNT | Active alarm count | noUnits | analogValue:9 | derived | point, alarm, zone |
