"""
[Virtual] Ward Round implementations
"""
import datetime

from opal.models import Episode
from wardround import WardRound
from obs import models as obsmodels

from elcid import models

class MicroHaem(WardRound):
    name        = 'Micro Haem'
    description = 'All patients on the Micro haem list in ward location order'

    @staticmethod
    def episodes():
        return Episode.objects.filter(active=True, tagging__team__name='micro_haem')


class FinalDiagnosisReview(WardRound):
    name        = 'Final Diagnosis Review'
    description = 'Discharged Patients with a final diagnosis for consultant review.'
    
    filter_template = 'wardrounds/final_diagnosis_filter.html'
    filters    = {
        'discharge_from': 'episode.discharge_date >= moment(value, "DD-MM-YYYY")',
        'discharge_to'  : 'episode.discharge_date <= moment(value, "DD-MM-YYYY")'
    }
    
    @staticmethod
    def episodes():
        unconfirmed = models.PrimaryDiagnosis.objects.filter(confirmed=False)
        return set([d.episode for d in unconfirmed])

    @staticmethod
    def schema():
        return [
            models.Demographics,
            models.Location,
            models.Diagnosis,
            models.MicrobiologyTest,
            models.Antimicrobial,
            models.PrimaryDiagnosis,
            models.SecondaryDiagnosis
        ]


class OPATReviewList(WardRound):
    name = 'OPAT Review'
    description = 'Final review of OPAT patients post end-of-treatment'

    @staticmethod
    def episodes():
        review_ready = models.OPATMeta.objects.filter(review_date__lte=datetime.date.today())
        return set([om.episode for om in review_ready
                    if om.episode.opatoutcome_set.get().treatment_outcome is None])

    @staticmethod
    def schema():
        return [
            models.OPATOutcome,
            models.Demographics,
            models.ContactDetails,
            #    models.Carers,
            models.Location,
            models.PresentingComplaint,
            models.Diagnosis,
            obsmodels.Observation,
            models.PastMedicalHistory,
            models.Antimicrobial,
            models.Allergies,
            models.MicrobiologyTest,
            models.Line,
            models.OPATLineAssessment,
            models.MicrobiologyInput,
            models.OPATReview,
            models.Travel,
            models.Appointment,
            models.Todo,
            models.OPATOutstandingIssues,
            models.GeneralNote,
        ]

