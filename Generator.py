import random
import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, asdict

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
        self.intersections_2 = {
            '01.08': {
                ('ПМ', 'ИВТ'): 22, ('ПМ', 'ИТСС'): 17, ('ПМ', 'ИБ'): 20,
                ('ИВТ', 'ИТСС'): 19, ('ИВТ', 'ИБ'): 22, ('ИТСС', 'ИБ'): 17
            },
            '02.08': {
                ('ПМ', 'ИВТ'): 190, ('ПМ', 'ИТСС'): 190, ('ПМ', 'ИБ'): 150,
                ('ИВТ', 'ИТСС'): 190, ('ИВТ', 'ИБ'): 140, ('ИТСС', 'ИБ'): 120
            },
            '03.08': {
                ('ПМ', 'ИВТ'): 760, ('ПМ', 'ИТСС'): 600, ('ПМ', 'ИБ'): 410,
                ('ИВТ', 'ИТСС'): 750, ('ИВТ', 'ИБ'): 460, ('ИТСС', 'ИБ'): 500
            },
            '04.08': {
                ('ПМ', 'ИВТ'): 1090, ('ПМ', 'ИТСС'): 1110, ('ПМ', 'ИБ'): 1070,
                ('ИВТ', 'ИТСС'): 1050, ('ИВТ', 'ИБ'): 1040, ('ИТСС', 'ИБ'): 1090
            }
        }
        self.intersections_3_4 = {
            '01.08': {
                ('ПМ', 'ИВТ', 'ИТСС'): 5, ('ПМ', 'ИВТ', 'ИБ'): 5,
                ('ИВТ', 'ИТСС', 'ИБ'): 5, ('ПМ', 'ИТСС', 'ИБ'): 5,
                ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 3
            },
            '02.08': {
                ('ПМ', 'ИВТ', 'ИТСС'): 70, ('ПМ', 'ИВТ', 'ИБ'): 70,
                ('ИВТ', 'ИТСС', 'ИБ'): 70, ('ПМ', 'ИТСС', 'ИБ'): 70,
                ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 50
            },
            '03.08': {
                ('ПМ', 'ИВТ', 'ИТСС'): 500, ('ПМ', 'ИВТ', 'ИБ'): 260,
                ('ИВТ', 'ИТСС', 'ИБ'): 300, ('ПМ', 'ИТСС', 'ИБ'): 250,
                ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 200
            },
            '04.08': {
                ('ПМ', 'ИВТ', 'ИТСС'): 1020, ('ПМ', 'ИВТ', 'ИБ'): 1020,
                ('ИВТ', 'ИТСС', 'ИБ'): 1000, ('ПМ', 'ИТСС', 'ИБ'): 1040,
                ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 1000
            }
        }
        self.score_ranges = {
            'physics': (40, 100),
            'russian': (40, 100),
            'math': (40, 100),
            'individual': (0, 10)
        }
        self.last_id = 1

    def generate_scores(self) -> dict:
        physics = random.randint(*self.score_ranges['physics'])
        russian = random.randint(*self.score_ranges['russian'])
        math = random.randint(*self.score_ranges['math'])
        individual = random.randint(*self.score_ranges['individual'])
        total = physics + russian + math + individual
        return {
            'physics': physics,
            'russian': russian,
            'math': math,
            'individual': individual,
            'total': total
        }

    def generate_priority(self, num_programs: int) -> List[int]:
        priorities = list(range(1, num_programs + 1))
        random.shuffle(priorities)
        return priorities

    def _generate_intersections(self, date: str, records: List[ApplicantRecord]):
        count_4 = self.intersections_3_4[date][('ПМ', 'ИВТ', 'ИТСС', 'ИБ')]
        for _ in range(count_4):
            applicant_id = self.last_id
            self.last_id += 1
            scores = self.generate_scores()
            priorities = self.generate_priority(4)
            for idx, program in enumerate(self.programs):
                records.append(ApplicantRecord(
                    id=applicant_id,
                    consent=False,
                    priority=priorities[idx],
                    physics_score=scores['physics'],
                    russian_score=scores['russian'],
                    math_score=scores['math'],
                    individual_score=scores['individual'],
                    total_score=scores['total'],
                    program_id=program,
                    date=date
                ))

        triples = [
            ('ПМ', 'ИВТ', 'ИТСС'),
            ('ПМ', 'ИВТ', 'ИБ'),
            ('ИВТ', 'ИТСС', 'ИБ'),
            ('ПМ', 'ИТСС', 'ИБ')
        ]
        for triple in triples:
            count = self.intersections_3_4[date][triple]
            for _ in range(count):
                applicant_id = self.last_id
                self.last_id += 1
                scores = self.generate_scores()
                priorities = self.generate_priority(3)
                for idx, program in enumerate(triple):
                    records.append(ApplicantRecord(
                        id=applicant_id,
                        consent=False,
                        priority=priorities[idx],
                        physics_score=scores['physics'],
                        russian_score=scores['russian'],
                        math_score=scores['math'],
                        individual_score=scores['individual'],
                        total_score=scores['total'],
                        program_id=program,
                        date=date
                    ))

        for pair, count in self.intersections_2[date].items():
            for _ in range(count):
                applicant_id = self.last_id
                self.last_id += 1
                scores = self.generate_scores()
                priorities = self.generate_priority(2)
                for idx, program in enumerate(pair):
                    records.append(ApplicantRecord(
                        id=applicant_id,
                        consent=False,
                        priority=priorities[idx],
                        physics_score=scores['physics'],
                        russian_score=scores['russian'],
                        math_score=scores['math'],
                        individual_score=scores['individual'],
                        total_score=scores['total'],
                        program_id=program,
                        date=date
                    ))

    def _fill_remaining(self, date: str, records: List[ApplicantRecord]):
        current_counts = {prog: 0 for prog in self.programs}
        for record in records:
            if record.date == date:
                current_counts[record.program_id] += 1
        for program in self.programs:
            needed = self.counts[date][program] - current_counts[program]
            for _ in range(needed):
                applicant_id = self.last_id
                self.last_id += 1
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

    def generate_date_data(self, date: str) -> List[ApplicantRecord]:
        records = []
        self._generate_intersections(date, records)
        self._fill_remaining(date, records)
        return records

    def setup_consent(self, all_records: List[ApplicantRecord]):
        for date in self.dates:
            date_records = [r for r in all_records if r.date == date]
            applicants = {}
            for record in date_records:
                if record.id not in applicants:
                    applicants[record.id] = []
                applicants[record.id].append(record)
            for apps in applicants.values():
                apps.sort(key=lambda x: x.priority)
                apps[0].consent = True
            if date == '04.08':
                for program in self.programs:
                    program_records = [r for r in date_records if r.program_id == program]
                    consent_count = sum(1 for r in program_records if r.consent)
                    places = self.places[program]
                    if consent_count <= places:
                        program_records.sort(key=lambda x: x.total_score, reverse=True)
                        for record in program_records[:places + 10]:  # +10 запас
                            if not record.consent:
                                record.consent = True
                                consent_count += 1
                                if consent_count > places:
                                    break

    def save_to_csv(self, records: List[ApplicantRecord], filename: str):
        if not records:
            return
        records.sort(key=lambda x: (x.id, x.priority))
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'ID', 'Согласие', 'Приоритет', 'Балл Физика/ИКТ',
                'Балл Русский язык', 'Балл Математика',
                'Балл за индивидуальные достижения', 'Сумма баллов'
            ])
            writer.writeheader()
            for record in records:
                writer.writerow({
                    'ID': record.id,
                    'Согласие': 'Да' if record.consent else 'Нет',
                    'Приоритет': record.priority,
                    'Балл Физика/ИКТ': record.physics_score,
                    'Балл Русский язык': record.russian_score,
                    'Балл Математика': record.math_score,
                    'Балл за индивидуальные достижения': record.individual_score,
                    'Сумма баллов': record.total_score
                })

    def generate_all_files(self, output_dir: str = './competitive_lists'):
        os.makedirs(output_dir, exist_ok=True)
        all_records = []
        print("ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ")
        for date in self.dates:
            print(f"\nГенерация данных за {date}...")
            records = self.generate_date_data(date)
            all_records.extend(records)
            for program in self.programs:
                count = len([r for r in records if r.program_id == program])
                expected = self.counts[date][program]
                print(f"  {program}: {count} записей (ожидалось {expected})")
        print(f"\nНастройка согласий на зачисление...")
        self.setup_consent(all_records)
        print(f"\nСохранение файлов...")
        for date in self.dates:
            date_records = [r for r in all_records if r.date == date]
            for program in self.programs:
                program_records = [r for r in date_records if r.program_id == program]
                filename = f"{output_dir}/{date}_{program}.csv"
                self.save_to_csv(program_records, filename)
                print(f"{filename}")
            all_date_file = f"{output_dir}/{date}_all.csv"
            self.save_to_csv(date_records, all_date_file)
            print(f"{all_date_file} ({len(date_records)} записей)")
        all_file = f"{output_dir}/all_days_all_programs.csv"
        self.save_to_csv(all_records, all_file)
        print(f"\nПолный файл: {all_file} ({len(all_records)} записей)")
        json_file = f"{output_dir}/all_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json_data = []
            for record in all_records:
                record_dict = asdict(record)
                record_dict['consent'] = 'Да' if record_dict['consent'] else 'Нет'
                json_data.append(record_dict)
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"{json_file}")
        return all_records

    def validate_data(self, all_records: List[ApplicantRecord]):
        print("\n" + "=" * 60)
        print("ВАЛИДАЦИЯ ДАННЫХ")
        print("=" * 60)
        print("\nПроверка количества записей:")
        for date in self.dates:
            print(f"\n{date}:")
            date_records = [r for r in all_records if r.date == date]
            for program in self.programs:
                prog_records = [r for r in date_records if r.program_id == program]
                expected = self.counts[date][program]
                actual = len(prog_records)
                if actual == expected:
                    print(f"{program}: {actual}")
                else:
                    print(f"{program}: {actual} (ожидалось {expected})")
        print("\nПроверка пересечений (04.08):")
        self._check_intersections(all_records, '04.08')
        print("\nПроверка согласий на зачисление (04.08):")
        date_records = [r for r in all_records if r.date == '04.08']
        applicants = {}
        for record in date_records:
            if record.id not in applicants:
                applicants[record.id] = []
            applicants[record.id].append(record)
        multiple_consent = 0
        for apps in applicants.values():
            consent_count = sum(1 for a in apps if a.consent)
            if consent_count > 1:
                multiple_consent += 1
        if multiple_consent == 0:
            print("У всех абитуриентов не более одного согласия")
        else:
            print(f"Найдено {multiple_consent} абитуриентов с несколькими согласиями")
        for program in self.programs:
            prog_records = [r for r in date_records if r.program_id == program]
            consent_count = sum(1 for r in prog_records if r.consent)
            places = self.places[program]
            if consent_count > places:
                print(f"{program}: {consent_count} согласий > {places} мест")
            else:
                print(f"{program}: {consent_count} согласий <= {places} мест")

    def _check_intersections(self, all_records: List[ApplicantRecord], date: str):
        date_records = [r for r in all_records if r.date == date]
        applicants = {}
        for record in date_records:
            if record.id not in applicants:
                applicants[record.id] = set()
            applicants[record.id].add(record.program_id)
        for pair in self.intersections_2[date]:
            count = sum(1 for apps in applicants.values()
                        if pair[0] in apps and pair[1] in apps
                        and len(apps) == 2)
            expected = self.intersections_2[date][pair]
            if count == expected:
                print(f"{pair[0]}-{pair[1]}: {count}")
            else:
                print(f"{pair[0]}-{pair[1]}: {count} (ожидалось {expected})")
        triples = [
            ('ПМ', 'ИВТ', 'ИТСС'),
            ('ПМ', 'ИВТ', 'ИБ'),
            ('ИВТ', 'ИТСС', 'ИБ'),
            ('ПМ', 'ИТСС', 'ИБ')
        ]
        for triple in triples:
            count = sum(1 for apps in applicants.values()
                        if all(p in apps for p in triple)
                        and len(apps) == 3)
            expected = self.intersections_3_4[date][triple]
            if count == expected:
                print(f"{'-'.join(triple)}: {count}")
            else:
                print(f"{'-'.join(triple)}: {count} (ожидалось {expected})")
        count = sum(1 for apps in applicants.values() if len(apps) == 4)
        expected = self.intersections_3_4[date][('ПМ', 'ИВТ', 'ИТСС', 'ИБ')]
        if count == expected:
            print(f"ПМ-ИВТ-ИТСС-ИБ: {count}")
        else:
            print(f"ПМ-ИВТ-ИТСС-ИБ: {count} (ожидалось {expected})")

def main():
    generator = TestDataGenerator()
    records = generator.generate_all_files('./competitive_lists')
    generator.validate_data(records)
    print("ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
    print("\nСгенерированные файлы находятся в папке './competitive_lists'")
    print("\nСтруктура файлов:")
    print("  - ДД.ММ_ОП.csv     - по дням и программам")
    print("  - ДД.ММ_all.csv    - общие файлы по дням")
    print("  - all_days_all_programs.csv - полные данные")
    print("  - all_data.json    - данные в JSON формате")

if __name__ == "__main__":
    random.seed(42)
    main()
