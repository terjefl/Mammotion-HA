"""Mammotion binary sensor entities."""

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pymammotion.data.model.device import MowingDevice
from pymammotion.utility.device_type import DeviceType

from . import MammotionConfigEntry
from .coordinator import MammotionBaseUpdateCoordinator
from .entity import MammotionBaseEntity


@dataclass(frozen=True, kw_only=True)
class MammotionBinarySensorEntityDescription(
    BinarySensorEntityDescription,
):
    """Describes Mammotion binary sensor entity."""

    is_on_fn: Callable[[MowingDevice], bool | None]


BINARY_SENSORS: tuple[MammotionBinarySensorEntityDescription, ...] = (
    MammotionBinarySensorEntityDescription(
        key="charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        is_on_fn=lambda mower_data: mower_data.report_data.dev.charge_state in (1, 2),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

# Luba 1 only — on Luba 1, a job paused (manually, or by returning to dock
# mid-job) stays paused with a resumable breakpoint until the mower is sent
# back out and actually reaches that point, rather than clearing immediately
# like MODE_PAUSE does on Luba 2 / Yuka. bp_info != 0 indicates that stored,
# resumable breakpoint — regardless of where the mower currently is.
LUBA_1_ONLY_BINARY_SENSORS: tuple[MammotionBinarySensorEntityDescription, ...] = (
    MammotionBinarySensorEntityDescription(
        key="job_paused",
        translation_key="job_paused",
        device_class=None,
        is_on_fn=lambda mower_data: mower_data.report_data.work.bp_info != 0,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MammotionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Mammotion sensor entity."""
    mammotion_devices = entry.runtime_data.mowers

    for mower in mammotion_devices:
        async_add_entities(
            MammotionBinarySensorEntity(mower.reporting_coordinator, entity_description)
            for entity_description in BINARY_SENSORS
        )

        if DeviceType.is_luba1(mower.device.device_name, mower.device.product_key):
            async_add_entities(
                MammotionBinarySensorEntity(
                    mower.reporting_coordinator, entity_description
                )
                for entity_description in LUBA_1_ONLY_BINARY_SENSORS
            )


class MammotionBinarySensorEntity(MammotionBaseEntity, BinarySensorEntity):
    """Mammotion sensor entity."""

    entity_description: MammotionBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: MammotionBaseUpdateCoordinator,
        entity_description: MammotionBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor entity."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description
        self._attr_translation_key = entity_description.translation_key

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)
