from datetime import datetime
from typing import NamedTuple, Optional

ClassName = str
EnumName = str
SlotName = str
EnumValName = str
URI = str
CURIE = str


CIM_PREFIX = "cim"
CIM_BASE_URI = "https://cim.ucaiug.io/ns#"


class PermissibleValue(NamedTuple):
    meaning: Optional[URI | CURIE] = None


class Slot(NamedTuple):
    name: str
    slot_uri: URI | CURIE
    range: str
    required: bool = False
    multivalued: bool = False
    description: Optional[str] = None


class Enum(NamedTuple):
    name: str
    enum_uri: URI | CURIE
    permissible_values: dict[EnumValName, dict[str, PermissibleValue]]
    description: Optional[str] = None
    from_schema: Optional[URI] = None


class Class(NamedTuple):
    name: str
    class_uri: URI | CURIE
    is_a: Optional[str] = None
    annotations: Optional[dict[str, str]] = None
    from_schema: Optional[URI] = None
    description: Optional[str] = None
    attributes: Optional[dict[SlotName, Slot]] = None


class Schema(NamedTuple):
    id: URI | CURIE
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    contributors: Optional[list[URI | CURIE]] = None
    created_by: Optional[URI | CURIE] = None
    generation_date: Optional[datetime] = None
    license: Optional[str] = None
    metamodel_version: Optional[str] = None
    imports: Optional[list[str]] = None
    prefixes: Optional[dict[str, str]] = None
    default_curi_maps: Optional[list[str]] = None
    default_prefix: Optional[str] = None
    default_range: Optional[str] = None
    classes: Optional[dict[ClassName, Class]] = None
    enums: Optional[dict[EnumName, Enum]] = None
