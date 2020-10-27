import typing
from statistics import median
from typing import List, Any

from datetime import datetime as dt
from models.SequenceModel import SequenceModel

EMOTE_DESPERATE_ENUM = 2
FB_DEATH_ENUM = 18
EMOTE_EVT_ENUM = 24
MONEY_RATE_ENUM = 33
FOOD_AV_ENUM = 32

## @class SimpleDeathPredModel
# Returns the number of deaths caused by hunger, or None if no deaths due to hunger
# @param levels: Levels applicable for model

class SimpleDeathPredModel(SequenceModel):
    def __init__(self, levels: typing.List[int] = []):
        super().__init__(levels)

    def collect_deaths(self, events):
        fb_sess_cache_list = list()
        for row in reversed(events):
            if row['event_custom'] == FB_DEATH_ENUM:
                fb, sess = row['event_data_complex']['farmbit'][2], row['sess_id']
                dh_time = self.get_utc(row['client_time'])
                x = {"name": fb, "sess_id": sess, "dh_time": dh_time}
                if not len(fb_sess_cache_list):
                    fb_sess_cache_list.append(x)
                else:
                    dupes = set([el != x for el in fb_sess_cache_list])
                    unlogged = False if len(list(dupes)) > 1 else list(dupes)[0]
                    if unlogged:
                        fb_sess_cache_list.append(x)
        return fb_sess_cache_list

    def get_utc(self, data):
        dt_string = '%Y-%m-%d %H:%M:%S'
        return dt.strptime(data, dt_string).timestamp()

    def _eval(self, events, verbose=False):
        assert events
        spdh_cnt = 0
        fb_sess_cache_list = list()
        for row in reversed(events):
            if row['event_custom'] == FB_DEATH_ENUM:
                fb = row['event_data_complex']['farmbit'][2]
                sess = row['sess_id']
                x = {"name": fb, "sess_id": sess}
                if not len(fb_sess_cache_list):
                    fb_sess_cache_list.append(x)
                else:
                    dupes = set([el != x for el in fb_sess_cache_list])
                    unlogged = False if len(list(dupes)) > 1 else list(dupes)[0]
                    if unlogged:
                        fb_sess_cache_list.append(x)
            if row['event_custom'] == EMOTE_EVT_ENUM:
                if row['event_data_complex']['emote_enum'] == EMOTE_DESPERATE_ENUM:
                    fb = row['event_data_complex']['farmbit'][2]
                    sess = row['sess_id']
                    x = {"name": fb, "sess_id": sess}
                    for i, el in enumerate(fb_sess_cache_list):
                        if x == el:
                            spdh_cnt += 1
        if not len(fb_sess_cache_list):
            return None
        else:
            return spdh_cnt

## @class SimpleMoneyDeathPredModel
# Returns a dictionary of money data X seconds before deaths, or None if no logs were found in the timeframes
# @param levels: Levels applicable for model, tbd: Time before death to collect money logs
class SimpleMoneyDeathPredModel(SimpleDeathPredModel):

    def __init__(self, levels: typing.List[int] = [], tbd=60):
        self.tbd = tbd
        super().__init__(levels)

    # money
    def _eval(self, events, verbose=False):
        assert events
        money_log = list()
        fb_sess_cache_list = self.collect_deaths(events)
        for el in fb_sess_cache_list:
            for row in events:
                if row['event_custom'] == MONEY_RATE_ENUM:
                    log_time = self.get_utc(row['client_time'])
                    if (log_time < el['dh_time']) and (log_time > el['dh_time'] - self.tbd):
                        money_log.append(row['event_data_complex']['money'])
        # max, avg, min, median
        if not len(money_log):
            return {"max": None, "avg": None, "min": None,
                    "median": None}
        return {"max": max(money_log), "avg": sum(money_log) / len(money_log), "min": min(money_log),
                "median": median(money_log)}

