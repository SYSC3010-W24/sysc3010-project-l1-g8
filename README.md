# 🔥 FANS (Fire Alarm Notification System)

<!--- TODO: include project image --->

FANS is a comprehensive multi-system solution for fire-related emergencies that require prompt notification of persons
in the affected area.

FANS utilizes smoke and temperature sensors to accurately detect fires in its surrounding environment. Upon detection,
FANS issues SMS and email notifications to individuals in the surrounding area.

FANS provides a dashboard for live monitoring of its environment, as well as an interface for customizing things like
its sensitivity to pressure changes.

## Contributors

SYSC3010 group L1-G8, under guidance of TA Sean Kirkby.

- Grant Achuzia
- Javeria Sohail
- Matteo Golin
- Saja Fawagreh

## Repository Organization

FANS is composed of several different nodes. Within the project repository, each node is given its own directory
containing its required files.

- The data collection system is stored in [`sensor-pi/`][sensor-pi]
- The notification system is stored in [`notifier/`][notifier]
- The web GUI is stored in [`web-app/`][gui]
- The alarm system is stored in [`alarm-system/`][alarm]
- The haptic alarm system is stored in [`pico_alarm/`][haptic]

In addition, the `docs/` directory contains documentation on our system design. Within `docs/`, the `assets/` folder
contains all of the UML class, sequence, state machine and deployment diagrams which describe the FANS system and which
are used throughout our reports. The `design-report/` folder contains all of the LaTeX source files that compose the
FANS design report, and the `proposal/` folder contains the LaTeX source files for building our initial project proposal.

## Further Reading

To read more about FANS, its implementation and design, you can visit its [GitHub Wiki][wiki].

[wiki]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/wiki
[alarm]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/alarm-system
[sensor-pi]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/sensor-pi
[gui]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/web-app
[haptic]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/pico_alarm
[notifier]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/notifier
