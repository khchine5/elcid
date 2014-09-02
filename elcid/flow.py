"""
Defining the patient flows for our system.
"""

flows = {
    'default': {
        'enter': {
            'controller': 'HospitalNumberCtrl',
            'template'  : '/templates/modals/hospital_number.html/'
        },
        'exit': {
            'controller': 'ElcidDischargeEpisodeCtrl',
            'template'  : '/templates/modals/discharge_episode.html/'
        }
    },
    'opat': {
        'default': {
            'exit': {
                'controller': 'OPATDischargeCtrl',
                'template'  : '/templates/modals/discharge_opat_episode.html/'
            }
        }
    },
    'infectious_diseases': {
        'id_inpatients': {
            'enter': {
                'controller': 'DiagnosisHospitalNumberCtrl',
                'template'  : '/templates/modals/hospital_number.html/'
            }
        }
    },
    'hiv': {
        'immune_inpatients': {
            'enter': {
                'controller': 'DiagnosisHospitalNumberCtrl',
                'template'  : '/templates/modals/hospital_number.html/'
            }
        }
    },
    'tropical_diseases': {
        'default': {
            'enter': {
                'controller': 'DiagnosisHospitalNumberCtrl',
                'template'  : '/templates/modals/hospital_number.html/'
            }
        }
    }
}
