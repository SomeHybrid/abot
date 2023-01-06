import random


class Colors:
    ERROR = 0xFF0000

    def rand():
        return int("%06x" % random.randint(0, 0xFFFFFF), 16)
