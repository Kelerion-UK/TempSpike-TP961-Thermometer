import asyncio
import logging
from homeassistant.components import bluetooth
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Home Assistant core bluetooth wrappers
from bleak_retry_connector import establish_connection, BleakClientWithServiceCache

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

NOTIFY_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the sensor platform."""
    address = entry.data[CONF_ADDRESS]

    internal_sensor = ProbeSensor(address, "Internal Temperature", "internal_temp", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
    ambient_sensor = ProbeSensor(address, "Ambient Temperature", "ambient_temp", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE)
    battery_sensor = ProbeSensor(address, "Battery", "battery", PERCENTAGE, SensorDeviceClass.BATTERY)

    async_add_entities([internal_sensor, ambient_sensor, battery_sensor])

    entry.async_on_unload(
        hass.async_create_background_task(
            monitor_ble_device(hass, address, internal_sensor, ambient_sensor, battery_sensor),
            "ble_probe_monitor"
        )
    )

async def monitor_ble_device(hass, address, internal_s, ambient_s, battery_s):
    """Background loop to manage active connection and receive notifications."""
    while True:
        ble_device = bluetooth.async_ble_device_from_address(hass, address.upper(), connectable=True)
        if not ble_device:
            _LOGGER.debug("Device %s not discovered yet. Retrying...", address)
            await asyncio.sleep(10)
            continue

        client = None
        try:
            # Fixed: Await establish_connection instead of using 'async with'
            client = await establish_connection(
                BleakClientWithServiceCache,
                ble_device,
                f"Probe {address}",
                max_attempts=3
            )
            _LOGGER.info("Successfully connected to BLE Probe: %s", address)

            def notification_callback(sender, data):
                # Fixed: Correct array indexing from your original working script
                if len(data) != 8 or data[0] != 0x10:
                    return

                probe = data[1]
                temp1 = ((data[3] << 8) | data[2]) - 30
                battery_mv = (data[5] << 8) | data[4]
                temp2 = ((data[7] << 8) | data[6]) - 30

                if battery_mv < 2311:
                    battery = 0
                elif battery_mv < 2451:
                    battery = 33
                elif battery_mv < 2601:
                    battery = 66
                else:
                    battery = 100

                # Push parsed state values directly into Home Assistant entities
                internal_s.update_state(temp1)
                ambient_s.update_state(temp2)
                battery_s.update_state(battery)

            await client.start_notify(NOTIFY_UUID, notification_callback)

            # Keep background worker alive while the BLE connection is active
            while client.is_connected:
                await asyncio.sleep(5)

        except Exception as err:
            _LOGGER.warning("BLE Probe Connection lost or failed: %s. Reconnecting...", err)
        finally:
            if client is not None:
                try:
                    await client.disconnect()
                except Exception:
                    pass
            await asyncio.sleep(10)

class ProbeSensor(SensorEntity):
    """Representation of a BLE Probe data sensor point."""

    def __init__(self, address, name_suffix, key, unit, device_class):
        self._address = address
        self._attr_name = f"TempSpike TP961 {name_suffix}"
        self._attr_unique_id = f"{address}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_should_poll = False
        self._attr_native_value = None

    def update_state(self, value):
        """Update native value and notify Home Assistant engine."""
        self._attr_native_value = value
        self.async_write_ha_state()
