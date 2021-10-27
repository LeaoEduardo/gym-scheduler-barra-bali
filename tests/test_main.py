import json

import pytest

from src.bot import Bot

CLEARED_SCHEDULE_PATH='tests/resources/cleared_schedule_example.json'
SCHEDULE_PATH='tests/resources/schedule_example.json'
UPDATED_SCHEDULE_PATH='tests/resources/updated_schedule_example.json'
UPDATED_ANY_SCHEDULE_PATH='tests/resources/updated_any_schedule_example.json'
APPENDED_SCHEDULE_PATH='tests/resources/appended_schedule_example.json'

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
    bot.set_tomorrow("Quarta")
    
    md = "*Terça*\n\n*20h*\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n*21h*\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n" 

    assert bot.format_day("today") == md

  def test_format_day_example(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    bot.set_current_hour(20)

    bot.set_today("Terça")
    bot.set_tomorrow("Quarta")
    
    md = "*Terça*\n\n*20h*\nMusculação: Rose\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n*21h*\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n" 

    assert bot.format_day("today") == md

  def test_update_schedule_next_day(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    with open(UPDATED_SCHEDULE_PATH) as file:
      updated_schedule = json.load(file)

    bot.set_today("Quarta")
    bot.set_tomorrow("Quinta")

    bot.set_current_hour(19)

    bot.update_schedule()

    assert bot.schedule == updated_schedule  

  def test_update_schedule_any_day(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    with open(UPDATED_ANY_SCHEDULE_PATH) as file:
      updated_schedule = json.load(file)

    bot.set_today("Sexta")
    bot.set_tomorrow("Sábado")

    bot.set_current_hour(19)

    bot.update_schedule()

    assert bot.schedule == updated_schedule  

  def test_append_to_schedule_today(self):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    bot.set_current_hour(6)
    bot.set_today('Terça')
    bot.set_tomorrow('Quarta')

    with open(APPENDED_SCHEDULE_PATH) as file:
      appoint_schedule = json.load(file)

    bot.append_to_schedule(hour=9, category='musc', name='Jamal', day='hoje')

    assert bot.schedule['today'] == appoint_schedule['today']

  def test_append_to_schedule_tomorrow(self):

    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    bot.set_current_hour(21)
    bot.set_today('Terça')
    bot.set_tomorrow('Quarta')

    with open(APPENDED_SCHEDULE_PATH) as file:
      appoint_schedule = json.load(file)

    bot.append_to_schedule(hour=18, category='aerobio', name='Ben', day='amanha')

    assert bot.schedule['tomorrow'] == appoint_schedule['tomorrow']

  @pytest.mark.parametrize("when", ["hoje", "amanha"])
  def test_error_append_to_schedule_domingo(self, when):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    bot.set_current_hour(10)
    if when == 'hoje':
      bot.set_today('Domingo')
    elif when == 'amanha':
      bot.set_tomorrow('Domingo')

    with pytest.raises(Exception, match='Não há marcação de horário no domingo.'):
      bot.append_to_schedule(hour=20, category='musc', name='Jamal', day=when)

  def test_remove_from_schedule_today(self):

    bot = Bot(schedule_path=APPENDED_SCHEDULE_PATH, download=False)

    with open(SCHEDULE_PATH) as file:
      removed_schedule = json.load(file)

    bot.remove_from_schedule(hour=9, category='musculação', name='Jamal', day='hoje')

    assert bot.schedule['today'] == removed_schedule['today']

  def test_show_next_day(self):

    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    bot.set_current_hour(20)
    bot.set_today('Terça')
    bot.set_tomorrow('Quarta')
    bot.update_schedule()

    md = '*Terça*\n\n' + \
         '*20h*\n' + \
         'Musculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha:\n\n' + \
         '*21h*\n' + \
         'Musculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha:\n\n' + \
         '*Quarta*\n\n' + \
         '*6h*\n' + \
         'Musculação: Jake\nMusculação: Jason\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha:\n\n' + \
         '*7h*\n' + \
         'Musculação: Jack\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha:\n\n' + \
         '*8h*\n' + \
         'Musculação: Arnold\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha:\n\n' + \
        '*9h*\n' + \
         'Musculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha:\n\n' + \
        '*10h*\n' + \
         'Musculação: Joe\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio: Louis\nAeróbio: Max\n' + \
         'Salinha:\n\n' + \
        '*17h*\n' + \
         'Musculação: Ricky\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha: Daniel\n\n' + \
         '*18h*\n' + \
         'Musculação: Ariel\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha:\n\n' + \
        '*19h*\n' + \
         'Musculação: Becky\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha:\n\n' + \
        '*20h*\n' + \
         'Musculação: Mary\nMusculação:\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio: Hamilton\nAeróbio:\n' + \
         'Salinha:\n\n' + \
         '*21h*\n' + \
         'Musculação: Joe\nMusculação: Jason\nMusculação:\nMusculação:\nMusculação:\n' + \
         'Aeróbio:\nAeróbio:\n' + \
         'Salinha:\n\n'

    assert bot.formatted_schedule == md

  @pytest.mark.parametrize("when", ["today", "tomorrow"])
  def test_list_format_day_domingo(self, when:str):
    bot = Bot(schedule_path=SCHEDULE_PATH, download=False)

    bot.set_current_hour(10)
    if when == 'today':
      bot.set_today('Domingo')
      bot.set_tomorrow('Segunda')
    elif when == 'tomorrow':
      bot.set_today('Sábado')
      bot.set_tomorrow('Domingo')
    
    md = ""

    assert bot.format_day(when) == md

  @pytest.mark.parametrize("when", ["today", "tomorrow"])
  def test_list_format_day_sabado(self, when:str):
    bot = Bot(schedule_path=CLEARED_SCHEDULE_PATH, download=False)

    bot.set_current_hour(10)
    if when == 'today':
      bot.set_today('Sábado')
      bot.set_tomorrow('Domingo')
      md = "*Sábado*\n\n*10h*\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n" 
    elif when == 'tomorrow':
      bot.set_today('Sexta')
      bot.set_tomorrow('Sábado')
      md = "*Sábado*\n\n*6h*\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n" + \
            "*7h*\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n" + \
            "*8h*\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n" + \
            "*9h*\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n" + \
            "*10h*\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nMusculação:\nAeróbio:\nAeróbio:\nSalinha:\n\n"
    
    assert bot.format_day(when) == md