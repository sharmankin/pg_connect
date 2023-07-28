import dotenv as _de
from .connections import *

_de.load_dotenv(
    _de.find_dotenv('project.env', raise_error_if_not_found=True)
)
