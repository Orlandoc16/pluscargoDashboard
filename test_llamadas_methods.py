import sys
sys.path.append('.')
from services.data_service import DataService
from datetime import datetime, timedelta

# Test specific methods used by llamadas.py
date_range = (datetime.now().date() - timedelta(days=30), datetime.now().date())

print('Testing get_daily_calls_volume...')
try:
    daily_volume = DataService.get_daily_calls_volume(date_range)
    print(f'Daily volume shape: {daily_volume.shape}')
    empty_msg = 'Empty DataFrame'
    print(f'Daily volume columns: {list(daily_volume.columns) if not daily_volume.empty else empty_msg}')
    if not daily_volume.empty:
        print(f'Daily volume first 3 rows: {daily_volume.head(3).to_dict("records")}')
    else:
        print('Daily volume: No data')
except Exception as e:
    print(f'Error in get_daily_calls_volume: {e}')

print('\nTesting get_calls_by_result...')
try:
    results_data = DataService.get_calls_by_result(date_range)
    print(f'Results data shape: {results_data.shape}')
    empty_msg = 'Empty DataFrame'
    print(f'Results data columns: {list(results_data.columns) if not results_data.empty else empty_msg}')
    if not results_data.empty:
        print(f'Results data first 3 rows: {results_data.head(3).to_dict("records")}')
    else:
        print('Results data: No data')
except Exception as e:
    print(f'Error in get_calls_by_result: {e}')