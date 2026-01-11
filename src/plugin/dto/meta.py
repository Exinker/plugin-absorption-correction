from dataclasses import dataclass


@dataclass
class AtomMeta:
    organization_name: str
    device_name: str
    user_name: str
    analysis_name: str
