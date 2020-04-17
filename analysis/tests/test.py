"""
Created by nuffer at 3/23/20

"""
import uuid
import random
import time
from datetime import datetime
from analysis.utils.db import IndividualReportModel
from analysis.utils.db import DailyDiagnosticChangeModel
from analysis.utils.db import session
from analysis.utils.analysis import analysis_next_report


def test_insert_speed():

    timestamps = range(1584892474, 1584892474 + 1000)
    npa = 1240
    start_time = time.time()
    for timestamp in timestamps:
        doc_id = str(uuid.uuid4())[0:10]
        report = IndividualReportModel(
            document_id=doc_id,
            diagnostic=random.randint(0, 4),
            locator=npa,
            session_id=str(uuid.uuid4()),
            timestamp=timestamp
        )
        session.add(report)
    session.commit()
    print('Insertion time:',time.time() - start_time)



def test_one_person_update():

    nb_update = 1000
    timestamps = range(1584892474, 1584892474 + nb_update)
    session_id = str(uuid.uuid4())
    npa = 1246

    for timestamp in timestamps:
        doc_id = str(uuid.uuid4())[0:10]
        print(doc_id)
        report = IndividualReportModel(
            document_id=doc_id,
            diagnostic=random.randint(0, 4),
            locator=npa,
            session_id=session_id,
            timestamp=timestamp,
            analysis_done=False
        )
        session.add(report)
    session.commit()

    analysis_next_report(nb_update)

    _date = datetime.fromtimestamp(timestamps[0])
    q = session.query(DailyDiagnosticChangeModel)
    daily_change = q.filter_by(locator=npa, year=_date.year, month=_date.month, day=_date.day).first()

    total = daily_change.diagnostic_0 + \
            daily_change.diagnostic_1 + \
            daily_change.diagnostic_2 + \
            daily_change.diagnostic_3 + \
            daily_change.diagnostic_4

    print(total)
    assert total == 1


def test_multiple_persons_by_npa():
    persons = 100
    timestamp = int(time.time())
    npa = 3240

    for id in range(0,persons):
        doc_id = str(uuid.uuid4())[0:10]
        print(doc_id)
        report = IndividualReportModel(
            document_id=doc_id,
            diagnostic=random.randint(0, 4),
            locator=npa,
            session_id=str(uuid.uuid4()),
            timestamp=timestamp,
            analysis_done=False
        )
        session.add(report)
    session.commit()

    analysis_next_report(persons)

    _date = datetime.fromtimestamp(timestamp)
    print(_date)
    q = session.query(DailyDiagnosticChangeModel)
    daily_change = q.filter_by(locator=npa, year=_date.year, month=_date.month, day=_date.day).first()

    total = daily_change.diagnostic_0 + \
            daily_change.diagnostic_1 + \
            daily_change.diagnostic_2 + \
            daily_change.diagnostic_3 + \
            daily_change.diagnostic_4

    assert persons == total

if __name__ == '__main__':
    test_multiple_persons_by_npa()

