from datetime import datetime
from pytz import UTC


def now():
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')
