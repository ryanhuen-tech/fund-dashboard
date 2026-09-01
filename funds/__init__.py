# funds/__init__.py

from funds.fund_z01 import DATA_Z01
from funds.fund_z03 import DATA_Z03
from funds.fund_z04 import DATA_Z04
from funds.fund_z05 import DATA_Z05
from funds.fund_z06 import DATA_Z06
from funds.fund_z07 import DATA_Z07
from funds.fund_z08 import DATA_Z08
from funds.fund_z12 import DATA_Z12
from funds.fund_z13 import DATA_Z13
from funds.fund_z15 import DATA_Z15
from funds.fund_z17 import DATA_Z17
from funds.fund_z18 import DATA_Z18
from funds.fund_z20 import DATA_Z20
from funds.fund_z29 import DATA_Z29
from funds.fund_z31 import DATA_Z31
from funds.fund_z33 import DATA_Z33
from funds.fund_z51 import DATA_Z51
from funds.fund_z52 import DATA_Z52
from funds.fund_z69 import DATA_Z69
from funds.fund_z77 import DATA_Z77
from funds.fund_zP4 import DATA_ZU6
from funds.fund_zP4 import DATA_ZP4

ALL_FUNDS = {
    **DATA_Z01,
    **DATA_Z03,
    **DATA_Z04,
    **DATA_Z05,
    **DATA_Z06,
    **DATA_Z07,
    **DATA_Z08,
    **DATA_Z13,
    **DATA_Z15,
    **DATA_Z17,
    **DATA_Z18,
    **DATA_Z20,
    **DATA_Z29,
    **DATA_Z31,
    **DATA_Z33,
    **DATA_Z51,
    **DATA_Z52,
    **DATA_Z69,
    **DATA_Z77,
    **DATA_ZU6,
    **DATA_ZP4,
}
