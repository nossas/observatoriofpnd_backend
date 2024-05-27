import re

camel_to_snake_pattern = re.compile(r'(?<!^)(?=[A-Z])')

def camel_to_snake(word):
    return camel_to_snake_pattern.sub('_', word).lower()
    
def snake_to_camel(word):
        parts = word.split('_')
        return parts[0] + ''.join(x.capitalize() or '_' for x in parts[1:])


def rename_dict_keys(dict_to_rename, function):
    keys = list(dict_to_rename.keys())
    for key in keys:
        value = dict_to_rename.pop(key)
        if type(value) == dict:
            value = rename_dict_keys(value, function)
        if type(value) == list:
            temp_list = []
            for i in value:
                if type(i) not in [list, dict]:
                    temp_list.append(i)
                else:
                    if type(i) == dict:
                        temp_list.append(rename_dict_keys(i, function))
                    elif type(i) == list:
                        temp_list.append(i)
            value = temp_list
        dict_to_rename[function(key)] = value
    return dict_to_rename

def camel_keys_to_snake(dict_to_rename):
    return rename_dict_keys(dict_to_rename, camel_to_snake)    

def snake_keys_to_camel(dict_to_rename):
    return rename_dict_keys(dict_to_rename, snake_to_camel)


