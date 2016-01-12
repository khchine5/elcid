"""
Randomise our admission dates over the last year.
"""
from datetime import datetime, date
import random
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from opal.core.subrecords import episode_subrecords, patient_subrecords
from django.db.models import (
    CharField, DateField, DateTimeField, BooleanField, TextField,
    NullBooleanField
)
from opal import models as omodels
from elcid.models import *
from optparse import make_option

from django.core.management.base import BaseCommand


first_names = [
    "Jane", "James", "Chandeep", "Samantha", "Oliver", "Charlie",
    "Sophie", "Emily", "Lily", "Olivia", "Amelia", "Isabella"
]

last_names = [
    "Smith", "Jones", "Williams", "Taylor", "Brown", "Davies", "Wilson",
    "Brooke", "King", "Patel", "Jameson", "Davidson", "Williams"
]

adjectives = [
    "orange", "red", "blue", "green", "pink", "purple", "gold", "silver",
    "bronze", "ruby", "azure", "copper", "forest", "silent", "loud", "dry",
    "angry"
]

nouns = [
    "cat", "dog", "eagle", "penguin", "lion", "tiger", "cheetah", "antelope",
    "chimpanzee", "gorilla", "spider", "frog", "toad", "bat", "owl", "elvis"
]

PROB_OF_FREE_TEXT = 2  # out of 10


def string_generator(*args, **kwargs):
    return "{0} {1}".format(random.choice(adjectives), random.choice(nouns))


def date_generator(*args, **kwargs):
    start_date = kwargs.get("start_date")
    end_date = kwargs.get("end_date")
    if not end_date:
        end_date = date.today()
    if not start_date:
        today = date.today()
        start_date = date(today.year - 90, today.month, today.day)

    year_diff = end_date.year - start_date.year
    year = end_date.year - random.randint(1, year_diff)

    if year == start_date.year:
        first_month = start_date.month
    else:
        first_month = 1

    if year == end_date.year:
        last_month = end_date.month
    else:
        last_month = 12
    month = random.randint(first_month, last_month)

    if month == end_date.month and year == end_date.year:
        last_day = end_date.day
    else:
        last_day = 28

    if month == start_date.month and year == start_date.year:
        first_day = start_date.day
    else:
        first_day = 1
    day = random.randint(first_day, last_day)
    return date(year, month, day)

def date_time_generator(*args, **kwargs):
    d = date_generator(*args, **kwargs)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    return datetime(d.year, d.month, d.day, hours, minutes)


def foreign_key_or_free_text_generator(field, **kwargs):
    all_options = field.foreign_model.objects.all().values_list("name", flat=True)

    if random.randint(1, 10) <= PROB_OF_FREE_TEXT:
        return string_generator(field)
    else:
        if len(all_options):
            return random.choice(all_options)
        else:
            print "no len for %s" % field.foreign_model


def text_field_generator(*args, **kwargs):
    result = ""
    choices = adjectives + nouns
    for i in xrange(20):
        result += " " + random.choice(choices)

    return result


def boolean_field_generator(*args, **kwargs):
    return random.choice([True, False])


class TagGenerator(object):
    unique_together = [
        ("opat_referrals", "opat_current", "opat_followup",),
        ("walkin_triage", "walkin_doctor", "walkin_review",),
        ("immune_inpatients", "immune_liason",),
        None,  # everything else
    ]

    category_map = {
        "opat": "OPAT",
        "walkin": "Walkin"
    }

    def tag_episode(self, episode):
        tag_types = random.choice(self.unique_together)

        if tag_types:
            tag_type = random.choice(tag_types)
            for tag_category, category in self.category_map.iteritems():
                if tag_type.startswith(tag_category):
                    episode.category = category
                    episode.save()
            episode.set_tag_names([tag_type], None)
        else:
            unique_tag_names = []
            for u in self.unique_together:
                if u:
                    unique_tag_names.extend(u)
            possible_tags = omodels.Team.objects.exclude(
                name__in=unique_tag_names
            ).values_list("name", flat=True)
            tag_amount = random.randint(1, min(len(possible_tags), 3))

            chosen_tags = random.sample(possible_tags, tag_amount)
            episode.set_tag_names(chosen_tags, None)


