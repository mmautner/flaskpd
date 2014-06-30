"""
utility functions
"""

import colorsys

def get_n_hex_colors(n=5):
    hsv_tuples = [(x*1.0/n, 0.5, 0.5) for x in range(n)]
    rgb_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples)
    rgb_tuples = map(lambda x: tuple(map(lambda y: int(y * 255),x)),rgb_tuples)
    hex_tuples = map(lambda x: tuple(map(lambda y: chr(y).encode('hex'),x)), rgb_tuples)
    hex_tuples = map(lambda x: "".join(x), hex_tuples)
    return hex_tuples

