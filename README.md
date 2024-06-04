# MACOBOX

**The all-in-one hacking toolbox for hardware penetration testing.**

## Overview

MACOBOX is designed to simplify and enhance hardware penetration testing by providing a comprehensive toolset for analyzing and extracting firmware from various hardware interfaces. With a custom 3D printed case and dedicated boards, MACOBOX ensures a seamless and efficient testing experience.

![Demo of MACOBOX in action](images/macobox.gif)


## Features

- **Automated Analysis**: Perform automated analysis of UART, SPI, I2C, and JTAG interfaces through an intuitive web interface.
- **3D Printed Case**: Comes with a sturdy and portable 3D printed case.
- **Custom Boards**: Includes custom boards for debug interfaces and an internal board for battery circuits, USB ports, and more.
- **Firmware Extraction**: Extract firmware from the supported interfaces.
- **Firmware Analysis Integration**: Integrates with third-party firmware analysis tools to analyze extracted firmware and generate detailed vulnerability reports.

## Getting Started

### Prerequisites

To use MACOBOX, you will need the following:
- Orange Pi Zero3 (may change in future releases)
- Printed PCBs and soldered SMD parts
- Touch screen
- Configured OS
- Third party firmware analysis tool APIs installed and configured

### Usage

Once the OS is properly configured, the app will start automatically at boot in kiosk mode with the following command:

`$ docker-compose up --build`

1. **Connect the hardware:**
    Connect MACOBOX to your target hardware using the provided debug interfaces.

2. **Start analyzing:**
    Use the MACOBOX app to interact with the target device.


## Acknowledgments

- This tool was developed in collaboration with whid.ninja (Luca Bongiorni) who provided technological support and acted as a beta tester for the finished product. 

---

*For more information, contact us at [info@mindstormsecurity.com](mailto:info@mindstormsecurity.com).*

