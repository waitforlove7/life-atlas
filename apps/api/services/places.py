from models.place import PlaceStatus

MAP_LIGHTING_STATUSES = (
    PlaceStatus.visited,
    PlaceStatus.lived,
    PlaceStatus.worked,
    PlaceStatus.studied,
)


def status_lights_map(status: str | PlaceStatus) -> bool:
    """Return whether a status represents an actual life experience."""
    value = status.value if isinstance(status, PlaceStatus) else status
    return value in {item.value for item in MAP_LIGHTING_STATUSES}
