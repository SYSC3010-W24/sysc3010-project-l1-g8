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

## Installation and Setup Guide

Guides to install and run each system node are provided below. Once all nodes have been set up, the system will be
functional.

### Sensor-Pi

In order to set up the `sensor-pi` sensor data collection system, you will need:

- Raspberry Pi 4
- Sense hat
- Breadboard
- Wires
- 2x 10k resistors
- 2x 1k resistors
- 2x NPN bipolar-junction transistors
- Flying fish MQ2 smoke detector module

In order to assemble the circuit, place the components on your breadboard according to the following schematic. Power
sources can come from the Raspberry Pi or an external source. The labelled pin outputs (GPIO 22, SCLK, MOSI, MISO) are
all meant to be connected to the corresponding pin on the Raspberry Pi 4. Please see its [pinout][pi-pinout] sheet to
locate this pins.

![](./docs/assets/schematics/MQ2-Schematic-Final.png)

Once the circuit is built and connected, the node can be started by running the software located in the `sensor-pi`
directory from the Raspberry Pi. Python 3.11 must be previously installed. The following commands will download the
repository and start the software when run in the terminal:

```console
git clone https://github.com/SYSC3010-W24/sysc3010-project-l1-g8.git
cd sysc-project-l1-g8/sensor-pi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### Alarm System

In order to set up the `alarm-system` node, you will need:

- Raspberry Pi 4
- Breadboard
- Wires
- Passive piezoelectric buzzer
- Red LED
- 1k resistor

In order to assemble the circuit, place the components on your breadboard according to the following schematic. The 3.3V
input signal should be connected to the Raspberry Pi's GPIO 22 pin. Please see the Pi's [pinout][pi-pinout] sheet to
connect the pins properly.

![](./docs/assets/schematics/Alarm-Schematic.png)

Once the circuit is assembled and connected, the node can be started by running the software located in the
`alarm-system` directory from the Raspberry Pi. Python 3.11 must be previously installed. The following commands will
download the repository and start the software when run in the terminal:

```console
git clone https://github.com/SYSC3010-W24/sysc3010-project-l1-g8.git
cd sysc-project-l1-g8/alarm-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### Notifier

In order to set up the `notifier` node, you will need:

- Raspberry Pi 4

The node can be started by running the software located in the notifier directory on the Raspberry Pi. Prior installation of Python 3.11 is required. Execute the following commands in the terminal to download the repository and start the software:

```console
git clone https://github.com/SYSC3010-W24/sysc3010-project-l1-g8.git
cd sysc-project-l1-g8/notifier
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 email_notification_system.py
```

Additionally, ensure that the following files are present in the same directory for it to function properly:

- fans_credentials.json: This file should contain the username and password required for authentication to the email server, enabling the system to send notifications via email.
- firebase_config.json: This file should include the configuration details required to connect to the Firebase database, such as the API key, authentication domain, database URL, and storage bucket.
- twilio_credentials.json: This file should contain the authentication credentials for accessing the Twilio API, including the account SID and authentication token, enabling the system to send notifications via SMS.

## Further Reading

To read more about FANS, its implementation and design, you can visit its [GitHub Wiki][wiki].

[wiki]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/wiki
[alarm]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/alarm-system
[sensor-pi]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/sensor-pi
[gui]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/web-app
[haptic]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/pico_alarm
[notifier]: https://github.com/SYSC3010-W24/sysc3010-project-l1-g8/tree/main/notifier
[pi-pinout]: https://www.the-diy-life.com/wp-content/uploads/2021/05/Raspberry-Pi-4-Pinout.png
