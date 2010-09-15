import opus.lib.log
log = opus.lib.log.get_logger()

def set_policy_type(sender, instance, **kwargs):
    """Sets the type to the child class's name.

    This is called as a pre_save signal before Policies subclasses are saved.

    """
    log.debug("Setting policy type to: '%s'" % sender.__name__)
    instance.type = sender.__name__
