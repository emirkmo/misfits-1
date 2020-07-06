from copy import deepcopy

def get_parameters_from_header(obj, header):

    name = obj.NAME
    params = {p:header['%s.%s'%(name,p)] for p in obj.PARAMETERS}
    return params

def update_parameter_header(obj, header):

    name = obj.NAME
    params = {'%s.%s'%(name,p):deepcopy(getattr(obj,p)) for p in obj.PARAMETERS}
    header.update(params)
