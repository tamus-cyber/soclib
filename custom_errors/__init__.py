"""custom_errors is a module that contains custom exceptions for the Vectra API wrapper.
"""

class LoopInterupt(Exception):
    """Exception raised when detection loop should skip the current detection.

    Args:
        Exception: Common base class for all exceptions.
    """


class DetectionNotFound(Exception):
    """Exception raised when a detection is not found. Used to dead-letter detections.

    Args:
        Exception: Common base class for all exceptions.
    """
