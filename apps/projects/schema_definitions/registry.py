from .text import TextField
from .number import NumberField
from .date import DateField
from .latlong import LatLongField
from .dropdown import DropdownField
from .bool import BoolField
from .reference import ReferenceField

FIELD_REGISTRY = {
    cls.type: cls
    for cls in [
        TextField,
        NumberField,
        DateField,
        LatLongField,
        DropdownField,
        BoolField,
        ReferenceField,
    ]
}


def get_field_class(ftype):
    if ftype not in FIELD_REGISTRY:
        raise ValueError(f"Unknown field type: {ftype}")
    return FIELD_REGISTRY[ftype]
