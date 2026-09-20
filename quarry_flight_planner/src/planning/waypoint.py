from dataclasses import dataclass, field
from enum import Enum


class ActionType(Enum):
    TAKEOFF = "takeoff"
    PHOTO = "photo"
    TURN = "turn"
    LAND = "land"


@dataclass
class Waypoint:
    x: float
    y: float
    z: float
    action: ActionType = ActionType.PHOTO
    heading_deg: float = 0.0
    gimbal_pitch_deg: float = -90.0
    metadata: dict = field(default_factory=dict)

    def __str__(self):
        return f"WP({self.x:.1f}, {self.y:.1f}, {self.z:.1f}) [{self.action.value}]"