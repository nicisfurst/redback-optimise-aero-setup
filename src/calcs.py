"""
File for all the aero calculations needed for the Optimal Downforce Calcs
Written by Nic Furst (z5421049)
Date: 05/05/2022
"""


# Imports
from numpy import linspace
import logging
from constants import *


# Init Logging
logger = logging.getLogger(__name__)
    
    
# Calculates the Coefficient of Drag
def calculate_cd(*, cdf: float = None, cl: float = None, clo: float = 0.01, 
                    cdo: float = 0.6,   k: float = 0.04) -> float:
    """Calculates the Coefficient of Drag off a Given Coefficient of Downforce
    Can input either cdf of cl

    Args:
        cdf (float): Coefficient of Downforce
        clo (float, optional): Coefficient of Lift (no-aero). Paper-Defaults to 0.01.
        cdo (float, optional): Coefficient of Drag (no-aero). Paper-Defaults to 0.6.
        k (float, optional): Polar Coefficient? (is power to mass ratio?). Paper-Defaults to 0.04.

    Returns:
        float: Calculated Coefficient of Drag
    """

    logger.debug(f'Called with {cdf=}, {cl=}, {clo=}, {cdo=}, {k=}')
    
    # Check Input Values
    if cdf is not None and cl is None:
        cl = -cdf  # Coefficient of Lift
    elif cdf is None and cl is not None:
        pass
    elif cdf is None and cl is None:
        raise ValueError('Must pass cdf or cl to the function')
    else:
        raise ValueError('Can not pass both cdf and cl, must pass one or the other')
        
    # TODO: Explore origins of formula and its efficacy in this application 
    cd = -(k*(cl-clo)**2 + cdo)  # Coefficient of Drag, given by formula in the research paper
    logger.debug(f'{cd=}')
    
    return cd


# Gets tuple pairs of corresponding cl and cd
def get_cl_cd_pairs(
    cl_range: float = None, cdf_range: float = None,
           n: int = 10,      **kwargs) -> tuple:
    """Get cl and cd tuple pairs

    Args:
        cl_range (float, optional): Range given by cl. Defaults to None.
        cd_range (float, optional): Range given by cd. Defaults to None.
        n (int, optional): _description_. Defaults to 10.

    Returns:
        tuple: (cl, cd)

    Yields:
        Iterator[float]: (cl, cd) tuple
    """
    
    logger.debug(f'Called with {cl_range=}, {cdf_range=}, {n=}, {kwargs=}')
    
    # Check Input Values (ranges)
    if cl_range is not None and cdf_range is None:
        iter_range = cl_range 
    elif cl_range is None and cdf_range is not None:
        iter_range = [-cdf_range[0], -cdf_range[1]]
    elif cl_range is None and cdf_range is None:
        raise ValueError('Must pass cl_range or cd_range to the function')
    else:
        raise ValueError('Can not pass both cl_range and cd_range, must pass one or the other')
    
    # Yield the (cl, cd) tuples
    for cl in linspace(*iter_range, n):
        cd = calculate_cd(cl=cl, **kwargs)
        logger.debug(f'yielding {cl=} and {cd=}')
        yield (sigfig_round(cl), sigfig_round(cd))


def sigfig_round(n: float, sigfigs: int = SIG_FIGS) -> float:
    """Evaluated a Float or Integer to sig figs

    Args:
        n (float || int): Number
        sigfigs (int, optional): Sig figs. Default = SIG_FIGS

    Returns:
        float | int: New number evaluated to sig figs
    """
    
    logging.debug(f'called with {n=}, {sigfigs=}')
    
    if type(n) not in (int, float):
        try:
            n = float(n)
        except ValueError:
            raise ValueError('n must be of type float or int')
    
    return float(f'{n:.{sigfigs}g}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=LOGGING_FORMATTER, 
                        filename=f'{REL_LOGS_DIR}/calculations', filemode='a')
