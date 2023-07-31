import sys

import dotenv as _de
from .connections import *
from .extras import *
import os

_de.load_dotenv(
    _de.find_dotenv('project.env', raise_error_if_not_found=True)
)

if not os.getenv('PG_NODE'):
    print('Please add `PG_NODE` into your project.env')
    sys.exit(1)
