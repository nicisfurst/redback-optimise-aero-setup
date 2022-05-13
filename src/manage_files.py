"""
File for all the file handling to interface with OpenLAP
Written by Nic Furst (z5421049)
Date: 05/05/2022
"""


# Imports
import pandas as pd
from constants import *
import logging
from datetime import datetime


# Init Logging
logger = logging.getLogger(__name__)


# Gets info and torque data from a vehicle template
def get_vehicle_template(file_name: str) -> list[pd.DataFrame]:
    """Get vehicle template info and torque data

    Args:
        file_name (str): name of the vehicle template file

    Returns:
        list[pd.DataFrame]: returns info_df, toqrue_df, and other_df
    """
    
    logger.debug(f'Called with {file_name=}')
    
    # Load in the sheets from the vehicle templates
    info_df = pd.read_excel(f'{REL_VEHICLE_TEMPLATES_DIR}/{file_name}', sheet_name=XLSX_INFO_SHEET)
    torque_df = pd.read_excel(f'{REL_VEHICLE_TEMPLATES_DIR}/{file_name}', sheet_name=XLSX_TORQUE_SHEET)
    other_df = pd.read_excel(f'{REL_VEHICLE_TEMPLATES_DIR}/{file_name}', sheet_name=XLSX_OTHER_SHEET)
    
    return [info_df, torque_df, other_df]


# Edits the cl and cd of a given vehicle file
def edit_vehicle_setup(file_name: str, cd: float, 
                       cl: float = None, cdf: float = None) -> None:
    """Edits the cl and cd of a given vehicle file

    Args:
        cl (float): coefficient of lift
        cd (float): coefficient of drag
        file (str): name of the vehicle template file
    """
    
    logger.debug(f'Called with {cl=}, {cdf=}, {cd=}, {file_name=}')
    
    # Check Input Vals
    if cl is not None and cdf is None:
        pass 
    elif cl is None and cdf is not None:
        cl = -cdf
    elif cl is None and cdf is None:
        raise ValueError('Must pass cl or cd to the function')
    else:
        raise ValueError('Can not pass both cl and cd, must pass one or the other')
    
    # Load in the sheets from the vehicle templates
    sheets = get_vehicle_template(file_name)
    info_df = sheets[0]
    torque_df = sheets[1]

    # Substitute the appropriate cl and cd values
    info_df.loc[info_df[XLSX_DESC_COL] == XLSX_CD_ROW, XLSX_VAL_COL] = cd
    info_df.loc[info_df[XLSX_DESC_COL] == XLSX_CL_ROW, XLSX_VAL_COL] = cl

    # Write the modified info into OpenLAP
    writer = pd.ExcelWriter(f'{REL_OLAP_DIR}/{OLAP_VEHICLE_INFO_FILE}', engine='xlsxwriter')
    info_df.to_excel(writer, sheet_name=XLSX_INFO_SHEET, index=False)
    torque_df.to_excel(writer, sheet_name=XLSX_TORQUE_SHEET, index=False)
    logger.debug('Writing XLSX to OLAP')
    writer.save()


def format_sim_folder(sim_type: str) -> str:
    """Formats the name of sim folders

    Args:
        sim_type (str): Either 'range' or 'optimise'

    Returns:
        str: Name of folder
    """
    
    # Check vals
    if sim_type not in ['range', 'optimise']:
        logging.error(f'Invalid {sim_type=}, must be either "range" or "optimise"')
        raise ValueError(f'Invalid {sim_type=}, must be either "range" or "optimise"')
    
    return f'{sim_type.upper()}_{datetime.now().strftime(DATETIME_FORMATTING)}'


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=LOGGING_FORMATTER, 
                        filename=f'{REL_LOGS_DIR}/manage_files', filemode='a')
