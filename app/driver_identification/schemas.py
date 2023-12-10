from enum import Enum
from pydantic import BaseModel

class DriverIdentificationStatus(str, Enum):
    driver_1 = 'Driver 1'
    driver_2 = 'Driver 2'
    driver_3 = 'Driver 3'
    driver_4 = 'Driver 4'

class DriverIdentificationOutput(BaseModel):
    status: DriverIdentificationStatus
