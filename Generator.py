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

        # программы
        self.programs = ['ПМ', 'ИВТ', 'ИТСС', 'ИБ']

        # даты
        self.dates = ['01.08', '02.08', '03.08', '04.08']

        # количество мест
        self.places = {
            'ПМ': 40,
            'ИВТ': 50,
            'ИТСС': 30,
            'ИБ': 20
        }

        # фиксированное количество абитуриентов
        self.counts = {
            '01.08': {'ПМ': 60, 'ИВТ': 100, 'ИТСС': 50, 'ИБ': 70},
            '02.08': {'ПМ': 380, 'ИВТ': 370, 'ИТСС': 350, 'ИБ': 260},
            '03.08': {'ПМ': 1000, 'ИВТ': 1150, 'ИТСС': 1050, 'ИБ': 800},
            '04.08': {'ПМ': 1240, 'ИВТ': 1390, 'ИТСС': 1240, 'ИБ': 1190}
        }

        # диапазоны баллов
        self.score_ranges = {
            'physics': (40, 100),
            'russian': (40, 100),
            'math': (40, 100),
            'individual': (0, 10)
        }

        self.last_id = 1

    # генерация баллов
    def generate_scores(self):

        physics = random.randint(*self.score_ranges['physics'])
        russian = random.randint(*self.score_ranges['russian'])
        math = random.randint(*self.score_ranges['math'])
        individual = random.randint(*self.score_ranges['individual'])

        total = physics + russian + math + individual

        return physics, russian, math, individual, total

    # генерация данных за дату
    def generate_date_data(self, date: str) -> List[ApplicantRecord]:

        records = []

        for program in self.programs:

            count = self.counts[date][program]

            for _ in range(count):

                physics, russian, math, individual, total = self.generate_scores()

                records.append(
                    ApplicantRecord(
                        id=self.last_id,
                        consent=False,
                        priority=1,
                        physics_score=physics,
                        russian_score=russian,
                        math_score=math,
                        individual_score=individual,
                        total_score=total,
                        program_id=program,
                        date=date
                    )
                )

                self.last_id += 1

        return records

    # установка согласий (top N по баллам)
    def setup_consent(self, all_records):

        for date in self.dates:

            for program in self.programs:

                records = [
                    r for r in all_records
                    if r.date == date and r.program_id == program
                ]

                records.sort(key=lambda x: x.total_score, reverse=True)

                places = self.places[program]

                for i in range(min(places, len(records))):
                    records[i].consent = True

    # сохранение CSV
    def save_to_csv(self, records, filename):

        if not records:
            return

        records.sort(key=lambda x: x.total_score, reverse=True)

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:

            writer = csv.DictWriter(f, fieldnames=[
                'ID',
                'Согласие',
                'Приоритет',
                'Балл Физика/ИКТ',
                'Балл Русский язык',
                'Балл Математика',
                'Балл за индивидуальные достижения',
                'Сумма баллов'
            ])

            writer.writeheader()

            for r in records:

                writer.writerow({
                    'ID': r.id,
                    'Согласие': 'Да' if r.consent else 'Нет',
                    'Приоритет': r.priority,
                    'Балл Физика/ИКТ': r.physics_score,
                    'Балл Русский язык': r.russian_score,
                    'Балл Математика': r.math_score,
                    'Балл за индивидуальные достижения': r.individual_score,
                    'Сумма баллов': r.total_score
                })

    # генерация всех файлов
    def generate_all_files(self, output_dir='./competitive_lists'):

        os.makedirs(output_dir, exist_ok=True)

        all_records = []

        print("ГЕНЕРАЦИЯ ДАННЫХ")

        for date in self.dates:

            print(f"\nДата {date}")

            records = self.generate_date_data(date)

            all_records.extend(records)

            for program in self.programs:

                count = len([
                    r for r in records
                    if r.program_id == program
                ])

                print(program, count)

        print("\nУстановка согласий...")
        self.setup_consent(all_records)

        print("\nСохранение файлов...")

        for date in self.dates:

            date_records = [
                r for r in all_records
                if r.date == date
            ]

            for program in self.programs:

                program_records = [
                    r for r in date_records
                    if r.program_id == program
                ]

                filename = f"{output_dir}/{date}_{program}.csv"

                self.save_to_csv(program_records, filename)

                print(filename)

            filename = f"{output_dir}/{date}_all.csv"

            self.save_to_csv(date_records, filename)

            print(filename)

        # общий CSV
        filename = f"{output_dir}/all_days_all_programs.csv"

        self.save_to_csv(all_records, filename)

        print(filename)

        # JSON
        json_file = f"{output_dir}/all_data.json"

        with open(json_file, 'w', encoding='utf-8') as f:

            json.dump(
                [
                    {
                        **asdict(r),
                        "consent": "Да" if r.consent else "Нет"
                    }
                    for r in all_records
                ],
                f,
                ensure_ascii=False,
                indent=2
            )

        print(json_file)

        return all_records


# main
def main():

    random.seed()  # каждый раз новые данные

    generator = TestDataGenerator()

    generator.generate_all_files()

    print("\nГОТОВО")


if __name__ == "__main__":
    main()
