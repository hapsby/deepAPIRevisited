import re


def get_description_from_name(name):
    name = re.sub(r'([A-Z])', ' \\1', name)
    return name.replace('_', ' ').strip()


def get_module_of_api_call(api_call):
    words = re.findall(r"^[^.]+", api_call)
    return words[0]