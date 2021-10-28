from datetime import datetime
import pytz
import json
from pprint import pprint
from copy import deepcopy

from src import BOT_TOKEN, WEBHOOK, PORT, TIMEZONE, days_of_the_week, translate, inverse_translate
from src.cloud_manager import CloudManager

MUSC_LIMIT=5
AER_LIMIT=2
SALIN_LIMIT=1

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
        self.temp_hour = 0
        self.temp_day = ''
        self.temp_category = ''

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
                if (self.today == 'Sábado' and day=='today') or \
                    (self.tomorrow=='Sábado' and day=='tomorrow'):
                    if int(hour) <=10:
                        schedule += self.format_hour(day,hour)
                else:
                    schedule += self.format_hour(day,hour)
        return schedule

    def format_hour(self, day, hour):
        formatted_hour = ''
        formatted_hour+= f"*{hour}h*\n" \
                        + self.format_list(day,hour,'musc') \
                        + self.format_list(day,hour,'aerobio') \
                        + self.format_list(day,hour,'salinha') \
                        + '\n'
        return formatted_hour

    def format_list(self, day, hour, category):
        formatted_list = ''
        i = 0
        if category == 'musc':
            for m in self.schedule[day][hour][category]:
                formatted_list += f'Musculação: {m}\n'
                i += 1
            for _ in range(i,MUSC_LIMIT):
                formatted_list += f'Musculação:\n'

        elif category == 'aerobio':
            for a in self.schedule[day][hour][category]:
                formatted_list += f'Aeróbio: {a}\n'
                i += 1
            for _ in range(i,AER_LIMIT):
                formatted_list += f'Aeróbio:\n'

        elif category == 'salinha':
            for a in self.schedule[day][hour][category]:
                formatted_list += f'Salinha: {a}\n'
                i += 1
            for _ in range(i,SALIN_LIMIT):
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
        else:
            raise Exception('Dia inválido\. Escolha uma das opções:\n_hoje_, _hj_, _amanhã_ ou _amn_')
        if category.lower() in translate:
            category = translate[category.lower()]
        else: 
            raise Exception('Categoria inválida\. Escolha uma das opções:\n_musculação_, _musc_, _aeróbio_, _aer_, _salinha_ ou _sala_')
        return hour, day, category

    def prepare_schedule_operation(self, hour, day, category):
        try:
            hour, day, category = self.clean_input(hour, day, category)
            self.temp_hour, self.temp_day, self.temp_category = hour, day, category
        except Exception as exc:
            raise Exception(exc)
        if (day == 'today' and self.today == 'Domingo') or (day == 'tomorrow' and self.tomorrow == 'Domingo'):
            raise Exception('Não há marcação de horário no domingo\.')
        if (day == 'today' and self.today == 'Sábado') or (day == 'tomorrow' and self.tomorrow == 'Sábado') and int(hour) > 10:
            raise Exception('Horário inválido\. Tente novamente\.')
        if hour not in self.schedule[day] or (self.current_hour >= int(hour) and day=="today"):
            raise Exception('Horário inválido\. Tente novamente\.')
        return hour, day, category

    def is_full(self,hour,day,category):
        if len(self.schedule[day][hour][category])==MUSC_LIMIT and category=='musc':
            return True
        elif len(self.schedule[day][hour][category])==AER_LIMIT and category=='aerobio':
            return True
        elif len(self.schedule[day][hour][category])==SALIN_LIMIT and category=='salinha':
            return True
        return False

    def append_to_schedule(self, name, hour, day='hoje', category='musc', other=''):
        try:
            hour, day, category = self.prepare_schedule_operation(hour, day, category)
        except Exception as exc:
            raise Exception(exc)
        if self.is_full(hour, day, category):
            raise Exception('Horário esgotado\. Tente novamente\.')
        if other != '':
            self.temp_name = other
            self.schedule[day][hour][category].append(other)
        else:   
            self.temp_name = name 
            self.schedule[day][hour][category].append(name)

    def remove_from_schedule(self, name, hour, day='hoje', category='musc', other=''):
        try:
            hour, day, category = self.prepare_schedule_operation(hour, day, category)
        except Exception as exc:
            raise Exception(exc)
        try:
            if other != '':
                self.temp_name = other
                self.schedule[day][hour][category].append(other)
            else:
                self.temp_name = name
                self.schedule[day][hour][category].remove(name)
        except Exception:
            raise Exception("Remoção inválida: marcação não encontrada\.")
       
    def save_schedule(self, dest='schedule.json'):
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
            if len(args) <= 0 or len(args) > 4:
                raise ValueError()
        except ValueError:
            update.message.reply_text(f"Argumentos inválidos! Por favor, digite seguindo um desse padrões:\n /marcar Horario Dia Tipo Nome\n /marcar Horario Dia Tipo (Nome será o seu)\n /marcar Horario Dia (Tipo será 'musculação')\n /marcar Horario (Tipo sera 'musculação' e Dia será 'hoje')")
            return
        try:
            self.append_to_schedule(username, *args)
        except Exception as exc:
            msg = str(exc.args[0])
            update.message.reply_text(f'Erro: {msg}', parse_mode='MarkdownV2')
            return
        self.save_schedule()
        update.message.reply_text(f'Marcado {self.temp_name} para {inverse_translate[self.temp_category]} {inverse_translate[self.temp_day]} às {self.temp_hour} horas!')

    def remove_appointment(self, update, context):
        """Send a message when the command /desmarcar is issued."""
        if update.message:
            username = f'{update.message.from_user.first_name} {update.message.from_user.last_name}'
        else:
            return
        try:
            args = tuple(context.args)
            if len(args) <= 0 or len(args) > 4:
                raise ValueError()
        except ValueError:
            update.message.reply_text(f"Argumentos inválidos! Por favor, digite seguindo um desse padrões:\n /desmarcar Horario Dia Tipo Nome\n /desmarcar Horario Dia Tipo (Nome será o seu)\n /desmarcar Horario Dia (Tipo será 'musculação')\n /desmarcar Horario (Tipo sera 'musculação' e Dia será 'hoje')")
            return
        try:
            self.remove_from_schedule(username, *args)
        except Exception as exc:
            msg = str(exc.args[0])
            update.message.reply_text(f'Erro: {msg}', parse_mode='MarkdownV2')
            return
        self.save_schedule()
        update.message.reply_text(f'Desmarcado {self.temp_name} para {inverse_translate[self.temp_category]} {inverse_translate[self.temp_day]} às {self.temp_hour} horas!')

    def fallback(self, update, context):
        """Default message if command is not understood"""
        update.message.reply_text('Não entendi esse comando. Tente novamente.')