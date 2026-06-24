from datetime import datetime

FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%m/%d/%Y %H:%M:%S",
    "now"
]

def is_valid_timestamp(ts):
    if ts == "now":
        return True
    for fmt in [f for f in FORMATS if f != "now"]:
        try:
            datetime.strptime(ts, fmt)
            return True
        except ValueError:
            pass
    return False