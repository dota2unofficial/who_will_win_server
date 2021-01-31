from pony.orm import db_session


@db_session
def optional_session(func):
    def wrapped(*args, create_session=False, **kwargs):
        if create_session:
            return func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapped


def batch_postprocessing(func):
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        rearranged = {}

        for entry in result:
            new_entry = {}
            steam_id = None
            for key, value in entry.items():
                m_key = key[0].lower() + key[1:]
                new_entry[m_key] = value

                if m_key == "steamId":
                    steam_id = str(value)
                    new_entry[m_key] = str(value)
            if steam_id:
                if steam_id not in rearranged:
                    rearranged[steam_id] = []
                rearranged[steam_id].append(new_entry)
        # pprint(rearranged)
        return rearranged

    return wrapped


def result_keys_lower_decorator(func):
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        if type(result) == list:
            for obj in result:
                obj_copy = obj.copy()
                for key in obj_copy.keys():
                    val = obj.pop(key)
                    obj[key[0].lower() + key[1:]] = val
        elif type(result) == dict:
            result_copy = result.copy()
            for key in result_copy.keys():
                val = result.pop(key)
                result[key[0].lower() + key[1:]] = val
        return result

    return wrapped
