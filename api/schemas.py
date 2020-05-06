import re

import jsonschema

from demo.settings import REG_URL

URL_SCHEMA = {
    "type": "object",
    "properties": {
        "links": {
            "type": "array",
            "items": {
                "type": "string",
                "format": "link"
            }
        }
    }
}


@jsonschema.FormatChecker.cls_checks("link")
def _validate_link_format(instance):
    try:
        if re.search(REG_URL, instance) is None:
            raise ValueError
    except ValueError:
        return False
    else:
        return True
