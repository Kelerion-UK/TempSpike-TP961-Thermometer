# TempSpike TP961 Meat Thermometer Integration for Home Assistant

A lightweight, high-performance Home Assistant custom integration for the **ThermoPro TempSpike TP961 BLE Meat Thermometer**. 

This component leverages Home Assistant's native Bluetooth architecture and push-notifications to instantly track internal and ambient temperatures without blocking the main event loop or risking connection conflicts.

---

## Features

- ⚡ **Instant Push Updates**: Listens to active BLE notification broadcasts (updates occur immediately when the probe transmits data).
- 🔋 **Battery Monitoring**: Tracks the battery level percentage calculated from raw millivolt readings.
- 📡 **Bluetooth Proxy Support**: Fully compatible with ESPHome Bluetooth proxies for extended range throughout your home.
- 🧩 **UI-Based Setup**: Configured via the integrations dashboard with optional automated background discovery.

---

## Entities Tracked

Once configured, the integration populates three distinct sensor entities:

1. **Internal Temperature** (`°C`) - Real-time temperature of the meat probe tip.
2. **Ambient Temperature** (`°C`) - Real-time temperature of the oven/grill environment.
3. **Battery** (`%`) - Remaining charge level of the wireless probe.

---

## Installation

1. Download the source code as a `.zip` file from this repository.
2. Extract the archive and copy the `custom_components/tempspike_tp961` folder into your Home Assistant `config/custom_components/` directory.
3. **Restart** Home Assistant.

---

## Configuration

1. In Home Assistant, navigate to **Settings** -> **Devices & Services**.
2. Click the **+ Add Integration** button in the bottom right corner.
3. Search for **TempSpike TP961 Meat Thermometer**.
4. Enter the Bluetooth MAC address of your TempSpike TP961 Thermometer (e.g., `8C:65:A3:2D:5F:B5`) and click **Submit**.
5. *Note: If the probe is powered on and advertising nearby, Home Assistant may automatically find it and show a **Discovered** prompt at the top of your integrations page.*

---

## Technical Details

The integration monitors the notification stream on GATT characteristic `0000ff01-0000-1000-8000-00805f9b34fb`. It intercepts the raw 8-byte Little-Endian data frames to parse the information:

- **Byte 0**: Validation preamble header (`0x10`).
- **Bytes 2-3**: Internal temperature calculation (with a 30°C offset calibration adjustment).
- **Bytes 4-5**: Raw battery voltage mapping (interpolated to 0%, 33%, 66%, or 100%).
- **Bytes 6-7**: Ambient temperature calculation (with a 30°C offset calibration adjustment).

---

## Credits & Disclaimer

This project is community-driven and not officially affiliated with or endorsed by ThermoPro. All product names, logos, and brands are property of their respective owners.
