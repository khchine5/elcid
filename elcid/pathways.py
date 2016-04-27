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
            template_url="elcid/templates/diagnosis_form.html"
        )
    )

    def save(self, data, user):
        episode = super(AddPatientPathway, self).save(data, user)

        # TODO: This should be refactored into the relevant step
        tagging = data["tagging"]
        episode.set_tag_names(tagging, user)
        return episode
