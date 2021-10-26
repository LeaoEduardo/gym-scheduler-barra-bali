from datetime import datetime
import pytz
import json
from pprint import pprint
from copy import deepcopy

from src import BOT_TOKEN, WEBHOOK, PORT, TIMEZONE, days_of_the_week, translate
from src.cloud_manager import CloudManager

class Bot:

    def __init__(self, schedule_path='/app/schedule.json', download=True):
        self.schedule_path = schedule_path
        if download:
            self.cm = CloudManager()
            self.cm.download(destination_file_name=schedule_path)
        with open(schedule_path) as file:
            self.schedule = json.load(file)
    
    def start(self):
        now = datetime.now(tz=pytz.timezone(TIMEZONE))
        self.current_hour = now.hour
        self.today = days_of_the_week[now.weekday()]
        self.tomorrow = days_of_the_week[now.weekday()+1]
        self.update_schedule()

    def set_schedule(self, schedule):
        self.schedule = schedule

    def set_current_hour(self, hour):
        self.current_hour = hour

    def set_today(self, day):
        self.today = day
    def set_tomorrow(self, day):
        self.tomorrow = day

    def update_schedule(self):
        """Update schedule data in case of day turning"""
        # verify if the day has changed
        today = list(days_of_the_week.keys())[list(days_of_the_week.values()).index(self.today)]
        if today > int(self.schedule["weekday"]):
            if today - 1 == int(self.schedule["weekday"]):
                self.schedule["today"] = deepcopy(self.schedule["tomorrow"])
            else:
                self.reset_day(self.schedule["today"])
            self.reset_day(self.schedule["tomorrow"])
            self.schedule["weekday"] = str(today)

        # verify if the current hour is past the schedule
        for hour in self.schedule["today"]:
            if self.current_hour >= int(hour):
                self.reset_hour(self.schedule["today"][hour])
            else:
                break

        self.formatted_schedule = self.format_schedule()

        # if current_hour is higher than 16 it should show tomorrow on list_schedule
        if self.current_hour >= 16:
            self.show_next_day(True)
    
    #by default show only today
    def format_schedule(self):
        schedule = self.format_day("today")
        return schedule
    
    def format_day(self, day):
        if day == "today":
            if self.today == 'Domingo': return ''
            schedule = f"*{self.today}*\n\n"
        elif day == "tomorrow":
            if self.tomorrow == 'Domingo': return ''
            schedule = f"*{self.tomorrow}*\n\n"
        for hour in self.schedule[day]:
            if int(hour) >= self.current_hour or day =='tomorrow':
                schedule += f"*{hour}h*\n"
                schedule += self.format_list(day,hour,'musc')
                schedule += self.format_list(day,hour,'aerobio')
                schedule += self.format_list(day,hour,'salinha')
                schedule += '\n'
        return schedule

    def format_list(self, day, hour, category):
        formatted_list = ''
        i = 0
        if category == 'musc':
            for m in self.schedule[day][hour][category]:
                formatted_list += f'Musculação: {m}\n'
                i += 1
            for _ in range(i,5):
                formatted_list += f'Musculação:\n'

        elif category == 'aerobio':
            for a in self.schedule[day][hour][category]:
                formatted_list += f'Aeróbio: {a}\n'
                i += 1
            for _ in range(i,2):
                formatted_list += f'Aeróbio:\n'

        elif category == 'salinha':
            for a in self.schedule[day][hour][category]:
                formatted_list += f'Salinha: {a}\n'
                i += 1
            for _ in range(i,1):
                formatted_list += f'Salinha:\n'
        return formatted_list

    def reset_day(self, day_dict):
        for hour in day_dict:
            self.reset_hour(day_dict[hour])
    
    def reset_hour(self, hour_dict):
        for l in hour_dict:
            hour_dict[l].clear()

    def show_next_day(self, show: bool):
        if show:
            self.formatted_schedule += self.format_day("tomorrow")

    def clean_input(self, hour, day, category):
        if type(hour) == int:
                hour = str(hour)
        if day.lower() in translate:
            day = translate[day.lower()]
        if category.lower() in translate:
            category = translate[category.lower()]
        return hour, day, category

    def append_to_schedule(self, name, hour, day='today', category='musc'):
        hour, day, category = self.clean_input(hour, day, category)
        if (day == 'today' and self.today == 'Domingo') or (day == 'tomorrow' and self.tomorrow == 'Domingo'):
            raise Exception('Não há marcação de horário no domingo.')
        if hour not in self.schedule[day] or (self.current_hour >= int(hour) and day=="today"):
            raise Exception('Horário inválido. Tente novamente.')
        self.schedule[day][hour][category].append(name)
    
    def remove_from_schedule(self, name, hour, day='today', category='musc'):
        hour, day, category = self.clean_input(hour, day, category)
        if hour not in self.schedule[day]:
            raise Exception('Horário inválido. Tente novamente.')
        self.schedule[day][hour][category].remove(name)
       
    def save_schedule(self, dest='schedule_example.json'):
        with open(self.schedule_path, 'w') as fp:
            json.dump(obj=self.schedule, fp=fp)
        self.cm.upload(source_file_name=self.schedule_path, destination_blob_name=dest)
 
    def list_schedule(self, update, context):
        """Send a message when the command /horarios is issued."""
        self.update_schedule()
        update.message.reply_text(self.formatted_schedule, parse_mode='MarkdownV2')

    def schedule_appointment(self, update, context):
        """Send a message when the command /marcar is issued."""
        if update.message:
            username = f'{update.message.from_user.first_name} {update.message.from_user.last_name}'
        else:
            return
        try:
            args = tuple(context.args)
            if len(args) <= 0 or len(args) > 3:
                raise ValueError()
        except ValueError:
            update.message.reply_text(f"Argumentos inválidos! Por favor, digite seguindo um desse padrões:\n /marcar Horario Dia Tipo\n /marcar Horario Dia (Tipo será 'musculação')\n /marcar Horario (Tipo sera 'musculação' e Dia será 'hoje')")
            return
        try:
            self.append_to_schedule(username, *args)
        except Exception as exc:
            update.message.reply_text(f"Erro: {exc.args[0]}")
            return
        # self.save_schedule()
        #TODO parameterize day and category in answer
        update.message.reply_text(f'Marcado {username} para musculação hoje as {args[0]} horas!')

    def remove_appointment(self, update, context):
        """Send a message when the command /desmarcar is issued."""
        if update.message:
            username = f'{update.message.from_user.first_name} {update.message.from_user.last_name}'
        else:
            return
        try:
            args = tuple(context.args)
            if len(args) <= 0 or len(args) > 3:
                raise ValueError()
        except ValueError:
            update.message.reply_text(f"Argumentos inválidos! Por favor, digite seguindo um desse padrões:\n /desmarcar Horario Dia Tipo\n /desmarcar Horario Dia (Tipo será 'musculação')\n /desmarcar Horario (Tipo sera 'musculação' e Dia será 'hoje')")
            return
        try:
            self.remove_from_schedule(username, *args)
        except Exception as exc:
            update.message.reply_text(f"Erro: {exc.args[0]}")
            return
        # self.save_schedule()
        #TODO parameterize day in answer
        update.message.reply_text(f'Desmarcado {username} para musculação hoje as {args[0]} horas!')

    def fallback(self, update, context):
        """Default message if command is not understood"""
        update.message.reply_text('Não entendi esse comando. Tente novamente.')