from opal.models import Diagnosis


from pathway.pathways import (
    Pathway, Step, RedirectsToEpisodeMixin
)


class AddPatientPathway(RedirectsToEpisodeMixin, Pathway):
    display_name = "Add Patient"
    slug = 'add_patient'

    steps = (
        Step(
            template_url="/templates/pathway/find_patient_form.html",
            controller_class="FindPatientCtrl",
            title="Find Patient",
            icon="fa fa-user"
        ),
        Step(
            model=Diagnosis,
            template_url="elcid/templates/forms/diagnosis_form.html"
        )
    )
