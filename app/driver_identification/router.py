import asyncio
import pandas as pd
import joblib
import numpy as np

from fastapi import APIRouter, UploadFile
from loguru import logger

import app.driver_identification.schemas as schemas 
from settings import settings

router = APIRouter(
    prefix='/driver_identification',
    tags=['driver_identification'],
)

path_to_model = settings.storage_folder.joinpath('driver_identification/model.joblib')
model = joblib.load(path_to_model)

columns_to_drop = ['can.fuel.level', 'can.ambient.air.temperature', 'movement.status', 'timestamp', 
                   'server.timestamp', 'ident', 'position.altitude', 'position.latitude' , 'position.longitude']

statuses = [schemas.DriverIdentificationStatus.driver_1, schemas.DriverIdentificationStatus.driver_2, 
         schemas.DriverIdentificationStatus.driver_3, schemas.DriverIdentificationStatus.driver_4]

def proccesing(input: pd.DataFrame):
    current_columns_to_drop = []
    for i in columns_to_drop:
        if i in input.columns:
            current_columns_to_drop.append(i)

    print(current_columns_to_drop)
    input = input.drop(columns=current_columns_to_drop, axis=1)
    input.fillna(0, inplace=True)

    return input


@router.post(
    "/upload",
    response_model = schemas.DriverIdentificationOutput
)
async def driver_identification(
        driver_identification_input: UploadFile,
):
    data_file = driver_identification_input

    if not data_file.filename.endswith(".csv"):
        return {"error": "Only CSV files are allowed."}

    data_df = pd.read_csv(data_file.file, sep = ";")

    proccesed_data_df = proccesing(data_df)
    proccesed_data_df = proccesed_data_df.sort_index(axis=1)

    output = model.predict(proccesed_data_df)

    counts = np.bincount(output)

    most_frequent_value = np.argmax(counts)

    status = statuses[most_frequent_value]

    logger.info(f'status is {status}')
    return schemas.DriverIdentificationOutput(status=status)


async def main():
    csv_file_path = '/Users/kuanyshbakytuly/Desktop/Relive/driver_ident_server/Talgat-Table 1.csv'

    data = pd.read_csv(csv_file_path, sep = ';')
    json_data = data.to_json()

    input_data = schemas.DriverIdentificationInput(
        json_data=json_data
    )

    res = await driver_identification(input_data)


if __name__ == '__main__':
    asyncio.run(main())
