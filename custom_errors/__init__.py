"""(Deprecated) custom_errors is a module that contains custom exceptions for the Vectra API wrapper.

This module is deprecated and will be removed in a future release. 
It was used for the Vectra API wrapper which is no longer supported. 
Instead, everything has been moved to the VectraClient class in the vectra module.

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
