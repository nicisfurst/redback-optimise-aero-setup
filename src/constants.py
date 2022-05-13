"""
Constants file to ensure consistency across the project
Allows for values to easily be changed if needed
NOTE: Logging specific constants and parameters can be found in __init__.py
"""

# Relative Paths (from src directory)
REL_VEHICLE_TEMPLATES_DIR = '../vehicle templates'
REL_OLAP_DIR = '../libs/openlap'
REL_LIBS_DIR = '../libs'
REL_RESULTS_DIR = '../results'

# Vehicle xlsx properties (NOTE: Following must be consistent with OLAP's code)
XLSX_INFO_SHEET = 'Info'
XLSX_TORQUE_SHEET = 'Torque Curve'
XLSX_OTHER_SHEET = 'Other'
XLSX_DESC_COL = 'Description'
XLSX_VAL_COL = 'Value'
XLSX_CD_ROW = 'Drag Coefficient CD'
XLSX_CL_ROW = 'Lift Coefficient CL'
XLSX_NAME_ROW = 'Name'

# Templates
RB21E_TEMPLATE_NAME = 'RB21-E.xlsx'
F1_TEMPLATE_NAME = 'Formula 1.xlsx'
TEST_TEMPLATE_NAME = 'TestRB21-E.xlsx'

# Tracks
MONZA_TRACK_NAME = 'Autodromo Nazionale Monza'

# OLAP
OLAP_VEHICLE_INFO_FILE = 'car.xlsx'
OLAP_BUILD_VEHICLE_FILE = 'OpenVEHICLE.m'
OLAP_SIM_LAP_FILE = 'OpenLAP.m'
OLAP_SIMS_DIR = 'OpenLap Sims'

# Simulation / Optimisation
STARTING_CL_RANGE = [-1, -10]

# Results (internal/external)
DATETIME_FORMATTING = '%d_%h_%y_%Hh_%Mm'
SIG_FIGS = 6
PD_TIME_COL = 'time'
PD_CL_COL = 'cl'
PD_CDF_COL = 'cdf'
PD_CD_COL = 'cd'

# Logging
LOGGING_FORMATTER = '[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s'
REL_LOGS_DIR = 'logs'

