import json

import pytest

from src.bot import Bot

CLEARED_SCHEDULE_PATH='tests/resources/cleared_schedule_example.json'
SCHEDULE_PATH='tests/resources/schedule_example.json'
UPDATED_SCHEDULE_PATH='tests/resources/updated_schedule_example.json'
UPDATED_ANY_SCHEDULE_PATH='tests/resources/updated_any_schedule_example.json'


class Test_Bot:

  def test_reset_hour(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)
    with open(SCHEDULE_PATH) as file:
      schedule = json.load(file)

    with open(CLEARED_SCHEDULE_PATH) as file:
      cleared_schedule = json.load(file)

    hour_dict = schedule["today"]["6"]

    cleared_dict = cleared_schedule["today"]["6"]

    bot.reset_hour(hour_dict)

    assert hour_dict == cleared_dict

  def test_reset_day(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)
    with open(SCHEDULE_PATH) as file:
      schedule = json.load(file)

    with open(CLEARED_SCHEDULE_PATH) as file:
      cleared_schedule = json.load(file)

    day_dict = schedule["today"]

    cleared_dict = cleared_schedule["today"]

    bot.reset_day(day_dict)

    assert day_dict == cleared_dict

  def test_format_list_empty(self):
    bot = Bot(schedule_path=CLEARED_SCHEDULE_PATH, download=False)
    
    md = "Musculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n" 
    
    assert bot.format_list("today","6","musc") == md
  
  def test_format_list_example(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)
    
    md = "Musculação: Jake\nMusculação: Jason\nMusculação:\nMusculação:\nMusculação:\n" 

    assert bot.format_list("today","6","musc") == md

  def test_format_day_empty(self):
    bot = Bot(schedule_path=CLEARED_SCHEDULE_PATH, download=False)

    bot.set_current_hour(20)

    bot.set_today("Terça")
    
    md = "**Terça**\n\n**20h**\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n**21h**\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n" 
    
    print(md)
    print("---")
    print(bot.format_day("today"))
    print("---")

    assert bot.format_day("today") == md

  def test_format_day_example(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    bot.set_current_hour(20)

    bot.set_today("Terça")
    
    md = "**Terça**\n\n**20h**\nMusculação: Rose\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n**21h**\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n" 
    
    print(md)
    print("---")
    print(bot.format_day("today"))
    print("---")

    assert bot.format_day("today") == md

  def test_update_schedule_next_day(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    with open(UPDATED_SCHEDULE_PATH) as file:
      updated_schedule = json.load(file)

    bot.set_today("Quarta")

    bot.set_current_hour(19)

    bot.update_schedule()

    assert bot.schedule == updated_schedule  

  def test_update_schedule_any_day(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    with open(UPDATED_ANY_SCHEDULE_PATH) as file:
      updated_schedule = json.load(file)

    bot.set_today("Sexta")

    bot.set_current_hour(19)

    bot.update_schedule()

    assert bot.schedule == updated_schedule  