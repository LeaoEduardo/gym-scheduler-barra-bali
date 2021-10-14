import pytest

from src.bot import Bot

class Test_Bot:

  def test_reset_hour(self):
    bot = Bot(schedule_path='artifacts/schedule.json', download=False)
    hour_dict = {
      "musc":["Jason", "Jack"],
      "aerobio": ["Mary"],
      "salinha": ["Joe"]
    }

    cleared_dict = {
      "musc":[],
      "aerobio":[],
      "salinha":[]
    }

    bot.reset_hour(hour_dict)

    assert hour_dict == cleared_dict


# class Test_Cloud_Manager:
#   def __init__(self):
#     pass