from .op_sync_operators import classes as sync_operators
from .op_auto_master    import classes as auto_master
from .op_lock_operators import classes as lock_operators


classes = (
    *sync_operators,
    *auto_master,
    *lock_operators,
)