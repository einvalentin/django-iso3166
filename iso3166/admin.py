from django.contrib import admin
from django.utils.translation import ugettext as _

from iso3166.models import Country, CountryName, Region


class CountryNameInline(admin.TabularInline):
    model = CountryName


class CountryAdmin(admin.ModelAdmin):
    list_display = ("get_name", "numeric", "iso2", "iso3")
    search_fields = ["names__name", "=numeric", "=iso2", "=iso3"]
    inlines = [CountryNameInline]
admin.site.register(Country, CountryAdmin)


def display_countries(obj):
    return u", ".join([c.get_name() for c in obj.countries.all()])
display_countries.short_description = _('countries')


class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", display_countries)
    search_fields = ["name", "countries__names__name", "=countries__numeric",
                     "=countries__iso2", "=countries__iso3"]

admin.site.register(Region, RegionAdmin)
