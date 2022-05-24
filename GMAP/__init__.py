r"""

  .-_'''-.                ,---.    ,---.   ____   .-------.  
 '_( )_   \               |    \  /    | .'  __ `.\  _(`)_ \ 
|(_ o _)|  '              |  ,  \/  ,  |/   '  \  \ (_ o._)| 
. (_,_)/___|   _ _    _ _ |  |\_   /|  ||___|  /  |  (_,_) / 
|  |  .-----. ( ' )--( ' )|  _( )_/ |  |   _.-`   |   '-.-'  
'  \  '-   .'(_{;}_)(_{;}_) (_ o _) |  |.'   _    |   |      
 \  `-'`   |  (_,_)--(_,_)|  (_,_)  |  ||  _( )_  |   |      
  \        /              |  |      |  |\ (_ o _) /   )      
   `'-...-'               '--'      '--' '.(_,_).'`---'      


Welcome to the G-MAP package. Currently, this is a work in progress. The
following options are available:

    GMAP
    GMAP help
prints this help.

    GMAP help [program]
prints the help for the requested program

    GMAP AIM
This program will create the required files for calculating infrared spectra.

    GMAP GEM
This program will create the required files for calculating electronic spectra.

"""



from .src.programs import AIM
from .src.programs import GEM

alltools = {
    "AIM": AIM,
    "GEM": GEM
}
