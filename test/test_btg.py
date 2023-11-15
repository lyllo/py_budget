import os

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

import sys
sys.path.insert(1, ROOT_DIR)

import btg

def test_obter_numero_mes():
    assert btg.obter_numero_mes('Jan') == 1