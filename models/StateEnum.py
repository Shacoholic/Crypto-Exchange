from enum import Enum


class State(Enum):
    PROCESSING = "Processing"
    PROCESSED = "Processed"
    REJECTED = "Rejected"
