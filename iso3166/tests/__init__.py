from django.test import TestCase, Client
from django.db import IntegrityError, connection

from iso3166.models import *


class iso3166Tests(TestCase):

    def setUp(self):
        self.c = Country.objects.create(numeric=4, iso3="AFG", iso2="AF")

    def tearDown(self):
        self.c.delete()
        self.c = None

    def failUnlessIntegrityError(self, callableObj, *args, **kwargs):
        """
        Fails unless IntegrityError has been raised.
        close connection(re-connenct) or other unittest will fail.
        """
        try:
            callableObj(*args, **kwargs)
        except IntegrityError:
            connection.close()
            return
        else:
            raise self.failureException, \
                  "%s not raised" % IntegrityError.__name__

    def test_numeric_integrity(self):
        self.failUnlessRaises(AssertionError,
                              Country.objects.create,
                              numeric=-1, iso3="ALA", iso2="AX")
        self.failUnlessRaises(AssertionError,
                              Country.objects.create,
                              numeric=1000, iso3="ALA", iso2="AX")

    def test_iso2_integrity(self):
        # check length
        self.failUnlessRaises(AssertionError,
                              Country.objects.create,
                              numeric=248, iso3="ALA", iso2="A")
        # check alpha
        self.failUnlessRaises(AssertionError,
                              Country.objects.create,
                              numeric=248, iso3="ALA", iso2="A1")
        # check auto upper
        c = Country.objects.create(numeric=248, iso3="ALA", iso2="ax")
        self.failUnlessEqual(c.iso2, "AX")
        # check unique, integratie error should be at the end.
        self.failUnlessIntegrityError(Country.objects.create,
                                      numeric=248, iso3="ALA", iso2="AX")

    def test_iso3_integrity(self):
        # check length
        self.failUnlessRaises(AssertionError,
                              Country.objects.create,
                              numeric=248, iso3="A", iso2="AX")
        # check alpha
        self.failUnlessRaises(AssertionError,
                              Country.objects.create,
                              numeric=248, iso3="248", iso2="AX")
        # check auto upper
        c = Country.objects.create(numeric=248, iso3="alA", iso2="AX")
        self.failUnlessEqual(c.iso3, "ALA")
        # check unique
        self.failUnlessIntegrityError(Country.objects.create,
                                      numeric=248, iso3="AlA", iso2="AX")

    def test_countryname(self):
        self.failUnlessEqual(unicode(self.c), u"AFG")
        self.failUnlessRaises(CountryName.DoesNotExist, self.c.get_name)
        self.failUnlessRaises(CountryName.DoesNotExist,
                              self.c.get_name, translation="fr")
        cn = CountryName.objects.create(country=self.c,
                                        translation=default_translation,
                                        display_name="Afghanistan",
                                        inverted_name="AFGHaNiSTAN")
        self.failUnlessEqual(unicode(self.c.get_name()), u"Afghanistan")
        self.failUnlessEqual(unicode(cn.inverted_name), u"AFGHANISTAN")
        self.failUnlessEqual(unicode(self.c.get_name("fr")), u"Afghanistan")

    def test_region(self):
        r = Region.objects.create(name="Africa")
        r.countries.add(self.c)
        self.failUnlessEqual(list(r.countries.all()),
                             [self.c])
        self.failUnlessEqual(list(self.c.regions.all()),
                             [r])
        r.countries.clear()
        self.failUnlessEqual(list(r.countries.all()),
                             [])
        self.failUnlessEqual(list(self.c.regions.all()),
                             [])
        # check unique constain
        self.failUnlessIntegrityError(Region.objects.create,
                                      name="Africa")
