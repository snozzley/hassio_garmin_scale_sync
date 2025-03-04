"""The Garmin Scale Sync integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN,SERVICE_NAME,DEFAULT_NAME
from .helper_methods import async_send_values_to_garmin_from_service

import voluptuous as vol
import logging

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("target"): cv.string,
        vol.Required("weight"): cv.string,
        vol.Optional("muscle_mass"): cv.string,
        vol.Optional("viceral_fat"): cv.string,
        vol.Optional("body_fat"): cv.string,
        vol.Optional("measurement_time"): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Asynchronously set up Garmin Scale Sync upon the addition of a config entry.
    This is called when Home Assistant is setting up the integration for a specific configuration entry.

    Args:
        hass (HomeAssistant): An instance representing the Home Assistant application.
        entry (ConfigEntry): The configuration entry that is being set up.

    Returns:
        bool: Indicates whether the setup was completed successfully (True) or failed (False).
    """
    # Placeholder for storing any necessary information in hass.data for later access by platforms.
    # Example:
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = YourCustomObject()

    # Validate any options in the config entry here before proceeding with setup.
    # If validation fails, you can return False or raise a specific exception.

    # Forward the setup to relevant platforms (sensor, button, etc.).
    await hass.config_entries.async_forward_entry_setups(
        entry, (Platform.NUMBER, Platform.BUTTON, Platform.DATETIME)
    )

    async def async_Sync_weight(service):
        """Service to sync weight to Garmin Connect"""
        _LOGGER.info("%s service called", service.service)
        params = {
             key: value for key, value in service.data.items() 
        }
        _LOGGER.info("Params %s",params)
        _LOGGER.info("Service Data %s",service.data)

        success = await async_send_values_to_garmin_from_service(service.data, hass)
        _LOGGER.info("Result %s",success)
    

    hass.services.async_register(
            DOMAIN, "sync_weight", async_Sync_weight, schema=SERVICE_SCHEMA
        )

    # Register a listener to handle options updates if the integration has an options flow.
    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))

    # Return True to indicate that the setup was successful.
    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Handle updates to the config entry.

    This callback is invoked when there are changes to the integration's options.
    Currently, it triggers a reload of the integration to apply the changes.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry that was updated.
    """
    # Reload the configuration entry to apply any changes made to the options.
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Asynchronously unload and clean up a config entry when it is removed.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry to be unloaded.

    Returns:
        bool: True if the unload process was successful, False otherwise.
    """
    # Remove the stored data for this config entry.
    unloaded = hass.data[DOMAIN].pop(entry.entry_id)

    # Reset any related platform setups for this config entry.
    return unloaded.async_reset()
