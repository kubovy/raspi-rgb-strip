# Raspberry Pi Zero RGB Led Strip

## MQTT API

The general convention of the topics follows the following format: `[service_name]/[state|control]/[module]/#`

Every state change SHOULD be accompanied by a `[service_name]/state/#` message published to the broker.

### General

* `[service_name]/state/status`

  is triggered when the system gets online/offline. This topic is also publish with the payload `OFF` as the systems's 
  _last will_.

  | Payload  | Description      |
  | -------- | ---------------- |
  | `ON`     | System is online  |
  | `OFF`    | System is offline |

### RGB Strip

* `[service_name]/state/rgb`

  is triggered when the RGB strip light configuration changes. The payload contains the settings in the format: 
  `[R],[G],[B]`, e.g., `255,0,0` for full red color

* `[service_name]/control/rgb`

  sets the color on the strip. Payload should be in the format: `[R],[G],[B]`, e.g., `255,0,0` for full red color

* `[service_name]/control/rgb/[pattern]`

  sets a color with a pattern. The following patterns are supported:

  * `fade-in` will fade in from black to defined color. The payload is in the following format: `[R],[G],[B],[step],[interval]` where:

    |              |                                              |
    | ------------ | -------------------------------------------- |
    | `[R]`        | Red color from `0` to `255`                  |
    | `[G]`        | Green color from `0` to `255`                |
    | `[B]`        | Blue color from `0` to `255`                 |
    | `[step]`     | Fading step in percent between `1` and `100`, if not set `5`% is used as default.  |
    | `[interval]` | Interval in ms to wait between fading steps, if not set `50`ms is used as default. |

  * `fade-out` will fade in from the defined color to black. The payload is in the following format: `[R],[G],[B],[step],[interval]` where:

    |              |                                              |
    | ------------ | -------------------------------------------- |
    | `[R]`        | Red color from `0` to `255`                  |
    | `[G]`        | Green color from `0` to `255`                |
    | `[B]`        | Blue color from `0` to `255`                 |
    | `[step]`     | Fading step in percent between `1` and `100`, if not set `5`% is used as default.  |
    | `[interval]` | Interval in ms to wait between fading steps, if not set `50`ms is used as default. |

