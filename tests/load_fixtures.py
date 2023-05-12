import json
import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)
from disease_trend_system.endpoints import SymptomsDAO, SymtomComplexTransform

SECONDS = 24 * 60 * 60  # seconds in one day


class Generator:
    """Generator test data
    """

    def __init__(self, SYMPTOMS='symptoms', HOSPITALS='hospitals', MIN_RANGE=2, MAX_RANGE=5, FREQUENCY=3, OUTCAST=10, MIN_OBSERVED=20,
                 MAX_OBSERVED=100, DAY_NIGHT_RATIO=3, DAY_RANGE=3, PERCENT_LOW = 20, PERCENT_HIGH = 90, VARIATION = 5, TREND_MIN = 3, TREND_MAX = 20):
        self.symptoms = SYMPTOMS
        self.hospitals = HOSPITALS
        self.min_range = MIN_RANGE  # Min symptoms for observe
        self.max_range = MAX_RANGE  # Max symptoms for observe
        self.frequency = FREQUENCY  # Factor to shrink quantity of observes
        self.outcast = OUTCAST  # max percent change in number of observed
        self.min_observed = MIN_OBSERVED  # min percent with approved
        self.max_observed = MAX_OBSERVED  # max percent with approved
        # difference between quantity of observed at day/night_time
        self.ratio = DAY_NIGHT_RATIO
        self.day_range = DAY_RANGE  #
        self.percent_low = PERCENT_LOW # low edge for disease approve
        self.percent_high = PERCENT_HIGH # high edge for disease approve
        self.variation = VARIATION # difference between previous and next
        self.trend_min = TREND_MIN # minimal trend occurance duration
        self.trend_max = TREND_MAX # maximum trend occurance duration

    def _cur_dir(self) -> str:
        """current directory

        Returns:
            str: path to current directory
        """
        return os.path.dirname(os.path.abspath(__file__))

    def _load_lines_symptoms(self, file: Any) -> Tuple[int, List]:
        """loads list of symptoms separated into groups for different illnesses

        Args:
            file (Any): path to file, maybe file

        Returns:
            Tuple[int, Dict]: len, data
        """
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

    def _load_lines_hospitals(self, file: Any) -> List[str,str]:
        file = open(file, encoding='UTF-8')
        hospitals = []
        for line in file:
            hospitals.append(line.split(":"))
        return hospitals

    def _random_period(self, start: datetime = datetime(2023, 1, 1),
                       stop: datetime = datetime.now()) -> Tuple[datetime, datetime, int]:
        """generates random period in range in range from start date to end

        Args:
            start (datetime, optional): Defaults to datetime(2022, 1, 1).
            stop (datetime, optional):  Defaults to datetime.now().

        Returns:
            Tuple[datetime, datetime, int]: random period
        """
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

    def _random_date(self, start: datetime = datetime(2023, 1, 1)) -> datetime:
        """get ramndom date

        Args:
            start (datetime, optional): Defaults to datetime(2022, 1, 1).

        Returns:
            datetime: random date
        """
        stop = datetime.now()
        delta = stop - start
        int_delta = (delta.days * SECONDS) + delta.seconds
        random_second = random.randrange(int_delta)
        begin = start + timedelta(seconds=random_second)
        return begin

    def _inc_random_date(self, start: datetime = datetime(2023, 1, 1)) -> datetime:
        """generate random data in range from received date to date plus fixed frequency

        Args:
            start (datetime, optional): Defaults to datetime(2022, 1, 1).

        Returns:
            datetime: random data
        """
        delta = timedelta(self.frequency)
        int_delta = (delta.days * SECONDS) + delta.seconds
        random.seed(datetime.now())
        random_second = random.randrange(int_delta)
        return start + timedelta(seconds=random_second)

    def _free_values(self, data: Dict[str, Any], cur_set: Dict[str, Any]) -> Dict[Any, str]:
        """gives elements missing in second set

        Args:
            data (Dict[str, Any]): first elements collection
            cur_set (Dict[str, Any]): second element collection

        Returns:
            Dict[Any, str]: First collection without second collection
        """
        new_set = {}
        keys = list(data.keys())
        for i in range(len(data)):
            if data.get(keys[i]) not in cur_set.values():
                new_set[keys[i]] = data.get(keys[i])
        return new_set

    def _random_key(self, data: Dict[str, Any]) -> Any:
        """gives random element key from set

        Args:
            data (Dict[str, Any]): Symtpomcomplex collection

        Returns:
            Any: random elem
        """
        keys = list(data.keys())
        index = random.randrange(len(data))
        return keys.pop(index)

    def _make_extra(self, all_values: Dict[str, Any], prev: Dict[str, Any], quantity: int) -> Dict[str, Any]:
        """generates detected symptom complex

        Args:
            all_values (Dict[str, Any]): symptom collection
            prev (Dict[str,Any]): ...
            quantity (int): ...

        Returns:
            Dict[str,Any]: random symptom complex
        """
        random.seed(datetime.now())
        if len(prev) == quantity:
            prev.pop(self._random_key(prev))
        if len(prev) > quantity:
            for _ in range(len(prev) - quantity):
                prev.pop(self._random_key(prev))
        else:
            free = self._free_values(all_values, prev)
            unused = list(free.keys())
            if not unused:
                return prev
            for _ in range(quantity - len(prev)):
                index = random.randrange(len(unused))
                prev[unused[index]] = free.get(unused[index])
                unused.pop(index)
        return prev

    def _gen_noice(self, data: Dict[str, Any], hospitals: List, group_data: List, percent: float) -> List:
        """generates trash data with mix of symptoms

        Args:
            data (Dict[str, Any]): data
            group_data (List): group data
            percent (float): percent

        Returns:
            List: _description_
        """
        observes = len(group_data) // 100 * percent // len(data)
        random.seed(datetime.now())
        for group in data:
            people = random.randrange(self.min_observed, self.max_observed)
            percent = random.randrange(self.percent_low, self.percent_high)
            city, hosp = hospitals[random.randrange(len(self.hospitals))]
            extra = {}
            for _ in range(observes):
                people = random.randrange(self.min_observed, self.max_observed)
                start = self._random_date()
                # different quantity of observed in day/night_time
                observed = people // self.ratio if start.hour < 12 else people
                # minimum quantity of symptoms
                MIN = self.min_range if self.max_range >= len(
                    group) else len(group) - 1
                # quantity of features
                features = random.randrange(
                    min(MIN, self.min_range), max(len(group), self.max_range))
                extra = self._make_extra(group, extra, features)

                percent = self._make_percent(percent)
                inf = {"total_number_people": observed, "date_symptoms": start.isoformat(), "percent_people": percent, "city":city, "hospital": hosp,
                       "symptoms": extra}
                group_data.append(inf)
        return group_data

    def _make_percent(self, value: int) -> int:
        if value < 30:  # to show some situations when trend appears
            decision = True if random.randrange(self.percent_high) < self.percent_high // 2 else False
            if decision:
                return value * 2
        sign = -1 if random.randrange(self.variation) < self.variation // 2 else 1
        alternative = value + sign * random.randrange(self.variation)
        if not alternative > 100 and not alternative < 0:
            return alternative
        else:
            if alternative > 100:
                return value - random.randrange(self.variation)
            else:
                return value + random.randrange(self.variation)


    def _generate_dataset(self, count: int, data: List, hospitals: List, noice: bool = False, percent: float = 10) -> List[Dict[str, Any]]:
        """generate dataset

        Args:
            count (int): count of symptimcomplexes
            data (List): source data for generation
            noice (bool, optional): Noise. Defaults to False.
            percent (float, optional): Percent of people for symptomcomplex. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: data for saving
        """
        res = self._gen_groups(count, data, hospitals)
        return res

    def _gen_groups(self, count: int, data: List, hospitals: List) -> List[Dict[str, Any]]:
        """generates groups (trends for illnesses)

        Args:
            count (int): count of symptomcomplexes
            data (List): source data

        Returns:
            List[Dict[str,Any]]: dest
        """

        result = []
        random.seed(datetime.now())
        for group in data:
            start, _, days = self._random_period()
            try:
                observes = random.randrange(days // self.day_range)
            except BaseException as _:
                pass
            people = random.randrange(self.min_observed, self.max_observed)
            percent = random.randrange(self.percent_low, self.percent_high)
            city, hosp = hospitals[random.randrange(len(hospitals))]
            extra: Dict[str, Any] = {}

            for _ in range(observes):
                variety = people // (self.outcast * 2)
                # choose sign for people observed quantity change
                sign = -1 if random.randrange(variety) < variety // 2 else 1
                start = self._inc_random_date(start)
                people = people + sign * variety

                # different quantity of observed in day/night time
                observed = people // self.ratio if start.hour < 12 else people

                # minimum quantity of symptoms
                MIN = self.min_range if self.max_range >= len(
                    group) else len(group) - 1

                # quantity of features
                features = random.randrange(
                    min(MIN, self.min_range), max(len(group), self.max_range))
                extra = self._make_extra(group, extra, features)
                # extra_hashed = self.get_extra_hashed(extra)
                # complex_hashed = self.get_complex_hashed(extra)
                percent = self._make_percent(percent)
                inf = {"total_number_people": observed, "date_symptoms": start.isoformat(), "percent_people": percent,"city": city, "hospital": hosp,
                       "symptoms": extra}
                result.append(inf)
        return result

    def run(self) -> List[Dict[str, Any]]:
        """data generation

        Returns:
            List[Dict[str, Any]]: list of data generation
        """
        count, data = self._load_lines_symptoms(f"{self._cur_dir()}/{self.symptoms}")
        hosp = self._load_lines_hospitals(f"{self._cur_dir()}/{self.hospitals}")
        result = self._generate_dataset(count, data, hosp, True)
        # result = self._gen_noice(data,hosp, result, 10)
        return result

    def export_to_json(self, filename: str, data: List) -> None:
        """export to json file

        Args:
            filename (str): filename
            data (List): list of dicts
        """
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, indent=4, ensure_ascii=False)

    def import_from_json(self, filename: str) -> List:
        """import from json

        Args:
            filename (str): filename

        Returns:
            List: list of dicts
        """
        with open(filename, 'r', encoding='utf-8') as fp:
            file = json.loads(fp)
            data = json.dumps(file, sort_keys=False,
                              indent=4, separators=(',', ': '))
        return data


if __name__ == '__main__':
    generator = Generator()
    symptom_complexes = generator.run()

    for symptom_complex in symptom_complexes:
        symptoms = SymtomComplexTransform.symptom_complex_to_symptoms(
            symptom_complex)
        symptom_dao = SymptomsDAO(
            username_db, password_db, hostname_db, port, name_db)
        symptom_dao.save_symptoms(symptoms)
