from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from analysis import DATABASE, MYSQL_PORT


base = declarative_base()
engine = sa.create_engine('mysql+pymysql://root:root@localhost:' + MYSQL_PORT + '/' + DATABASE)
base.metadata.bind = engine
session = orm.scoped_session(orm.sessionmaker())(bind=engine)


class IndividualReportModel(base):
    __tablename__ = 'individual_report'
    document_id = sa.Column(sa.String(30), primary_key=True)
    diagnostic = sa.Column(sa.Integer,nullable=False)
    locator = sa.Column(sa.String(15),nullable=False)
    session_id = sa.Column(sa.String(50),nullable=False)
    timestamp = sa.Column(sa.BigInteger, nullable=False)
    symptoms = sa.Column(sa.String(255))
    analysis_done = sa.Column(sa.Boolean,nullable=False)

    def __repr__(self):
        return '<Indiv. report: NPA ' + self.locator + ' time ' + str(self.timestamp) + '>'


class DailyDiagnosticChangeModel(base):
    __tablename__ = 'daily_diagnostic_change'
    id = sa.Column(sa.Integer, primary_key=True,autoincrement=True)
    locator = sa.Column(sa.String(15))
    date = sa.Column(sa.Date)
    diagnostic_0 = sa.Column(sa.Integer, default=0)
    diagnostic_1 = sa.Column(sa.Integer, default=0)
    diagnostic_2 = sa.Column(sa.Integer, default=0)
    diagnostic_3 = sa.Column(sa.Integer, default=0)
    diagnostic_4 = sa.Column(sa.Integer, default=0)
    diagnostic_5 = sa.Column(sa.Integer, default=0)

    def __repr__(self):
        d = str(self.year) + '-' + str(self.month) + '-' + str(self.day)
        change = [
            self.diagnostic_0,
            self.diagnostic_1,
            self.diagnostic_2,
            self.diagnostic_3,
            self.diagnostic_4,
        ]
        return '<DailyChang: NPA ' + self.locator + ' ' + d + ' ' + str(change) + '>'


class LocationModel(base):
    """
    headers from csv: country_code,postal_code,town,region,latitude,longitude
    """
    __tablename__ = 'locations'
    postal_code = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    country_code = sa.Column(sa.String(3))
    region_id = sa.Column(sa.Text)
    longitude = sa.Column(sa.Float)
    latitude = sa.Column(sa.Float)

    def __repr__(self):
        return '<Location: ' + self.postal_code + '>'


def init_db():
    base.metadata.create_all()


