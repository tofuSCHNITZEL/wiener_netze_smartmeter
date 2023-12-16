"""Contains exceptions for this module"""


class WienerNetzeSmartMeterConnectionException(Exception):
    """Exception indicating problems with the connection to the accespoint"""

    def __init__(self, message):
        super().__init__(message)


class WienerNetzeSmartMeterDecryptionException(Exception):
    """Exception indicating a problem with the decryption"""

    def __init__(self, message):
        super().__init__(message)
