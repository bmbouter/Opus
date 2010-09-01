"""
Various tools to make writing a driver easier.
"""

def filter_images(images, filter_dict):
    """Takes a list of images and returns the subset of that list that meet the filter_dict's criteria."""
    filter_function = lambda image: \
        ("id" not in filter_dict or filter_dict["id"] == image.id) and \
        ("owner_id" not in filter_dict or filter_dict["owner_id"] == image.id) and \
        ("name" not in filter_dict or filter_dict["name"] == image.id) and \
        ("architecture" not in filter_dict or filter_dict["architecture"] == image.id)
    return filter(filter_function, images)

def filter_instances(instances, filter_dict):
    """Takes a list of instances and returns the subset of that list that meets the filter_dict's criteria."""
    filter_function = lambda instance: \
        ("id" not in filter_dict or filter_dict["id"] == instance.id) and \
        ("state" not in filter_dict or filter_dict["state"] == instance.state)
    return filter(filter_function, instances)

def filter_realms(realms, filter_dict):
    """Takes a list of realms and returns the subset of that list that meets the filter_dict's criteria."""
    filter_function = lambda realm: \
        ("id" not in filter_dict or filter_dict["id"] == realm.id)
    return filter(filter_function, realms)
