"""USB interface implementations belong here."""
from .mock_usb import MockUSBInterface, USBTransfer

__all__ = ["MockUSBInterface", "USBTransfer"]
