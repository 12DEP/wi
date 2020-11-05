"""Support for Google Wifi Routers as device tracker."""

from homeassistant.components.device_tracker.config_entry import ScannerEntity
from homeassistant.components.device_tracker.const import DOMAIN as DEVICE_TRACKER
from homeassistant.components.device_tracker.const import SOURCE_TYPE_ROUTER
from homeassistant.const import ATTR_NAME

from . import GoogleWifiEntity, GoogleWiFiUpdater
from .const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    COORDINATOR,
    DEFAULT_ICON,
    DEV_CLIENT_MODEL,
    DEV_MANUFACTURER,
    DOMAIN,
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the device tracker platforms."""

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    entities = []

    for system_id, system in coordinator.data.items():
        for dev_id, device in system["devices"].items():
            device_name = f"{device['friendlyName']}"

            if device.get("friendlyType"):
                device_name = device_name + f" ({device['friendlyType']})"

            entity = GoogleWifiDeviceTracker(
                coordinator=coordinator,
                name=device_name,
                icon=DEFAULT_ICON,
                system_id=system_id,
                item_id=dev_id,
            )
            entities.append(entity)

    async_add_entities(entities)


class GoogleWifiDeviceTracker(GoogleWifiEntity, ScannerEntity):
    """Defines a Google WiFi device tracker."""

    def __init__(self, coordinator, name, icon, system_id, item_id):
        """Initialize the device tracker."""
        super().__init__(
            coordinator=coordinator,
            name=name,
            icon=icon,
            system_id=system_id,
            item_id=item_id,
        )

        self._is_connected = None

    @property
    def is_connected(self):
        """Return true if the device is connected."""
        try:
            if self.coordinator.data[self._system_id]["devices"][self._item_id].get(
                "connected"
            ):
                connected_ap = self.coordinator.data[self._system_id]["devices"][
                    self._item_id
                ].get("apId")
                if connected_ap:
                    connected_ap = self.coordinator.data[self._system_id][
                        "access_points"
                    ][connected_ap]["accessPointSettings"]["accessPointOtherSettings"][
                        "roomData"
                    ][
                        "name"
                    ]
                    self._attrs["connected_ap"] = connected_ap
                else:
                    self._attrs["connected_ap"] = "NA"

                if self.coordinator.data[self._system_id]["devices"][self._item_id].get(
                    "ipAddresses"
                ):
                    self._attrs["ip_address"] = self.coordinator.data[self._system_id][
                        "devices"
                    ][self._item_id]["ipAddresses"][0]

                self._is_connected = True
            else:
                self._is_connected = False
        except TypeError:
            pass

        return self._is_connected

    @property
    def source_type(self):
        """Return the source type of the client."""
        return SOURCE_TYPE_ROUTER

    @property
    def device_info(self):
        """Define the device as a device tracker system."""
        device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, self._item_id)},
            ATTR_NAME: self._name,
            ATTR_MANUFACTURER: "Google",
            ATTR_MODEL: DEV_CLIENT_MODEL,
            "via_device": (DOMAIN, self._system_id),
        }

        return device_info
