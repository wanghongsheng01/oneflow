global_storage = {}


def Get(name):
    return global_storage.get(name).numpy()


def Setter(name):
    global global_storage

    def _set(x):
        global_storage[name] = x

    return _set
