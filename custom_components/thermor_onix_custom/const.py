"""Constants for the Thermor Onix DHW Plus integration."""
from homeassistant.const import Platform

DOMAIN = "thermor_onix_custom"

# Configuration keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SERVER = "server"
CONF_POLL_INTERVAL = "poll_interval"

# Default values
DEFAULT_POLL_INTERVAL = 60  # seconds (balanced between responsiveness and avoiding rate limits)
DEFAULT_SERVER = "thermor_cozytouch"

# Supported Home Assistant platforms
PLATFORMS: list[Platform] = [
    Platform.WATER_HEATER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.TIME,
    Platform.BUTTON,
]

# Overkiz / Cozytouch API State Names
STATE_WATER_TARGET_TEMP = "core:WaterTargetTemperatureState"
STATE_CONTROL_TARGET_TEMP = "core:ControlWaterTargetTemperatureState"
STATE_TEMP_OUTLET = "modbuslink:MiddleWaterTemperatureState"
STATE_TEMP_INLET = "core:MiddleWaterTemperatureInState"
STATE_BOOSTER_HOURS = "modbuslink:ElectricBoosterOperatingTimeState"
STATE_POWER_HEAT_ELECTRICAL = "modbuslink:PowerHeatElectricalState"
STATE_POWER_HEAT_ELECTRICAL_IN = "core:PowerHeatElectricalInState"
STATE_TARIFF_0 = "core:ConsumptionTariff0State"
STATE_TARIFF_1 = "core:ConsumptionTariff1State"
STATE_TARIFF_2 = "core:ConsumptionTariff2State"
STATE_ENERGY_TOTAL = "core:ElectricEnergyConsumptionState"
STATE_V40_VOLUME = "core:V40WaterVolumeEstimationState"
STATE_SHOWERS_REMAINING = "core:NumberOfShowerRemainingState"
STATE_SHOWERS_EXPECTED = "core:ExpectedNumberOfShowerState"
STATE_ANTI_LEGIONELLOSIS = "modbuslink:AntiLegionellosisState"
STATE_SMART_GRID = "modbuslink:SmartGridOptionState"
STATE_DHW_MODE = "modbuslink:DHWModeState"
STATE_BOOST_MODE = "modbuslink:DHWBoostModeState"
STATE_ABSENCE_MODE = "modbuslink:DHWAbsenceModeState"
STATE_HEATING_STATUS = "core:HeatingStatusState"
STATE_DHW_ERROR = "modbuslink:DHWErrorState"
STATE_DHW_CAPACITY = "modbuslink:DHWCapacityState"
STATE_NUMBER_OF_TANK = "core:NumberOfTankState"
STATE_PROGRAMMING_SLOTS = "modbuslink:ProgrammingSlotsState"
STATE_OPERATING_RANGE = "modbuslink:OperatingRangeState"
STATE_RSSI_LEVEL = "core:RSSILevelState"
STATE_DATE_TIME = "core:DateTimeState"

# Overkiz API Command Names
CMD_SET_WATER_TARGET_TEMP = "setWaterTargetTemperature"
CMD_SET_EXPECTED_SHOWERS = "setExpectedNumberOfShower"
CMD_SET_BOOST_MODE = "setBoostMode"
CMD_SET_ABSENCE_MODE = "setAbsenceMode"
CMD_SET_DHW_MODE = "setDHWMode"
CMD_SET_ANTI_LEGIONELLOSIS = "setAntiLegionellosis"
CMD_SET_SMART_GRID_OPTION = "setSmartGridOption"
CMD_SET_OPERATING_RANGE = "setOperatingRange"
CMD_SET_PROGRAMMING_SLOTS = "setProgrammingSlots"
CMD_SET_DATE_TIME = "setDateTime"

# Operating Range mapping
RANGE_24H = "pac24h_elec24h"
RANGE_PROGRAMMED = "pacProg_elecProg"
RANGE_OFF_PEAK = "pac24h_elecHC"