class PatientGenerator(object):
    """ returns a whole batch of patients with a single episde
        with names, hospital numbers and dates of birth
    """
    def get_name(self):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        return "%s %s" % (first_name, last_name)

    def get_hospital_numbers(self, amount, seed=0):
        template = "00000000"
        numbers = xrange(seed, amount)
        hospital_numbers = []
        for number in numbers:
            hospital_numbers.append("%s%s" % (template[:len(str(number))], number))
        return hospital_numbers

    def get_birth_date(self):
        return date_generator(start_date=date(1920, 1, 1))

    def get_unique_hospital_numbers(self, amount):
        """ return a uniqe amount of hospital numbers
        """
        existing = True
        hospital_numbers = []
        seed = 0

        while existing:
            hospital_numbers.extend(self.get_hospital_numbers(amount))
            existing = Demographics.objects.filter(
                hospital_number__in=hospital_numbers
            ).count()
            if existing:
                seed = seed + amount
                amount = amount - existing

        return hospital_numbers

    def get_country_of_birth(self):
        return foreign_key_or_free_text_generator(omodels.Destination)

    def get_gender(self):
        return foreign_key_or_free_text_generator(omodels.Gender)

    def create_episode(self, patient):
        dob = patient.demographics_set.first().date_of_birth
        kwargs = dict(date_of_admission=date_generator(start_date=dob))
        episode_finished = random.choice([True, False])

        if episode_finished:
            kwargs["discharge_date"] = date_generator(
                start_date=kwargs["date_of_admission"]
            )

        episode = patient.create_episode(**kwargs)
        t = TagGenerator()
        t.tag_episode(episode)
        return episode

    def make(self):
        patient = omodels.Patient.objects.create()
        demographics = patient.demographics_set.first()
        hospital_number = random.randint(1000, 2000000)  # self.get_unique_hospital_numbers(1)[0]
        hospital_number = str(hospital_number)
        demographics_kwargs = dict(
            name=self.get_name(),
            hospital_number=hospital_number,
            nhs_number=hospital_number,
            date_of_birth=self.get_birth_date(),
            gender=random.choice(['Female', 'Male', 'Not Known', 'Not Specified'])
        )

        patient.demographics_set.update(**demographics_kwargs)
        demographics = patient.demographics_set.get()
        demographics.country_of_birth = foreign_key_or_free_text_generator(Demographics.country_of_birth)
        
        # Let's have some episode history.
        for i in range(0, random.choice(range(1, 5))):
            self.create_episode(patient)

            for subrecord in episode_subrecords():
                s = EpisodeSubrecordGenerator(subrecord, patient.episode_set.first())
                s.make()

            for subrecord in patient_subrecords():
                # we've already made the demographics above
                if subrecord.__name__ != "Demographics":
                    s = PatientSubrecordGenerator(subrecord, patient)
                    s.make()

        return patient


class SubRecordGenerator(object):
    default_mapping = {
        CharField: string_generator,
        DateField: date_generator,
        DateTimeField: date_time_generator,
        TextField: text_field_generator,
        BooleanField: boolean_field_generator,
        NullBooleanField: boolean_field_generator,
        ForeignKeyOrFreeText: foreign_key_or_free_text_generator
    }

    PROB_OF_NONE = 2

    def get_additional_kwargs(self, field_class):
        additional_kwargs = {
            DateField: {"start_date": self.start_date},
            DateTimeField: {"start_date": self.start_date}
        }
        return additional_kwargs.get(field_class, {})

    def get_fields(self):
        for field in self.model._meta.get_fields():
            if not field.name.endswith("_fk"):
                if field.name.endswith("_ft"):
                    yield getattr(self.model, field.name[:-3])
                else:
                    if field.__class__ in self.default_mapping:
                        yield field

    def is_null_field(self, field):
        """ should we make this field null
        """
        if random.randint(1, 10) <= self.PROB_OF_NONE:
            if field == NullBooleanField:
                return True

            if getattr(field, "null", False):
                return True

        return False

    def is_empty_string_field(self, field):
        """ should we make this field empty
        """
        if random.randint(1, 10) <= self.PROB_OF_NONE:
            if field == CharField and getattr(field, "blank", False):
                return True

        return False

    def make(self):
        instance = self.get_instance()

        for field in self.get_fields():
            if self.is_null_field(field):
                setattr(instance, field.name, None)
            elif self.is_empty_string_field(field):
                setattr(instance, field.name, "")
            else:
                some_func = self.default_mapping[field.__class__]
                kwargs = self.get_additional_kwargs(field.__class__)
                field_value = some_func(field, **kwargs)
                setattr(instance, field.name, field_value)

        instance.save()
        return instance


class EpisodeSubrecordGenerator(SubRecordGenerator):
    def __init__(self, model, episode):
        self.model = model
        self.episode = episode

    @cached_property
    def start_date(self):
        return self.episode.patient.demographics_set.first().date_of_birth

    def get_instance(self):
        if self.model._is_singleton:
            instance = self.model.objects.get(episode=self.episode)
        else:
            instance = self.model()
            instance.episode = self.episode

        return instance


class PatientSubrecordGenerator(SubRecordGenerator):
    def __init__(self, model, patient):
        self.model = model
        self.patient = patient

    @cached_property
    def start_date(self):
        return self.patient.demographics_set.first().date_of_birth

    def get_instance(self):
        if self.model._is_singleton:
            instance = self.model.objects.get(patient=self.patient)
        else:
            instance = self.model()
            instance.patient = self.patient

        return instance


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            "-n",
            "--number",
            dest="number",
            help="how many would you like to create",
        ),
    )

    def handle(self, *args, **options):
        # create 100 patients, give each between 1-5 episodes
        # over the past 3 years, at least 10 of which have an episode in the
        # last week
        if options['number']:
            number = int(options['number'])
        else:
            number = 100
        p = PatientGenerator()

        for i in xrange(number):
            p.make()
