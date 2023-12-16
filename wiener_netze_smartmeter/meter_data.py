"""Represents Wiener Netze Smart Meter Data"""
from datetime import datetime


class WienerNetzeSmartMeterData:
    """Represents Wiener Netze Smart Meter Data"""

    def __init__(self, raw_meter_data: bytes) -> None:
        self.date_time = datetime(
            year=int.from_bytes(raw_meter_data[22:24], "big"),
            month=int.from_bytes(raw_meter_data[24:25], "big"),
            day=int.from_bytes(raw_meter_data[25:26], "big"),
            hour=int.from_bytes(raw_meter_data[27:28], "big"),
            minute=int.from_bytes(raw_meter_data[28:29], "big"),
            second=int.from_bytes(raw_meter_data[29:30], "big"),
        )  # OBIS [0-0:1.0.0]
        self.active_energy_in = (
            int.from_bytes(raw_meter_data[35:39], "big") / 1000.000
        )  # +A Wh OBIS [1-0:1.8.0]
        self.active_energy_out = (
            int.from_bytes(raw_meter_data[40:44], "big") / 1000.000
        )  # -A Wh OBIS [1-0:2.8.0]
        self.reactive_energy_in = (
            int.from_bytes(raw_meter_data[45:49], "big") / 1000.000
        )  # +R varh OBIS [1-0:3.8.0]
        self.reactive_energy_out = (
            int.from_bytes(raw_meter_data[50:54], "big") / 1000.000
        )  # -R varh OBIS [1-0:4.8.0]
        self.active_power_in = int.from_bytes(
            raw_meter_data[55:59], "big"
        )  # +P W OBIS [1-0:1.7.0]
        self.active_power_out = int.from_bytes(
            raw_meter_data[60:64], "big"
        )  # -P W OBIS [1-0:2.7.0]
        self.reactive_power_in = int.from_bytes(
            raw_meter_data[65:69], "big"
        )  # +Q var OBIS [1-0:3.7.0]
        self.reactive_power_out = int.from_bytes(
            raw_meter_data[70:74], "big"
        )  # -Q var OBIS [1-0:4.7.0]

    def __str__(self) -> str:
        return f"{self.date_time}\n+A: {self.active_energy_in:.3f} kWh\n-A: {self.active_energy_out:.3f} kWh\n+R: {self.reactive_energy_in:.3f} kvarh\n-R: {self.reactive_energy_out:.3f} kvarh\n+P: {self.active_power_in:.0f} W\n-P: {self.active_power_out:.0f} W\n+Q: {self.reactive_power_in:.0f} var\n-Q: {self.reactive_power_out:.0f} var"
