from django.conf import settings
from django.db import models
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext as _

from iso3166.fields import ISONumericField


try:
    default_translation = settings.ISO3166_DEFAUL_LANG
except AttributeError:
    default_translation = "en"


class Country(models.Model):
    """
    Model holding three unique identities per country.

    number
        ISO 3166-1 numeric
    iso2
        ISO 3166-1 alpha-2
    iso3
        ISO 3166-1 alpha-3

    """
    numeric = ISONumericField(_("ISO numeric"), primary_key=True)
    iso2 = models.CharField(_("ISO alpha-2"), max_length=2, unique=True)
    iso3 = models.CharField(_("ISO alpha-3"), max_length=3, unique=True)

    class Meta:
        verbose_name = _("country")
        verbose_name_plural = _("countries")

    def __unicode__(self):
        return unicode(self.iso3)

    def save(self, *args, **kwargs):
        assert self.numeric >= 0, 'numeric should be positive'
        assert self.numeric < 1000, 'numeric should be less then 1000'
        assert len(self.iso2) == 2 and self.iso2.isalpha(), \
               'iso2 should be 2 characters long'
        assert len(self.iso3) == 3 and self.iso3.isalpha(), \
               'iso3 should be 3 characters long'
        # force upper
        self.iso2 = self.iso2.upper()
        self.iso3 = self.iso3.upper()
        super(Country, self).save(*args, **kwargs)

    def get_name(self, translation=default_translation, force=False):
        """
        Get country name based on translation.
        """
        opts = self._meta
        key = '%s.%s:%s:%s:name' % (opts.app_label, opts.module_name,
                                    self.pk, translation)
        name = cache.get(key)
        if name is None or force:
            try:
                obj = self.names.get(translation=translation)
            except CountryName.DoesNotExist:
                if translation != default_translation:
                    obj = self.names.get(translation=default_translation)
                else:
                    raise
            name = obj.display_name
            cache.set(key, name, 86400)
        return name


class CountryName(models.Model):
    """
    country
        country
    translation
        settings.LANGUAGES
    display_name
        Display name for a country.
    inverted_name
        Official country name using UPPERCASE.
    """
    country = models.ForeignKey(Country, related_name="names")
    translation = models.CharField(_("language"), max_length=5, db_index=True,
                                   choices=settings.LANGUAGES)
    display_name = models.CharField(_("display name"), max_length=255,
                                    db_index=True,
                                    help_text=_("example: &quot;British Virgin Islands&quot"))
    inverted_name = models.CharField(_("inverted name"), max_length=255,
                                     db_index=True,
                                     help_text=_("Official name, UPPERCASE. example: &quot;VIRGIN ISLANDS, BRITISH&quot;"))

    class Meta:
        verbose_name = _("country name")
        verbose_name_plural = _("country names")
        unique_together = ("country", "translation")

    def __unicode__(self):
        return u"%s[%s]: %s" % (unicode(self.country), self.translation,
                                self.display_name)

    def save(self, *args, **kwargs):
        self.inverted_name = self.inverted_name.upper()
        super(CountryName, self).save(*args, **kwargs)


class Region(models.Model):
    """
    Unique name for a list of countries.
    """
    name = models.CharField(_("name of the region"), max_length=255,
                            unique=True)
    countries = models.ManyToManyField(Country, related_name="regions")

    def __unicode__(self):
        return unicode(self.name)


def clear_name_cache(sender, instance, **kwargs):
    """
    Make sure we clear the cache
    """
    opts = Country._meta
    key = '%s.%s:%s:%s:name' % (opts.app_label, opts.module_name,
                                instance.pk, instance.translation)
    cache.delete(key)

post_save.connect(clear_name_cache, CountryName)
post_delete.connect(clear_name_cache, CountryName)
