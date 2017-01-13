from opal.core.test import OpalTestCase
from opal.models import Patient
from django.core.urlresolvers import reverse


class ViewsTest(OpalTestCase):
    fixtures = ['patients_users', 'patients_options', 'patients_records']

    def setUp(self):
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=self.PASSWORD))
        self.patient = Patient.objects.get(pk=1)

    def test_try_to_get_microhaem_for_nonexistent_patient(self):
        last_patient = Patient.objects.order_by("-id").first()

        if last_patient:
            nonexistent_id = last_patient.id + 1
        else:
            nonexistent_id = 1

        url = reverse("microhaem_data_view", kwargs={
            "patient_id": nonexistent_id
        })
        self.assertStatusCode(url, 404)

    def test_add_patient_template_view(self):
        self.assertStatusCode('/templates/modals/add_episode.html', 200)
