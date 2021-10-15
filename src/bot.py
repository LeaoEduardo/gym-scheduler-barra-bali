import datetime
import json
from pprint import pprint
from copy import deepcopy

from src import BOT_TOKEN, WEBHOOK, PORT, days_of_the_week
from src.cloud_manager import CloudManager

class Bot:

    def __init__(self, schedule_path='/app/schedule.json', download=True):
        if download:
            self.cm = CloudManager()
            self.cm.download(destination_file_name=schedule_path)
        with open(schedule_path) as file:
            self.schedule = json.load(file)
    
    def start(self):
        self.current_hour = datetime.datetime.now().hour
        self.today = days_of_the_week[datetime.datetime.today().weekday()]
        self.tomorrow = days_of_the_week[datetime.datetime.today().weekday()+1]
        self.update_schedule()
        self.formatted_schedule = self.format_schedule()

    def set_schedule(self, schedule):
        self.schedule = schedule

    def set_current_hour(self, hour):
        self.current_hour = hour

    def set_today(self, day):
        self.today = day

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
            self.show_next_day(False)
            self.schedule["weekday"] = str(today)

        # verify if the current hour is past the schedule
        for hour in self.schedule["today"]:
            if self.current_hour >= int(hour):
                self.reset_hour(self.schedule["today"][hour])
            else:
                break

        # if current_hour is higher than 16 it should show tomorrow on list_schedule
        if self.current_hour >= 16:
            self.show_next_day(True)
    
    #by default show only today
    def format_schedule(self):
        schedule = self.format_day("today")
        return schedule
    
    def format_day(self, day):
        if day == "today":
            schedule = f"**{self.today}**\n\n"
        elif day == "tomorrow":
            schedule = f"**{self.tomorrow}**\n\n"
        for hour in self.schedule[day]:
            if int(hour) >= self.current_hour:
                schedule += f"**{hour}h**\n"
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
        pass
        # if show:
        #     self.formatted_schedule += self.format_day(self.tomorrow)

    def list_schedule(self, update, context):
        """Send a message when the command /horarios is issued."""
        self.update_schedule()
        update.message.reply_text(self.formatted_schedule, parse_mode='Markdown')

    # def schedule_musc(self, update, context):
    #     """Send a message when the command /marcar is issued."""
    #     try:
    #         name, hour = tuple(context.args)
    #         hour = int(hour)
    #     except:
    #         update.message.reply_text(f"Argumentos inválidos por favor digite:\n /marcar_musc SeuNome Horario.")
    #         return
    #     today_hours_dictionary[hour]['musc'].append(name)
    #     print(today_hours_dictionary)

    #     update.message.reply_text(f'Marcado {name} para musculação hoje as {hour} horas!')

    def fallback(self, update, context):
        """Default message if command is not understood"""
        update.message.reply_text('Não entendi esse comando. Tente novamente.')