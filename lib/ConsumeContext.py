from ApiMap import ApiMap


class ConsumeContext:
    """ This keeps track of the context (currently existing symbols, etc...) while walking through an AST. """

    def __init__(self, dir_path):
        self.api_map = ApiMap()
        self.external_modules = {}
        self.dir_path = dir_path
        self.class_names = []

    def get_function_name(self, node_name):
        if len(self.class_names) == 0:
            return node_name
        return "::".join(self.class_names) + "::" + node_name




