import random as r
from aiogram.fsm.state import State, StatesGroup

class Write(StatesGroup):
    group = State()
    word = State()

class ChooseGroup(StatesGroup):
    num = State()

class ChooseWord(StatesGroup):
    num = State()

class TestNew(StatesGroup):
    word = State()

class RepeatOld(StatesGroup):
    word = State()

class StudyOldWord(StatesGroup):
    word = State()

class ChooseOldGroup(StatesGroup):
    num = State()

class ChangeNOROW(StatesGroup):
    num = State()