## @class SimpleFoodDeathPredModel
# Returns a dictionary of food data X seconds before deaths, or None if no logs were found in the timeframes
# @param levels: Levels applicable for model, tbd: Time before death to collect food logs
class SimpleFoodDeathPredModel(SimpleDeathPredModel):

    def __init__(self, levels: typing.List[int] = [], tbd=60):
        self.tbd = tbd
        super().__init__(levels)

    def _eval(self, events, verbose=False):
        assert events
        food_log = list()
        fb_sess_cache_list = self.collect_deaths(events)
        for el in fb_sess_cache_list:
            for row in events:
                if row['event_custom'] == FOOD_AV_ENUM:
                    log_time = self.get_utc(row['client_time'])
                    if (log_time < el['dh_time']) and (log_time > (el['dh_time'] - self.tbd)):
                        food_log.append(row['event_data_complex']['food'])
        # max, avg, min, median
        if not len(food_log):
            return {"max": None, "avg": None, "min": None,
                    "median": None}
        return {"max": max(food_log) or 0, "avg": sum(food_log) / len(food_log), "min": min(food_log),
                "median": median(food_log)}

#     def all_hunger_death_eval(self):
#         sessions = list(self.df['sess_id'].drop_duplicates())
#         res = True
#         for sess in sessions:
#             self.hunger_death_sess_eval(sess)
#
#     def food_money_death_eval(self, event: int):
#         self.filtered_df = self.filtered_df.append(
#             self.df.query(f'(event_custom == {event})'))
#         (usr_val, cat) = (self.money, "money") if event == MONEY_RATE_ENUM else (self.food, "food")
#         for x in self.farmBits.values():
#             timeslice = self.filtered_df.query(
#                 f'(event_custom == {event}) & (utc_time_secs < {x.dh_time}) & (utc_time_secs > {x.hg_time})')
#             if len(timeslice.index) > 0:
#                 for (key, data) in zip(timeslice['utc_time_secs'], timeslice['event_data_complex']):
#                     if event == MONEY_RATE_ENUM:
#                         x.money_data[key] = data
#                     else:
#                         x.food_data[key] = data
#
#                     if data[cat] < usr_val: return False
#         return True
#
#     def hunger_death_sess_eval(self, sess: int):
#         for i, x in enumerate(self.filtered_df[(self.filtered_df['sess_id'] == sess)].itertuples()):
#             farmbit = x.event_data_complex['farmbit'][2]
#             key = f'{sess}_{farmbit}'
#             if x.event_custom == EMOTE_EVT_ENUM:
#                 self.farmBits[key] = self.FarmbitDeaths(x)
#             elif key not in self.farmBits.keys():
#                 raise Exception(
#                     f'Farmbit {farmbit} died without getting hungry. There\'s a bug, honey')
#             else:
#                 self.farmBits[key].set_dh(x)
#
#     def process_df(self):
#         date_string = '%Y-%m-%d %H:%M:%S'
#         if set(self.df_filter).issubset(set(self.df.columns)):
#             self.df = self.df.drop(columns=self.df_filter, axis=0)
#             self.df['utc_time_secs'] = self.df['client_time'].apply(
#                 lambda x: dt.strptime(x, date_string).timestamp())
#             self.process_hunger_df()
#
#     def process_hunger_df(self):
#         self.filtered_df = self.df.query(self.query)
#         self.preprocess_df()
#         temp = self.filtered_df[
#             (self.filtered_df['event_custom'] == 18) |
#             (self.filtered_df['event_custom'] == 24) &
#             ((self.filtered_df['emote_enum'] == 7) |
#              (self.filtered_df['emote_enum'] == 2))]
#         self.filtered_df = pd.DataFrame()
#         self.filtered_df = temp
#
#     def preprocess_df(self):
#         self.thresh_df = pd.DataFrame(
#             list(self.filtered_df['event_data_complex'].values))
#         farmbit = ['tile.tx', 'tile.ty', 'name', 'job_state',
#                    'job_type', 'fullness', 'energy', 'joy', 'fulfillment']
#         self.filtered_df['n_row'] = [i for i in range(len(self.filtered_df.index))]
#         self.thresh_df['n_row'] = [i for i in range(len(self.thresh_df.index))]
#
#         self.thresh_df[farmbit] = pd.DataFrame(
#             self.thresh_df.farmbit.tolist(), index=self.thresh_df.index)
#         self.filtered_df = self.filtered_df.merge(
#             self.thresh_df, on=['n_row', 'event_custom'], how='outer'
#         )
#
#     def get_farmbit_data(self, x):
#         return {
#             "fb_name": x.name,
#             "hg_dh_interval_secs": x.get_interval(),
#             "sess_id": x.sess_id,
#             "hg_data": x.hunger_data,
#             "dh_data": x.death_data}
#
#     def fb_to_csv(self, out):
#         fb_df = pd.DataFrame()
#         fb_df = fb_df.append([self.get_farmbit_data(x) for x in self.farmBits.values()], ignore_index=True)
#         print(fb_df)
#         fb_df.to_csv(out)
#
#     class FarmbitDeaths():
#         def __init__(self, hunger_data, death_data=None):
#             self.hunger_data, self.dh_data = hunger_data, np.NaN
#             self.name = self.hunger_data.event_data_complex['farmbit'][2]
#             self.food_data, self.money_data = {}, {}
#             self.hg_time, self.dh_time = self.hunger_data.utc_time_secs, -100000000
#             self.sess_id = self.hunger_data.sess_id
#
#         def set_dh(self, death_data):
#             self.dh_data = death_data
#             self.dh_time = self.dh_data.utc_time_secs
#
#         def get_interval(self):
#             if self.dh_time < 0:
#                 return -self.dh_time
#             return self.dh_time - self.hg_time
#
#         def get_food(self):
#             return sorted([[k, v['food']] for k, v in self.food_data.items()], key=lambda x: x[0])
#
#         def get_money(self):
#             return sorted([[k, v['money']] for k, v in self.money_data.items()], key=lambda x: x[0])
#
#         def print_farmbit(self):
#             dh_t_print = self.dh_data if self.dh_data == 'No death' else self.dh_data.utc_time_secs
#             s = f'Name: {self.name}\nTime:{self.get_interval()}\nSession:{self.sess_id}\n'
#             s += f'Hunger: {self.hunger_data.utc_time_secs}\nDeath: {dh_t_print}\n'
#             s += "\n".join(f'Session: {x[0]} Food: {x[1]}' for x in self.get_food()) + "\n"
#             s += "\n".join(f'Session: {x[0]} Money: {x[1]}' for x in self.get_money())
#             print(s)
#
#
# class SimpleDeathPredModel(DeathPredModel):
#     def __init__(self, levels=[], time_int=10):
#         super().__init__(levels, time_int)
#
#     def _eval(self, rows):
#         self.df = pd.DataFrame.from_records(rows)
#         self.process_df()
#         self.all_hunger_death_eval()
#         if list(self.farmBits.values())[0].get_interval() > self.time_int:
#             return False
#         return True
#
#
# class SimpleMoneyDeathPredModel(DeathPredModel):
#     def __init__(self, levels=[], money=300):
#         super().__init__(levels, money)
#
#     def Eval(self, rows):
#         return self._eval(rows)
#
#     def _eval(self, rows):
#         self.df = pd.DataFrame.from_records(rows)
#         self.process_df()
#         self.all_hunger_death_eval()
#         return self.food_money_death_eval(MONEY_RATE_ENUM)
#
#
# class SimpleFoodDeathPredModel(DeathPredModel):
#     def __init__(self, levels=[], food=300):
#         super().__init__(levels, food)
#
#     def Eval(self, rows):
#         return self._eval(rows)
#
#     def _eval(self, rows):
#         self.df = pd.DataFrame.from_records(rows)
#         self.process_df()
#         self.all_hunger_death_eval()
#         res = self.food_money_death_eval(FOOD_AV_ENUM)
#         print(res)
#         return res
