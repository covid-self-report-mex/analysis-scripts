from datetime import timedelta, date
from analysis.utils.db import DailyDiagnosticChangeModel
from analysis.utils.db import LocationModel
from analysis.utils.db import session
from analysis import OUTPUT_DATASETS_PATH
from analysis import DAILY_REPORT_DIR
import csv


DAY_FORMAT = '%Y-%m-%d'


def get_starting_date():
    q = session.query(DailyDiagnosticChangeModel)
    daily_change = q.order_by(DailyDiagnosticChangeModel.date).first()
    if daily_change is None:
        return date.today()
    else:
        return daily_change.date


def export_daily_report_to_csv():

    from_date = get_starting_date()
    to_date = date.today()

    # clean the current output
    for _f in DAILY_REPORT_DIR.glob('*.csv'):
        _f.unlink()

    # query all location first
    q = session.query(LocationModel)
    locations = q.all()
    geo_locations = {}
    for location in locations:
        geo_locations[str(location.postal_code)] = {
            'longitude': location.longitude,
            'latitude': location.latitude,
        }

    fieldnames = [
        'date',
        'postal_code',
        'latitude',
        'longitude',
        'healthy',
        'sick_guess_no_corona',
        'sick_guess_corona',
        'sick_corona_confirmed',
        'recovered_confirmed',
        'recovered_not_confirmed',
    ]

    merge_file = OUTPUT_DATASETS_PATH / 'merge-all-days.csv'
    with open(str(merge_file), 'w', newline='') as csvfile:
        merge_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        merge_writer.writeheader()

        # iterate over days
        totals = {}
        current_day = from_date
        while current_day <= to_date:

            # create daily file
            daily_file = DAILY_REPORT_DIR / (current_day.strftime(DAY_FORMAT) + '.csv')
            with open(str(daily_file), 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                q = session.query(DailyDiagnosticChangeModel)
                daily_changes = q.filter_by(date=current_day).all()

                print(current_day)
                if daily_changes is not None:
                    for daily_change in daily_changes:
                        try:
                            if daily_change.locator not in totals:
                                # then create it
                                totals[daily_change.locator] = {
                                    'longitude': geo_locations[daily_change.locator]['longitude'],
                                    'latitude': geo_locations[daily_change.locator]['latitude'],
                                    'data': [
                                        daily_change.diagnostic_0,
                                        daily_change.diagnostic_1,
                                        daily_change.diagnostic_2,
                                        daily_change.diagnostic_3,
                                        daily_change.diagnostic_4,
                                        daily_change.diagnostic_5,
                                    ]
                                }
                            else:
                                # use the previous total
                                totals[daily_change.locator]['data'] = [
                                    totals[daily_change.locator]['data'][0] + daily_change.diagnostic_0,
                                    totals[daily_change.locator]['data'][1] + daily_change.diagnostic_1,
                                    totals[daily_change.locator]['data'][2] + daily_change.diagnostic_2,
                                    totals[daily_change.locator]['data'][3] + daily_change.diagnostic_3,
                                    totals[daily_change.locator]['data'][4] + daily_change.diagnostic_4,
                                    totals[daily_change.locator]['data'][5] + daily_change.diagnostic_5,
                                ]

                            # totals cannot be negative, just fix if some errors are present in the dataset
                            if totals[daily_change.locator]['data'][0] < 0:
                                totals[daily_change.locator]['data'][0] = 0
                            if totals[daily_change.locator]['data'][1] < 0:
                                totals[daily_change.locator]['data'][1] = 0
                            if totals[daily_change.locator]['data'][2] < 0:
                                totals[daily_change.locator]['data'][2] = 0
                            if totals[daily_change.locator]['data'][3] < 0:
                                totals[daily_change.locator]['data'][3] = 0
                            if totals[daily_change.locator]['data'][4] < 0:
                                totals[daily_change.locator]['data'][4] = 0
                            if totals[daily_change.locator]['data'][5] < 0:
                                totals[daily_change.locator]['data'][5] = 0


                        except KeyError:
                            # wrong npa
                            print('Wrong postal code: ' + daily_change.locator)

                total_status = 0
                # export all totals in the current day
                # this take into account the total from previous days if no daily change in the current day
                for locator, total in totals.items():
                    total_status += sum(total['data'])
                    writer.writerow({
                        'postal_code': locator,
                        'longitude': total['longitude'],
                        'latitude': total['latitude'],
                        'date': current_day.strftime(DAY_FORMAT),
                        'healthy': total['data'][0],
                        'sick_guess_no_corona': total['data'][1],
                        'sick_guess_corona': total['data'][2],
                        'sick_corona_confirmed': total['data'][3],
                        'recovered_not_confirmed': total['data'][4],
                        'recovered_confirmed': total['data'][5],
                    })
                    merge_writer.writerow({
                        'postal_code': locator,
                        'longitude': total['longitude'],
                        'latitude': total['latitude'],
                        'date': current_day.strftime(DAY_FORMAT),
                        'healthy': total['data'][0],
                        'sick_guess_no_corona': total['data'][1],
                        'sick_guess_corona': total['data'][2],
                        'sick_corona_confirmed': total['data'][3],
                        'recovered_not_confirmed': total['data'][4],
                        'recovered_confirmed': total['data'][5],
                    })
                print('CSV for date: ' + str(current_day) + ' with ' + str(total_status) + ' records')

            current_day = current_day + timedelta(days=1)


if __name__ == '__main__':
    export_daily_report_to_csv()

