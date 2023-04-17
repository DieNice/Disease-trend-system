import base64
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timedelta

# from disease_trend_system.endpoints import SymtomComplexTransform

SECONDS = 24 * 60 * 60  # seconds in one day


class Generator:

    def __init__(self, FILE='symptoms', MIN_RANGE=2, MAX_RANGE=5, FREQUENCY=3, OUTCAST=10, MIN_OBSERVED=20,
                 MAX_OBSERVED=100, DAY_NIGHT_RATIO=3, DAY_RANGE=3):
        self.file = FILE
        self.min_range = MIN_RANGE  # Min symptoms for observe
        self.max_range = MAX_RANGE  # Max symptoms for observe
        self.frequency = FREQUENCY  # Factor to shrink quantity of observes
        self.outcast = OUTCAST  # max percent change in number of observed
        self.min_observed = MIN_OBSERVED  # min percent with approved
        self.max_observed = MAX_OBSERVED  # max percent with approved
        # difference between quantity of observed at day/night time
        self.ratio = DAY_NIGHT_RATIO
        self.day_range = DAY_RANGE  #

    def _cur_dir(self) -> str:
        return os.path.dirname(os.path.abspath(__file__))

    # loads list of symptoms separated into groups for different illnesses

    def load_lines(self, file):
        file = open(file, encoding='UTF-8')
        illness_symptoms = []
        subset = {}
        index = 0
        for line in file:
            if "#" in line:
                line = line.replace('#', '')
                line = line.replace('\n', '')
                line = line.lstrip()
                line = line.rstrip()
                if len(subset) != 0:
                    illness_symptoms.append(subset.copy())
                    subset.clear()
                    index = 0
            else:
                line = line.replace('#', '')
                line = line.replace('\n', '')
                line = line.lstrip()
                line = line.rstrip()
                subset.update({line: ""})
                index += 1
        illness_symptoms.append(subset.copy())
        return len(illness_symptoms), illness_symptoms

    # generates random period in range in range from start date to end
    def random_period(self, start=datetime(2022, 1, 1), stop=datetime.now()):
        delta = stop - start
        int_delta = (delta.days * SECONDS) + delta.seconds
        random_second = random.randrange(int_delta)
        begin = start + timedelta(seconds=random_second)
        delta = stop - begin
        int_delta = (delta.days * SECONDS) + delta.seconds
        random_second = random.randrange(int_delta)
        end = begin + timedelta(seconds=random_second)
        delta = end - begin
        return begin, end, delta.days

    def random_date(self, start=datetime(2022, 1, 1)):
        stop = datetime.now()
        delta = stop - start
        int_delta = (delta.days * SECONDS) + delta.seconds
        random_second = random.randrange(int_delta)
        begin = start + timedelta(seconds=random_second)
        return begin

    # generate random data in range from received date to date plus fixed frequency
    def inc_random_date(self, start=datetime(2022, 1, 1)):
        delta = timedelta(self.frequency)
        int_delta = (delta.days * SECONDS) + delta.seconds
        random.seed(datetime.now())
        random_second = random.randrange(int_delta)
        return start + timedelta(seconds=random_second)

    # gives elements missing in second set
    def free_values(self, data, cur_set):
        new_set = {}
        keys = list(data.keys())
        for i in range(len(data)):
            if data.get(keys[i]) not in cur_set.values():
                new_set[keys[i]] = data.get(keys[i])
        return new_set

    # gives random element key from set
    def random_key(self, data):
        keys = list(data.keys())
        index = random.randrange(len(data))
        return keys.pop(index)

    # generates detected symptom complex
    def make_extra(self, all_values, prev, quantity):
        random.seed(datetime.now())
        if len(prev) == quantity:
            prev.pop(self.random_key(prev))
        if len(prev) > quantity:
            for i in range(len(prev) - quantity):
                prev.pop(self.random_key(prev))
        else:
            free = self.free_values(all_values, prev)
            unused = list(free.keys())
            for i in range(quantity - len(prev)):
                index = random.randrange(len(unused))
                prev[unused[index]] = free.get(unused[index])
                unused.pop(index)
        return prev

    def make_hash_sha1(self, data):
        hasher = hashlib.sha1()
        hasher.update(repr(self.make_hashable(data)).encode())
        return base64.b64encode(hasher.digest()).decode()

    def make_hashable(self, data):
        if isinstance(data, (tuple, list)):
            return tuple((self.make_hashable(item) for item in data))

        if isinstance(data, dict):
            return tuple(sorted((k, self.make_hashable(v)) for k, v in data.items()))

        if isinstance(data, (set, frozenset)):
            return tuple(sorted(self.make_hashable(item) for item in data))

        return data

    # hashing symptoms (extra)
    def get_extra_hashed(self, data):
        res = {}
        for key in data:
            value = data.get(key)
            res[key] = self.make_hash_sha1(value)
        return res

    # hashing symptom complex (extra)
    def get_complex_hashed(self, data):
        return self.make_hash_sha1(data)

    # generates trash data with mix of symptoms
    def gen_noice(self, data, group_data, percent):
        observes = len(group_data) // 100 * percent // len(data)
        random.seed(datetime.now())
        for group in data:
            people = random.randrange(self.min_observed, self.max_observed)
            extra = {}
            print()
            for i in range(observes):
                people = random.randrange(self.min_observed, self.max_observed)
                start = self.random_date()
                # different quantity of observed in day/night time
                observed = people // self.ratio if start.hour < 12 else people
                # minimum quantity of symptoms
                MIN = self.min_range if self.max_range >= len(
                    group) else len(group) - 1
                # quantity of features
                features = random.randrange(
                    min(MIN, self.min_range), max(len(group), self.max_range))
                extra = self.make_extra(group, extra, features)
                extra_hashed = self.get_extra_hashed(extra)
                complex_hashed = self.get_complex_hashed(extra)
                percent = random.randrange(20, 100)
                inf = {"people": observed, "date": start.isoformat(), "percent": percent,
                       "extra": json.dumps(extra, ensure_ascii=False), "extra_hashed": extra_hashed,
                       "complex_hashed": complex_hashed}
                group_data.append(inf)
        return group_data

    def generate_dataset(self, count, data, noice=False, percent=10):
        res = self.gen_groups(count, data)
        return res

    # generates groups (trends for illnesses)
    def gen_groups(self, count, data):
        result = []
        random.seed(datetime.now())
        for group in data:
            start, end, days = self.random_period()
            try:
                observes = random.randrange(days // self.day_range)
            except BaseException as _:
                pass
            people = random.randrange(self.min_observed, self.max_observed)
            extra = {}
            
            for i in range(observes):
                variety = people // (self.outcast * 2)
                # choose sign for people observed quantity change
                sign = -1 if random.randrange(variety) < variety // 2 else 1
                start = self.inc_random_date(start)
                people = people + sign * variety

                # different quantity of observed in day/night time
                observed = people // self.ratio if start.hour < 12 else people

                # minimum quantity of symptoms
                MIN = self.min_range if self.max_range >= len(
                    group) else len(group) - 1

                # quantity of features
                features = random.randrange(
                    min(MIN, self.min_range), max(len(group), self.max_range))
                extra = self.make_extra(group, extra, features)
                # extra_hashed = self.get_extra_hashed(extra)
                # complex_hashed = self.get_complex_hashed(extra)
                percent = random.randrange(20, 100)
                inf = {"total_number": observed, "date": start.isoformat(), "percent_people": percent,
                       "symptoms": json.dumps(extra)}
                result.append(inf)
        return result

    def run(self):
        count, data = self.load_lines(f"{self._cur_dir()}/{self.file}")
        result = self.generate_dataset(count, data, True)
        result = self.gen_noice(data, result, 10)
        print(result)
        return result

    def export_to_json(self, filename, data):
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, indent=4, ensure_ascii=False)

    def import_from_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as fp:
            file = json.loads(fp)
            data = json.dumps(file, sort_keys=False,
                              indent=4, separators=(',', ': '))
            print(data)
        return data


if __name__ == '__main__':
    generator = Generator()
    res = generator.run()
    generator.export_to_json("test.json", res)
