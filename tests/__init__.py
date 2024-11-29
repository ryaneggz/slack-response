
def disabled(f):
    def _decorator():
        print(f.__name__ + ' has been disabled')
    return _decorator