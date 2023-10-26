from pikepdf import Dictionary, Name

def get_inheritable(dic:Dictionary, name:Name):
    """
    Look up an inheritable property through the chain of inheritance
    """
    if name in dic:
        return dic[name]
    elif Name.Parent in dic:
        return get_inheritable(dic.Parent, name)
    else:
        return None