""" """


def pt_func(variable_name: str):
    """
    Pass through function.
    """

    def func(vars):
        return vars[variable_name]

    return func
