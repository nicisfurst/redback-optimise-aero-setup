"""
File for all the OLAP sims
Written by Nic Furst (z5421049)
Date: 05/05/2022
"""


# Imports
import pandas as pd
from constants import *
import logging
import sys
import os
import manage_files
import calcs
from tqdm import tqdm, trange

sys.path.append(REL_LIBS_DIR)
try:
    import matlab.engine as mateng
except ModuleNotFoundError:
    raise ModuleNotFoundError('Please either (1) run the program from the src directory or (2) check that matlab is in the libs directory')


# Init Logging
logger = logging.getLogger(__name__)


def start_mateng(olap_path: str = REL_OLAP_DIR) -> mateng.EngineSession:
    """Starts a matlab engine

    Args:
        olap_path (str, optional): Path to olap Defaults to REL_LOGS_DIR.

    Returns:
        mateng.EngineSession: EngineSession Object
    """
    
    eng = mateng.start_matlab()    
    eng.cd(olap_path)
    logging.info('Matlab Engine Successfully Created and Initialised')
    return eng


def simulate_range(cl_range: list[float] = None,         cdf_range: list[float] = None,
                      eng: mateng.EngineSession = None,        n: int = 4,
         vehicle_template: str = RB21E_TEMPLATE_NAME, sim_folder: str = None,
             save_results: bool = True) -> pd.DataFrame:
    """Runs a set of simulations for a given range of cl or cdf
    NOTE: Only pass cl_range XOR cdf_range

    Args:
        cl_range (list[float]): cl range
        cdf_range (list[float]): cdf range
        eng (mateng.EngineSession): Matlab Engine if one has already been setup. Defaults to None.
        n (int, optional): Number of subintervals within the given range. Defaults to 5.
        vehicle_template (str, optional): XLSX Vehicle template to use. Defaults to RB21E_TEMPLATE_NAME.
        sim_folder (str, optional): If set is called in a batch of simulations, this is its folder name
        save_results (bool, optional): If true, saves the results as a csv in the sim_folder folder

    Returns:
        pd.DataFrame: Cols: ['time', 'cl', 'cdf']
    """
    # TODO: add variability of track
    # Check Input Values (ranges)
    if cl_range is not None and cdf_range is None:
        iter_range = cl_range 
    elif cl_range is None and cdf_range is not None:
        iter_range = [-cdf_range[0], -cdf_range[1]]
    elif cl_range is None and cdf_range is None:
        raise ValueError('Must pass cl_range or cd_range to the function')
    else:
        raise ValueError('Can not pass both cl_range and cd_range, must pass one or the other')
    
    if eng is None:
        logger.info('No matlab engine passed, starting one now')
        eng = start_mateng()
        end_eng = True
    else:
        end_eng = False
    
    if sim_folder is None:
        sim_folder = manage_files.format_sim_folder('set')
        
    # Inits
    try:
        os.mkdir(f'{REL_RESULTS_DIR}/{sim_folder}')
        logger.info('Sim folder doesn\'t exist, created one')
    except FileExistsError:
        logger.warning('Sim folder already exists, continuing')
    
    results = pd.DataFrame(float(0), index=list(range(0,n)), columns=[PD_TIME_COL, PD_CL_COL, PD_CDF_COL, PD_CD_COL])
    
    # Main iter
    # TODO: add kwards to get_cl_cd_pairs to read k, clo etc from xlsx
    for i, cl_cd_tuple in tqdm(enumerate(calcs.get_cl_cd_pairs(cl_range=cl_range, n=n)), total=n, desc='Simulating Set'):
        logging.debug(f'starting simulation, {i=}')
        cl, cd = cl_cd_tuple
        cl = calcs.sigfig_round(cl)
        cd = calcs.sigfig_round(cd)
        
        # (0) Check if it already exists
        final_dir = f'{REL_RESULTS_DIR}/{sim_folder}/{cl=} ~ {cd=}'
        if not os.path.isdir(final_dir):
        
            # (1) Adjust vehicle params and send to OLAP
            manage_files.edit_vehicle_setup(vehicle_template, cd=cd, cl=cl)
            logging.debug('vehicle params set')
            
            # (2) Build the Vehicle Model
            eng.run(OLAP_BUILD_VEHICLE_FILE, nargout=0)
            eng.close()
            logging.debug('vehicle model built')
            
            # (3) Simulate the Lap
            eng.run(OLAP_SIM_LAP_FILE, nargout=0)
            eng.close()
            logging.debug('lap simulated')
            
            # (4) Move files and dirs out of OLAP
            os.rename(f'{REL_OLAP_DIR}/{OLAP_SIMS_DIR}', final_dir)
            logging.debug(f'sim dir moved to {final_dir=}')
        
        else:
            logging.info(f'{final_dir} exists, skipping this sim')
            
        # (5) Read in the final lap time
        df = pd.read_csv(f'{final_dir}/OpenLAP_sim.csv', header=10).iloc[1:]
        # TODO: add sig figs func implementation
        results.loc[i, PD_TIME_COL] = calcs.sigfig_round(df.iloc[-1][PD_TIME_COL])
        results.loc[i, PD_CL_COL] = cl
        results.loc[i, PD_CDF_COL] = -cl
        results.loc[i, PD_CD_COL] = -cd
        logging.debug('read final lap time and added to results')
        
    if end_eng:
        eng.exit()
    
    if save_results:
        results.to_csv(f'{REL_RESULTS_DIR}/{sim_folder}')
    
    # Return results
    return results


def optimise(vehicle_template: str = RB21E_TEMPLATE_NAME, session_name: str = None,
                   iterations: int = 5, eng: mateng.EngineSession = None, **kwargs) -> pd.Series:
    """Finds the optimal level of cl and cd to achieve the fastest lap times

    Args:
        vehicle_template (str, optional): XLSX Vehicle template to use. Defaults to RB21E_TEMPLATE_NAME.
        session_folder (str, optional): Custom name for the given optimisation session
        iteration (int, optional): Number of iterations to find the optimal cdf cl ratio
        eng (mateng.EngineSession, optional): Matlab Engine if one has already been setup. Defaults to None.

    Returns:
        pd.Series: optimal time, cdf, cl, cd
    """

    iter_cl_range = STARTING_CL_RANGE
  
    if eng is None:
        logger.info('No matlab engine passed, starting one now')
        eng = start_mateng()
        end_eng = True
    else:
        end_eng = False
        
    if session_name is None:
        session_name = manage_files.format_sim_folder('optimise')
        
    # Inits
    try:
        os.mkdir(f'{REL_RESULTS_DIR}/{session_name}')
        logger.info('Sim folder doesn\'t exist, created one')
    except FileExistsError:
        logger.warning('Sim folder already exists, continuing')
    
    # Main itter
    for i in trange(iterations):
        logging.info(f'Starting iteration {i=} of optimise')
        results = simulate_range(cl_range=iter_cl_range, eng=eng, vehicle_template=vehicle_template, 
                                 sim_folder=session_name, save_results=False, **kwargs)
        min_time = results[PD_TIME_COL].idxmin()
        logging.debug(f'min time is {min=}, and {results=}')
        iter_cl_range[0] = results.loc[min_time-1, PD_CL_COL]
        iter_cl_range[1] = results.loc[min_time+1, PD_CL_COL]
    
    logging.info('Optimise ran successfully')

    # Return the min cl, cd, and time
    return results.loc[min_time]


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=LOGGING_FORMATTER, 
                        filename=f'{REL_LOGS_DIR}/manage_files', filemode='a')
