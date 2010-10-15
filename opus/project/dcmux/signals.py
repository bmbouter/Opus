import opus.lib.log
log = opus.lib.log.get_logger()

def set_policy_type(sender, instance, **kwargs):
    """Sets the type to the child class's name.

    This is called as a pre_save signal before Policies subclasses are saved.

    """
    instance.type = sender.__name__
