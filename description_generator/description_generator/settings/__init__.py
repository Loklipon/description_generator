from .base import *

if ENVIRONMENT == 'prod':
    from .prod import *
elif ENVIRONMENT == 'local':
    from .local import *