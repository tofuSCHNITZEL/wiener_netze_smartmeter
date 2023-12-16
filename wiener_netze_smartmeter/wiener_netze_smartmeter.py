"""Communicate with a Wiener Netze Smart Meter over a serial connection"""
import logging
from string import hexdigits
import binascii

from Crypto.Cipher import AES

import aioserial
import serial.tools.list_ports

from .meter_data import WienerNetzeSmartMeterData
from .exceptions import (
    WienerNetzeSmartMeterConnectionException,
    WienerNetzeSmartMeterDecryptionException,
)

_LOGGER = logging.getLogger(__name__)

_HDLC_PACKET_MARK = b"\x7E"


class WienerNetzeSmartMeter:
    """Communicate with a Wiener Netze Smart Meter over a serial connection"""

    def __init__(self, interface: str, decryption_key: str) -> None:
        self._serial_connection = None
        self._last_notification_data = None
        self._interface = interface
        self._decryption_key = decryption_key

        assert all(
            c in hexdigits for c in decryption_key
        ), "Decryption key must be in hex"
        assert (
            len(decryption_key) == 32
        ), "Decryption key must be 32 hex characters long"
        assert (
            interface in self.get_available_serial_ports()
        ), "Interface does not exist"

    def __del__(self):
        if self._serial_connection and self._serial_connection.isOpen():
            _LOGGER.info("Closing connection")
            self._serial_connection.close()

    def get_available_serial_ports(self) -> list:
        """Returns a list of available serial ports of the system"""
        if serial.tools.list_ports.comports and list(
            serial.tools.list_ports.comports()
        ):
            return [item[0] for item in list(serial.tools.list_ports.comports())]
        return []

    def connect(self):
        """Establishes serial connection"""
        try:
            self._serial_connection = aioserial.AioSerial(
                self._interface,
                baudrate=9600,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=3,
            )
            _LOGGER.info("Connection to serial port %s established", self._interface)
        except serial.serialutil.SerialException as e:
            _LOGGER.error(e)
            raise WienerNetzeSmartMeterConnectionException(str(e)) from e

    def is_connected(self) -> bool:
        """Checks if the connection is established"""
        if self._serial_connection is None:
            return False
        return self._serial_connection.isOpen()

    async def _async_receive_raw_data(
        self, length: int = 105, mark: bytes = _HDLC_PACKET_MARK
    ) -> bytes:
        """Reads raw byte data from serial with a defined length"""
        if not self._serial_connection:
            return None
        # read one whole notification packet (210 hex chars = 105 bytes) only valid for certain meters
        data = await self._serial_connection.read_async(length)

        # check if first and last byte are the same and from a smart meter - if not we started receiving in the middle of a package
        if self._validate_received_data(data):
            self._last_notification_data = data
            return data

        # data is not valid:
        _LOGGER.debug(
            "Started receiving in the middle of packet - waiting for next packet"
        )
        await self._serial_connection.read_until_async(mark)
        return await self._async_receive_raw_data(length, mark)

    def _validate_received_data(self, data) -> bool:
        """Test if data we received is a full HDLC Frame"""
        return data[-1:] == data[:1] and data[:1] == _HDLC_PACKET_MARK

    def _validate_decrypted_data(
        self, data: str, length: int = 74, check_byte: bytes = b"\x0f"
    ) -> bool:
        """Test if data was correctly decrypted"""
        return data and len(data) == length and data[:1] == check_byte

    def get_last_raw_notification_packet(self) -> bytes:
        """Return the raw data of the last received notification packet"""
        return self._last_notification_data

    def get_last_raw_decrypted_data(self) -> bytes:
        """Return the raw decrypted data of the last received notification packet"""
        return self._decrypt_notification_packet(self._last_notification_data)

    def _decrypt_notification_packet(self, data: bytes) -> bytes:
        """Decrypt notification packet with provided decryption key"""
        if data is None:
            return None

        sytem_title = data[14:22]
        invocation_counter = data[24:28]
        meter_data = data[28:-3]
        nonce = sytem_title + invocation_counter

        cipher = AES.new(
            binascii.unhexlify(self._decryption_key), AES.MODE_GCM, nonce=nonce
        )

        return cipher.decrypt(meter_data)

    async def read_meter_data(self) -> WienerNetzeSmartMeterData | None:
        """Reads meter and returns all meter data"""

        if not self.is_connected():
            try:
                self.connect()
            except WienerNetzeSmartMeterConnectionException:
                return None

        decrypted_data = self._decrypt_notification_packet(
            await self._async_receive_raw_data()
        )

        if not self._validate_decrypted_data(decrypted_data):
            raise WienerNetzeSmartMeterDecryptionException(
                "Decryption key seems not to be correct"
            )

        return WienerNetzeSmartMeterData(decrypted_data)

    def get_last_meter_data(self) -> WienerNetzeSmartMeterData | None:
        """Returns last received meter data"""
        if not self._last_notification_data:
            return None

        if not self._validate_decrypted_data(self.get_last_raw_decrypted_data()):
            raise WienerNetzeSmartMeterDecryptionException(
                "Decryption key seems not to be correct"
            )

        return WienerNetzeSmartMeterData(self.get_last_raw_decrypted_data())
