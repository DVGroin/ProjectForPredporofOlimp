import random
import csv
import json
import os
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class ApplicantRecord:
    id: int
    consent: bool
    priority: int
    physics_score: int
    russian_score: int
    math_score: int
    individual_score: int
    total_score: int
    program_id: str
    date: str


class TestDataGenerator:

    def __init__(self):

        self.programs = ['ПМ', 'ИВТ', 'ИТСС', 'ИБ']

        self.dates = ['01.08', '02.08', '03.08', '04.08']

        self.places = {
            'ПМ': 40,
            'ИВТ': 50,
            'ИТСС': 30,
            'ИБ': 20
        }

        self.counts = {
            '01.08': {'ПМ': 60, 'ИВТ': 100, 'ИТСС': 50, 'ИБ': 70},
            '02.08': {'ПМ': 380, 'ИВТ': 370, 'ИТСС': 350, 'ИБ': 260},
            '03.08': {'ПМ': 1000, 'ИВТ': 1150, 'ИТСС': 1050, 'ИБ': 800},
            '04.08': {'ПМ': 1240, 'ИВТ': 1390, 'ИТСС': 1240, 'ИБ': 1190}
        }

        # пересечения
        self.intersections_2 = {
            '01.08': {('ПМ','ИВТ'):10, ('ПМ','ИТСС'):5, ('ПМ','ИБ'):7,
                      ('ИВТ','ИТСС'):6, ('ИВТ','ИБ'):8, ('ИТСС','ИБ'):4},

            '02.08': {('ПМ','ИВТ'):40, ('ПМ','ИТСС'):35, ('ПМ','ИБ'):30,
                      ('ИВТ','ИТСС'):30, ('ИВТ','ИБ'):25, ('ИТСС','ИБ'):20},

            '03.08': {('ПМ','ИВТ'):120, ('ПМ','ИТСС'):110, ('ПМ','ИБ'):90,
                      ('ИВТ','ИТСС'):100, ('ИВТ','ИБ'):85, ('ИТСС','ИБ'):70},

            '04.08': {('ПМ','ИВТ'):200, ('ПМ','ИТСС'):180, ('ПМ','ИБ'):170,
                      ('ИВТ','ИТСС'):190, ('ИВТ','ИБ'):180, ('ИТСС','ИБ'):160}
        }

        self.intersections_3_4 = {
            '01.08': {
                ('ПМ','ИВТ','ИТСС'):3,
                ('ПМ','ИВТ','ИБ'):3,
                ('ИВТ','ИТСС','ИБ'):2,
                ('ПМ','ИТСС','ИБ'):2,
                ('ПМ','ИВТ','ИТСС','ИБ'):1
            },

            '02.08': {
                ('ПМ','ИВТ','ИТСС'):15,
                ('ПМ','ИВТ','ИБ'):15,
                ('ИВТ','ИТСС','ИБ'):12,
                ('ПМ','ИТСС','ИБ'):10,
                ('ПМ','ИВТ','ИТСС','ИБ'):8
            },

            '03.08': {
                ('ПМ','ИВТ','ИТСС'):50,
                ('ПМ','ИВТ','ИБ'):45,
                ('ИВТ','ИТСС','ИБ'):40,
                ('ПМ','ИТСС','ИБ'):35,
                ('ПМ','ИВТ','ИТСС','ИБ'):30
            },

            '04.08': {
                ('ПМ','ИВТ','ИТСС'):80,
                ('ПМ','ИВТ','ИБ'):80,
                ('ИВТ','ИТСС','ИБ'):70,
                ('ПМ','ИТСС','ИБ'):70,
                ('ПМ','ИВТ','ИТСС','ИБ'):60
            }
        }

        self.score_ranges = {
            'physics': (40,100),
            'russian': (40,100),
            'math': (40,100),
            'individual': (0,10)
        }

        self.last_id = 1


    def generate_scores(self):

        physics = random.randint(*self.score_ranges['physics'])
        russian = random.randint(*self.score_ranges['russian'])
        math = random.randint(*self.score_ranges['math'])
        individual = random.randint(*self.score_ranges['individual'])

        return {
            'physics': physics,
            'russian': russian,
            'math': math,
            'individual': individual,
            'total': physics + russian + math + individual
        }


    def generate_priority(self, n):

        p = list(range(1, n+1))
        random.shuffle(p)
        return p


    def _generate_intersections(self, date, records):

        created = []

        def create(programs):

            applicant_id = self.last_id
            self.last_id += 1

            scores = self.generate_scores()
            priorities = self.generate_priority(len(programs))

            for i, program in enumerate(programs):

                records.append(ApplicantRecord(
                    id=applicant_id,
                    consent=False,
                    priority=priorities[i],
                    physics_score=scores['physics'],
                    russian_score=scores['russian'],
                    math_score=scores['math'],
                    individual_score=scores['individual'],
                    total_score=scores['total'],
                    program_id=program,
                    date=date
                ))

            created.append(set(programs))


        quad = ('ПМ','ИВТ','ИТСС','ИБ')

        for _ in range(self.intersections_3_4[date][quad]):
            create(quad)


        triples = [
            ('ПМ','ИВТ','ИТСС'),
            ('ПМ','ИВТ','ИБ'),
            ('ИВТ','ИТСС','ИБ'),
            ('ПМ','ИТСС','ИБ')
        ]

        for triple in triples:

            needed = self.intersections_3_4[date][triple]

            for _ in range(needed):
                create(triple)


        for pair in self.intersections_2[date]:

            needed = self.intersections_2[date][pair]

            for _ in range(needed):
                create(pair)


    def _fill_remaining(self, date, records):

        counts = {p:0 for p in self.programs}

        for r in records:
            if r.date == date:
                counts[r.program_id]+=1

        for program in self.programs:

            needed = self.counts[date][program] - counts[program]

            for _ in range(max(0, needed)):

                applicant_id = self.last_id
                self.last_id+=1

                scores = self.generate_scores()

                records.append(ApplicantRecord(
                    id=applicant_id,
                    consent=False,
                    priority=1,
                    physics_score=scores['physics'],
                    russian_score=scores['russian'],
                    math_score=scores['math'],
                    individual_score=scores['individual'],
                    total_score=scores['total'],
                    program_id=program,
                    date=date
                ))


    def generate_date_data(self, date):

        records = []

        self._generate_intersections(date, records)

        self._fill_remaining(date, records)

        return records


    def setup_consent(self, records):

        for date in self.dates:

            date_records = [r for r in records if r.date==date]

            by_applicant = {}

            for r in date_records:
                by_applicant.setdefault(r.id, []).append(r)

            for apps in by_applicant.values():
                apps.sort(key=lambda x:x.priority)
                apps[0].consent=True


    def save_to_csv(self, records, filename):

        records.sort(key=lambda x:(x.total_score), reverse=True)

        with open(filename,'w',newline='',encoding='utf-8-sig') as f:

            writer = csv.DictWriter(f, fieldnames=[
                'ID','Согласие','Приоритет',
                'Балл Физика','Балл Русский',
                'Балл Математика','ИД','Сумма'
            ])

            writer.writeheader()

            for r in records:

                writer.writerow({
                    'ID':r.id,
                    'Согласие':'Да' if r.consent else 'Нет',
                    'Приоритет':r.priority,
                    'Балл Физика':r.physics_score,
                    'Балл Русский':r.russian_score,
                    'Балл Математика':r.math_score,
                    'ИД':r.individual_score,
                    'Сумма':r.total_score
                })


    def generate_all_files(self, out='./competitive_lists'):

        os.makedirs(out,exist_ok=True)

        all_records=[]

        for date in self.dates:

            print("DATE",date)

            rec=self.generate_date_data(date)

            all_records.extend(rec)

            for program in self.programs:

                prog=[r for r in rec if r.program_id==program]

                print(program,len(prog))

                self.save_to_csv(
                    prog,
                    f"{out}/{date}_{program}.csv"
                )

        self.setup_consent(all_records)

        self.save_to_csv(
            all_records,
            f"{out}/ALL.csv"
        )

        with open(f"{out}/ALL.json",'w',encoding='utf8') as f:

            json.dump(
                [asdict(r) for r in all_records],
                f,
                ensure_ascii=False,
                indent=2
            )


def main():

    random.seed()

    g=TestDataGenerator()

    g.generate_all_files()


if __name__=="__main__":
    main()
