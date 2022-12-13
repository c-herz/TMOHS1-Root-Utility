# TMOHS1 Root Utility

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Description

An interactive python script that enables root access on the T-Mobile (Wingtech) TMOHS1, as well as providing several useful utilites to change the configuration of the device.

## Features

- Root shell via telnet
- Temporarily or pesistently enable ADB
- Disable OMA-DM update bootstrap
- On-device root FTP server to browse the filesystem
- Mood lighting
- Mask data that would normally be counted against your hotspot quota as "on-client-device" data

## What it doesn't (yet?) feature

- SIM unlock :(
- SSH server installation
- Other USB modes (though if you edit `utils.py` you can easily implement this)

## Setup

Ensure you have Python >= 3.6 and pip installed then run:

```bash
pip install -r requirements.txt
```

Or install the required libraries manually.

## Usage

Connect to your hotspot's network via USB tethering (recommended) or WiFi, then run:

```sh
python ./rootScript.py
```
Or for verbose/debug output:
```sh
python ./rootScript.py -v
```

### **Notes**

- The script has been tested to work on Windows 10 & 11, EndeavorOS Linux, and MacOS 13 Ventura
- Script assumes your hotspot's IP is 192.168.0.1
- Script assumes you have set a **custom** weblogin password, i.e. you have changed it from the default AdminXXXX
- For the sake of your own experimentation, the script leaves an unauthenticated root FTP server running on the device *but only once you enable it*. When you are done browsing the filesystem, be sure to manually close it by running `killall tcpsvd` on the TMOHS1 as root, or simply reboot the device.
