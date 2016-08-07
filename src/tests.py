import pytest
from army import Army
from ruler import Ruler
from soldier import Soldier


class TestSoldier(object):
    def __init__(self):
        self.soldier = Soldier(1, 1, 1, 1, 1, "1")

    def test_age(self):
        assert self.soldier.will_retire(1)

