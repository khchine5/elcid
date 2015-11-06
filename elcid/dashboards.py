"""
elCID Dashboards
"""
import datetime
from urllib import urlencode

from dashboard import Dashboard, widgets
from django.db.models import Count
from django.core.urlresolvers import reverse
from opal.models import Episode
from django.utils.functional import cached_property
from elcid.models import Diagnosis, Consultant


class NumberOfDiagnoses(widgets.Number):
    tagline = 'Diagnoses made'

    def get_number(self):
        return Diagnosis.objects.count()


class CurrentPatients(widgets.Number):
    tagline = 'Active'

    def get_number(self):
        return Episode.objects.filter(active=True).count()


class Admissions(widgets.LineChart):
    tagline = 'Admissions'
    slug = 'elcid-admissions'

    def get_lines(self):
        twentyten = datetime.datetime(2013, 1, 1)
        dates = Episode.objects.filter(date_of_admission__gte=twentyten).values('date_of_admission').annotate(Count('date_of_admission'))
        ticks = ['x']
        lines = ['Date of admission']
        for date in dates:
            if date['date_of_admission']:
                ticks.append(date['date_of_admission'].isoformat())
                lines.append(date['date_of_admission__count'])

        return [ticks, lines]


class ConfirmedDiagnosisByConsultant(widgets.Table):
    tagline = "Confirmed Diagnosis by Consultant"
    TOTAL_NUMBER = "Total Number of Patients"
    CONFIRMED_DIAGNOSIS = "% Confirmed Diagnosis"
    CONSULTANT = "consultant"
    table_headers = [CONSULTANT, TOTAL_NUMBER, CONFIRMED_DIAGNOSIS]
    include_index=True

    @cached_property
    def table_data(self):
        rows = []
        consultants = Consultant.objects.all()

        for consultant in consultants:
            row = {}
            row[self.CONSULTANT] = consultant.name
            link = reverse("wardround_index")
            link_args = urlencode({"consultant_at_discharge": consultant.name})
            link = link + "#/consultantreview?" + link_args
            consultant_link = "%s__link" % self.CONSULTANT
            row[consultant_link] = link
            episodes = Episode.objects.exclude(discharge_date=None)
            episodes = episodes.filter(consultantatdischarge__consultant_fk=consultant.pk)
            row[self.TOTAL_NUMBER] = episodes.count()
            with_confirmed = episodes.filter(primarydiagnosis__confirmed=True)
            confirmed_diagnosis = with_confirmed.distinct().count()
            if row[self.TOTAL_NUMBER] == 0:
                row[self.CONFIRMED_DIAGNOSIS] = 0
            else:
                completed = float(confirmed_diagnosis)/float(row[self.TOTAL_NUMBER])
                row[self.CONFIRMED_DIAGNOSIS] = int(100 * completed)
            rows.append(row)

        return sorted(rows, key=lambda x: -x[self.CONFIRMED_DIAGNOSIS])


class UsageDashboard(Dashboard):
    """
    Dashboard relaying core usage statistics for elCID
    """
    name        = 'elCID Metrics'
    description = 'Core metrics for the elCID service.'

    def get_widgets(user):
        return [
            Admissions,
            widgets.NumberOfUsers,
            widgets.NumberOfEpisodes,
            NumberOfDiagnoses,
            CurrentPatients,
        ]


class ConfirmedDiagnosis(Dashboard):
    """
    Dashboard relaying stats about the number of patients discharged
    by named consultants
    """
    name = "Consultant Review Dashboard"
    description = "Statistics about the number of discharged patients with confirmed diagnoses"

    def get_widgets(user):
        return [ConfirmedDiagnosisByConsultant]
