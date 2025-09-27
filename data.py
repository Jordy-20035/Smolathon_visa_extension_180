import pandas as pd
import random
from datetime import datetime, timedelta

# Create fictional data for all endpoints
def generate_fines_data():
    """Generate fines data for 2024-2025"""
    fines = []
    violation_codes = ['12.9.1', '12.9.2', '12.12', '12.15.1', '12.16.1', '12.19.2']
    statuses = ['paid', 'unpaid', 'cancelled']
    districts = ['Ленинский', 'Заднепровский', 'Промышленный']
    addresses = [
        'ул. Ленина, 15', 'пр-т Гагарина, 25', 'ул. Большая Советская, 10',
        'ул. Николаева, 8', 'ул. Багратиона, 12', 'ул. Дзержинского, 5'
    ]
    
    for year in [2024, 2025]:
        for month in range(1, 13):
            num_fines = random.randint(80, 150)
            for _ in range(num_fines):
                fine_date = datetime(year, month, random.randint(1, 28))
                fines.append({
                    'issued_at': fine_date.strftime('%Y-%m-%d'),
                    'plate_number': f'А{random.randint(100, 999)}БВ{random.randint(10, 99)}',
                    'violation_code': random.choice(violation_codes),
                    'amount': random.randint(500, 5000),
                    'address': random.choice(addresses),
                    'district': random.choice(districts),
                    'status': random.choice(statuses)
                })
    return pd.DataFrame(fines)

def generate_accidents_data():
    """Generate accidents data for 2024-2025"""
    accidents = []
    accident_types = ['столкновение', 'наезд на пешехода', 'опрокидывание', 'наезд на препятствие']
    severities = ['легкая', 'средняя', 'тяжелая']
    districts = ['Ленинский', 'Заднепровский', 'Промышленный']
    addresses = [
        'ул. Ленина/ул. Большая Советская', 'пр-т Гагарина/ул. Николаева',
        'ул. Багратиона/ул. Дзержинского', 'ул. Маршала Конева/ул. Ново-Ленинградская'
    ]
    
    for year in [2024, 2025]:
        for month in range(1, 13):
            num_accidents = random.randint(15, 40)
            for _ in range(num_accidents):
                accident_date = datetime(year, month, random.randint(1, 28))
                accidents.append({
                    'occurred_at': accident_date.strftime('%Y-%m-%d'),
                    'accident_type': random.choice(accident_types),
                    'severity': random.choice(severities),
                    'casualties': random.randint(0, 3),
                    'address': random.choice(addresses),
                    'district': random.choice(districts)
                })
    return pd.DataFrame(accidents)

def generate_traffic_lights_data():
    """Generate traffic lights inventory"""
    traffic_lights = []
    types = ['пешеходный', 'транспортный', 'комбинированный']
    statuses = ['работает', 'не работает', 'ремонт']
    districts = ['Ленинский', 'Заднепровский', 'Промышленный']
    
    addresses = [
        'ул. Ленина, 1', 'ул. Ленина, 25', 'пр-т Гагарина, 10', 'пр-т Гагарина, 35',
        'ул. Большая Советская, 5', 'ул. Большая Советская, 30', 'ул. Николаева, 3',
        'ул. Николаева, 20', 'ул. Багратиона, 8', 'ул. Дзержинского, 12'
    ]
    
    for i, address in enumerate(addresses):
        install_date = datetime(2020 + random.randint(0, 4), random.randint(1, 12), random.randint(1, 28))
        traffic_lights.append({
            'type': random.choice(types),
            'status': random.choice(statuses),
            'install_date': install_date.strftime('%Y-%m-%d'),
            'address': address,
            'district': random.choice(districts)
        })
    
    return pd.DataFrame(traffic_lights)

def generate_evacuations_data():
    """Generate evacuations data matching the structure from ЦОДД.xlsx"""
    evacuations = []
    months_ru = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    
    for year in [2024, 2025]:
        for month_num, month_name in enumerate(months_ru, 1):
            if year == 2025 and month_num > 8:  # Only up to August 2025
                continue
                
            evacuations.append({
                'год': year,
                'месяц': month_name,
                'маршрут': f'Маршрут {month_num}',
                'количество_эвакуаторов': random.randint(3, 8),
                'количество_выездов': random.randint(80, 200),
                'количество_эвакуаций': random.randint(60, 150),
                'доход_штрафстоянка': random.randint(500000, 2000000)  # in rubles
            })
    
    return pd.DataFrame(evacuations)

# Generate all data
print("Generating fines data...")
fines_df = generate_fines_data()

print("Generating accidents data...")
accidents_df = generate_accidents_data()

print("Generating traffic lights data...")
traffic_lights_df = generate_traffic_lights_data()

print("Generating evacuations data...")
evacuations_df = generate_evacuations_data()

# Save to Excel file with multiple sheets
with pd.ExcelWriter('ЦОДД_полные_данные.xlsx', engine='openpyxl') as writer:
    fines_df.to_excel(writer, sheet_name='Штрафы', index=False)
    accidents_df.to_excel(writer, sheet_name='ДТП', index=False)
    traffic_lights_df.to_excel(writer, sheet_name='Светофоры', index=False)
    evacuations_df.to_excel(writer, sheet_name='Эвакуации', index=False)

print("File 'ЦОДД_полные_данные.xlsx' created successfully!")
print(f"Fines records: {len(fines_df)}")
print(f"Accidents records: {len(accidents_df)}")
print(f"Traffic lights records: {len(traffic_lights_df)}")
print(f"Evacuations records: {len(evacuations_df)}")