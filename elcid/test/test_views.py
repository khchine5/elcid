"""
Unittests for the UCLH eLCID OPAL implementation.
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import ffs

from opal.core.test import OpalTestCase
from opal.models import Patient, Team

from elcid.test.test_models import AbstractEpisodeTestCase
from elcid import constants

HERE = ffs.Path.here()
TEST_DATA = HERE/'test_data'


class ViewsTest(OpalTestCase):
    fixtures = ['patients_users', 'patients_options', 'patients_records']

    def setUp(self):
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=self.PASSWORD))
        self.patient = Patient.objects.get(pk=1)

    def test_try_to_get_patient_detail_for_nonexistent_patient(self):
        last_patient = Patient.objects.order_by("-id").first()

        if last_patient:
            nonexistent_id = last_patient.id + 1
        else:
            nonexistent_id = 1

        url = reverse("patient_detail_data_view", kwargs={
            "patient_id": nonexistent_id
        })
        self.assertStatusCode(url, 404)

    def test_try_to_create_episode_for_existing_patient_with_active_episode(self):
        data = {
            'demographics': {
                "consistency_token": "12345678",
                "date_of_birth": "20/06/1972",
                "hospital_number": "AA1111",
                "id": 1,
                "name": "John Smith",
                "patient_id": 1
            },
            'location': {
                'category': 'Inpatient',
                'hospital': 'UCH',
                'ward': 'T13',
                'bed': 10
                }
            }
        response = self.post_json('/episode/', data)
        self.assertEqual(201, response.status_code)

    def test_create_episode_for_new_patient(self):
        data = {
            'demographics': {
                'hospital_number': 'BB2222',
                'name': 'Johann Schmidt',
                'date_of_birth': '01/06/1970'
                },
            'location': {
                'category': 'Inpatient',
                'hospital': 'UCH',
                'ward': 'T13',
                'bed': 10
                },
            'tagging': [{}]
            }
        response = self.post_json('/episode/', data)
        self.assertEqual(201, response.status_code)

    def test_create_episode_for_patient_without_hospital_number(self):
        data = {
            'demographics': {
                'hospital_number': '',
                'name': 'Johann Schmidt',
                'date_of_birth': '01/06/1970'
                },
            'location': {
                'category': 'Inpatient',
                'hospital': 'UCH',
                'ward': 'T13',
                'bed': 10
                },
            'tagging': [{}]
            }
        response = self.post_json('/episode/', data)
        self.assertEqual(201, response.status_code)

    def test_try_to_update_nonexistent_demographics_subrecord(self):
        response = self.put_json('/api/v0.1/demographics/1234/', {})
        self.assertEqual(404, response.status_code)

    def test_episode_list_template_view(self):
        self.assertStatusCode('/templates/episode_list.html/', 200)

    def test_episode_detail_template_view(self):
        self.assertStatusCode('/templates/episode_detail.html/1', 200)

    def test_patient_notes_template_view(self):
        url = reverse("patient_detail_template_view")
        self.assertStatusCode(url, 200)

    def test_add_patient_template_view(self):
        self.assertStatusCode('/templates/modals/add_episode.html/', 200)

    def test_discharge_patient_template_view(self):
        self.assertStatusCode('/templates/modals/discharge_episode.html/', 200)

    def test_delete_item_confirmation_template_view(self):
        self.assertStatusCode('/templates/modals/delete_item_confirmation.html/', 200)

    def test_location_modal_template_view(self):
        self.assertStatusCode('/templates/modals/location.html/', 200)


class ListSchemaViewTest(OpalTestCase):
    fixtures = ['patients_users', 'patients_options', 'patients_records']

    def setUp(self):
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=self.PASSWORD))
        self.patient = Patient.objects.get(pk=1)
        schema_file = TEST_DATA/'list.schema.json'
        self.schema = schema_file.json_load()

    def assertStatusCode(self, path, expected_status_code):
        response = self.client.get(path)
        self.assertEqual(expected_status_code, response.status_code)


class DetailSchemaViewTest(OpalTestCase):
    fixtures = ['patients_users', 'patients_options', 'patients_records']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.assertTrue(self.client.login(username=self.user.username,
                                          password='password'))
        self.patient = Patient.objects.get(pk=1)
        schema_file = TEST_DATA/'detail.schema.json'
        self.schema = schema_file.json_load()

    def assertStatusCode(self, path, expected_status_code):
        response = self.client.get(path)
        self.assertEqual(expected_status_code, response.status_code)


class ExtractSchemaViewTest(OpalTestCase):
    fixtures = ['patients_users', 'patients_options', 'patients_records']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.assertTrue(self.client.login(username=self.user.username,
                                          password='password'))
        self.patient = Patient.objects.get(pk=1)
        schema_file = TEST_DATA/'extract.schema.json'
        self.schema = schema_file.json_load()

    def assertStatusCode(self, path, expected_status_code):
        response = self.client.get(path)
        self.assertEqual(expected_status_code, response.status_code)


class MicrobiologyInputViewTest(OpalTestCase, AbstractEpisodeTestCase):
    def setUp(self):
        super(MicrobiologyInputViewTest, self).setUp()
        Team.objects.create(
            name=constants.MICROHAEM_TEAM_NAME,
            title=constants.MICROHAEM_TEAM_NAME.title()
        )
        self.url = "/api/v0.1/microbiology_input/"
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=self.PASSWORD))

        self.args = {
            "clinical_discussion": "something interesting",
            "discussed_with": "Jane",
            "episode_id": self.episode.id,
            "initials": "Jane Doe",
            "reason_for_interaction": constants.MICROHAEM_CONSULTATIONS[0],
            "when": "07/10/2015 23:30:00"
        }

    def test_add_microbiology_input(self):
        tags = self.episode.get_tag_names(self.user)
        self.assertEqual(len(tags), 0)
        self.post_json(self.url, self.args)
        updated_tags = self.episode.get_tag_names(self.user)
        self.assertEqual(updated_tags, [constants.MICROHAEM_TEAM_NAME])
        self.post_json(self.url, self.args)

        # make sure tags don't get applied twice if run twice
        updated_tags = self.episode.get_tag_names(self.user)
        self.assertEqual(updated_tags, [constants.MICROHAEM_TEAM_NAME])
