from utils import Services
from datetime import datetime


def serialize(package):
    result = {}
    for field in package:
        if isinstance(package[field], Services):
            result[field] = package[field].value
            continue
        if isinstance(package[field], datetime):
            result[field] = package[field].strftime('%Y-%m-%d %H:%M:%S')
            continue
        result[field] = package[field]
    return result
