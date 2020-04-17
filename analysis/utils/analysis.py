"""
Created by nuffer at 3/24/20

"""
import time
from datetime import datetime, date
import pandas as pd
from analysis.utils.db import engine, session
from analysis.utils.db import DailyDiagnosticChangeModel
from analysis.utils.db import IndividualReportModel


def count_report_to_analyse():
    q = session.query(IndividualReportModel)
    return q.filter_by(analysis_done=False).count()


def analysis_next_report(collection_size: int):
    start_time_analysis = time.time()

    # load all previous reports
    report_done_df = pd.read_sql("SELECT * FROM individual_report WHERE analysis_done = 1",
                                 con=engine, index_col="document_id")

    # load the next collection of reports to analyse
    next_reports = pd.read_sql("SELECT * FROM individual_report WHERE analysis_done = 0 ORDER BY timestamp LIMIT " + str(collection_size),
                               con=engine, index_col="document_id")

    # timestamp from millisecond to second
    report_done_df["timestamp"] = report_done_df["timestamp"] / 1000
    next_reports["timestamp"] = next_reports["timestamp"] / 1000

    # Hold the reports to update in the end
    report_to_update = list()

    # Hold the reports to update in the end
    daily_delta_df = pd.DataFrame(columns=['locator','year','month','day','0','1','2','3','4','5'])

    sample = 0
    start_time = time.time()
    # iterate in all the report to analyse
    for doc_id, next_report in next_reports.iterrows():
        sample += 1

        _date = datetime.fromtimestamp(next_report['timestamp']) # to seconds

        delta = [0, 0, 0, 0, 0, 0]

        # search for last status
        same_session_id_df = report_done_df.loc[report_done_df['session_id'] == next_report['session_id']]
        if same_session_id_df.empty:
            delta[next_report['diagnostic']] = 1
            #print('Delta (new user)',str(delta))
        else:
            last_report = same_session_id_df.sort_values(by=['timestamp'], ascending=False).iloc[0]
            if last_report['diagnostic'] != next_report['diagnostic']:
                delta[last_report['diagnostic']] = -1
                delta[next_report['diagnostic']] = 1
            #print('Delta (existing user)', str(delta))


        # check if daily delta already exist
        previous_daily = daily_delta_df.loc[(daily_delta_df['year'] == _date.year)
                                             & (daily_delta_df['month'] == _date.month)
                                             & (daily_delta_df['day'] == _date.day)
                                             & (daily_delta_df['locator'] == next_report['locator'])]

        if previous_daily.empty:
            # then create it
            new_daily = dict()
            new_daily['locator'] = next_report['locator']
            new_daily['year'] = _date.year
            new_daily['month'] = _date.month
            new_daily['day'] = _date.day
            new_daily['0'] = delta[0]
            new_daily['1'] = delta[1]
            new_daily['2'] = delta[2]
            new_daily['3'] = delta[3]
            new_daily['4'] = delta[4]
            new_daily['5'] = delta[5]
            new_daily[str(next_report['diagnostic'])] = 1
            daily_delta_df = daily_delta_df.append(new_daily, ignore_index=True)
        else:
            # then update it
            previous_daily = previous_daily.iloc[0]  # convert dataframe to serie by ask the first (the only one) row
            # print('new diagnostic:',next_report['diagnostic'])
            daily_delta_df.at[previous_daily.name, "0"] = previous_daily["0"] + delta[0]
            daily_delta_df.at[previous_daily.name, "1"] = previous_daily["1"] + delta[1]
            daily_delta_df.at[previous_daily.name, "2"] = previous_daily["2"] + delta[2]
            daily_delta_df.at[previous_daily.name, "3"] = previous_daily["3"] + delta[3]
            daily_delta_df.at[previous_daily.name, "4"] = previous_daily["4"] + delta[4]
            daily_delta_df.at[previous_daily.name, "5"] = previous_daily["5"] + delta[5]

        if sample % 100 == 0:
            spend_time = time.time() - start_time
            print('Analysed ' + str(sample) + ' samples in ' + str(spend_time) + 's')
            start_time = time.time()

        # update report status
        next_report['analysis_done'] = 1
        # keep trace of the report to update in DB
        #report_to_update_df = report_to_update_df.append(next_report)
        report_to_update.append(doc_id)
        # update the done report list
        report_done_df = report_done_df.append(next_report)

    #print('====== Report to update ========')
    #print(report_to_update)
    print('====== Daily change ========')
    print(daily_delta_df)



    # upload daily changes
    for doc_id, daily_delta in daily_delta_df.iterrows():
        locator = daily_delta['locator']
        _date = date(daily_delta['year'],daily_delta['month'],daily_delta['day'])
        q = session.query(DailyDiagnosticChangeModel)
        daily_change = q.filter_by(locator=locator, date=_date).first()

        if daily_change is None:
            # then create it
            daily_change = DailyDiagnosticChangeModel(
                locator=locator,
                date=_date,
                diagnostic_0=daily_delta['0'],
                diagnostic_1=daily_delta['1'],
                diagnostic_2=daily_delta['2'],
                diagnostic_3=daily_delta['3'],
                diagnostic_4=daily_delta['4'],
                diagnostic_5=daily_delta['5'],
            )
            session.add(daily_change)
        else:
            # update diagnostic
            daily_change.diagnostic_0 += daily_delta['0']
            daily_change.diagnostic_1 += daily_delta['1']
            daily_change.diagnostic_2 += daily_delta['2']
            daily_change.diagnostic_3 += daily_delta['3']
            daily_change.diagnostic_4 += daily_delta['4']
            daily_change.diagnostic_5 += daily_delta['5']

    session.commit()

    # build query to update individual reports
    ids = '('
    idx = 0
    for doc_id in report_to_update:
        if idx != 0:
            ids += ','
        ids += '"'+doc_id+'"'
        idx += 1
    ids += ')'

    query = 'UPDATE individual_report SET analysis_done=1 WHERE individual_report.document_id IN ' + ids + '; '
    with engine.connect() as con:
        con.execute(query)

    print('Analysis of ' + str(collection_size) + ' in ' + str(time.time() - start_time_analysis) + 's')



