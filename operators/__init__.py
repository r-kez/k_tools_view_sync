from .op_sync_operators import classes as sync_operators
from .op_auto_master    import classes as auto_master
from .op_lock_operators import classes as lock_operators
from .op_layout_operators import classes as layout_operators


classes = (
    *sync_operators,
    *auto_master,
    *lock_operators,
    *layout_operators,
)