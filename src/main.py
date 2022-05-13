"""
Main func to execute aero code
Project still in early days so not many docs, but if you look through the source
code, all funcs should be clearly documented and outlined as to how they work.

Typically, you would just call functions frm the simulation file, namely
simulation_range and optimise (look at the respective function for more info)

Logging has also been added, although to a limited extend
"""


# Imports
import logging
from constants import *
import simulation
import matplotlib.pyplot as plt


# Init Logging
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMATTER, filename=f'{REL_LOGS_DIR}/main', filemode='a')
# logging.basicConfig(level=logging.INFO, format=LOGGING_FORMATTER)
logger = logging.getLogger(__name__)


# # Test Sim
# results = simulation.simulate_range([-1, -7], vehicle_template=F1_TEMPLATE_NAME, sim_folder='testing', n=4)
# plt.plot(results[PD_CDF_COL], results[PD_TIME_COL])
# plt.show()
# print(results)


# Test Optimise
results = simulation.optimise(vehicle_template=F1_TEMPLATE_NAME, iterations=1, session_name='tt')
print(results)
