import sys

import dotenv as _de
from .connections import *
from .extras import *
import os
from config_reader import project_root

p_env = project_root / 'project.env'

assert p_env.exists()

_de.load_dotenv(
    p_env
)

if not os.getenv('PG_NODE'):
    print('Please add `PG_NODE` into your project.env')
    sys.exit(1)
