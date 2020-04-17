"""
Created by nuffer at 3/25/20

"""
import pandas as pd
from analysis.utils.db import engine, session
from datetime import datetime
import matplotlib.pyplot as plt


def generate_report_by_time():
    """
    todo replace date ticker
    :return:
    """
    reports = pd.read_sql("SELECT * FROM individual_report ORDER BY timestamp", con=engine, index_col="document_id")
    reports["timestamp"] = reports["timestamp"] / 1000

    reports_count = 0
    reports_counts = []
    reports_dates = []
    for doc_id, report in reports.iterrows():
        reports_count += 1
        _date = datetime.fromtimestamp(report['timestamp'])
        reports_counts.append(reports_count)
        reports_dates.append(_date)
    import matplotlib.dates as mdates

    # plot
    fig, ax = plt.subplots()
    plt.plot(reports_dates, reports_counts)
    # beautify the x-labels
    plt.gcf().autofmt_xdate()

    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    # use a more precise date string for the x axis locations in the
    # toolbar
    # ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d %H:%m')
    # ax.set_title('fig.autofmt_xdate fixes the labels')

    plt.show()


if __name__ == '__main__':
    generate_report_by_time()




