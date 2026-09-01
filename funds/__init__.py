# funds/__init__.py

from funds.fund_z03 import DATA_Z03
from funds.fund_z07 import DATA_Z07
from funds.fund_z18 import DATA_Z18
from funds.fund_z20 import DATA_Z20
from funds.fund_z33 import DATA_Z33
from funds.fund_z77 import DATA_Z77
from funds.fund_z31 import DATA_Z31
from funds.fund_z05 import DATA_Z05
from funds.fund_z06 import DATA_Z06
from funds.fund_zP4 import DATA_ZP4

ALL_FUNDS = {
    **DATA_Z03,
    **DATA_Z07,
    **DATA_Z18,
    **DATA_Z20,
    **DATA_Z33,
    **DATA_Z77,
    **DATA_Z31,
    **DATA_Z05,
    **DATA_Z06,
    **DATA_ZP4,
}
