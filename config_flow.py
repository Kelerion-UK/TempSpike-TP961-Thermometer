import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN

class TempSpikeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TempSpike TP961 Meat Thermometer."""
    VERSION = 1

    def __init__(self):
        """Initialize the flow."""
        self._discovery_info = None

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak):
        """Handle discovery via local Bluetooth or proxies."""
        address = discovery_info.address
        await self.async_set_unique_id(address.upper())
        self._abort_if_unique_id_configured()

        self._discovery_info = {CONF_ADDRESS: address}
        self.context["title_placeholders"] = {"name": "TempSpike TP961"}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(self, user_input=None):
        """Confirm discovery step from the user UI."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"TempSpike TP961 ({self._discovery_info[CONF_ADDRESS]})", 
                data=self._discovery_info
            )

        return self.async_show_form(step_id="bluetooth_confirm")

    async def async_step_user(self, user_input=None):
        """Fallback manual step if user adds it via the '+' button manually."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_ADDRESS].upper())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"TempSpike TP961 ({user_input[CONF_ADDRESS]})", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): str}),
            errors=errors,
        )
