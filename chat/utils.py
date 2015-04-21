# -*- coding: utf-8 -*-
import random
import string


def get_random_string(length=12, allowed_chars=string.hexdigits):
    return ''.join(random.choice(allowed_chars) for i in range(length))
