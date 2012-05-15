import os
from tempfile import mkdtemp
from urllib import urlretrieve

from django.conf import settings
from django.core import management

try:
    urls = settings.ISO3166_SOURCES
except AttributeError:
    urls = (
        "http://files.co-capacity.biz/iso3166/latest.json.bz2",
        "http://files.co-capacity.biz/iso3166/latest.xml.bz2",
        "http://files.co-capacity.biz/iso3166/latest.json.gz",
        "http://files.co-capacity.biz/iso3166/latest.xml.gz",
        "http://files.co-capacity.biz/iso3166/latest.json",
        "http://files.co-capacity.biz/iso3166/latest.xml",
    )


class Command(management.base.NoArgsCommand):

    def handle_noargs(self, **options):
        """
        We will try to update country objects based on
        `settings.ISO3166_SOURCES` if it's not defined we will use default.

        Only iso3166 models will be updated.

        """
        for url in urls:
            try:
                d = mkdtemp(prefix="iso3166.")
            except:
                continue
            else:
                filename = os.path.join(d, url.split("/")[-1])
                try:
                    filename, headers = urlretrieve(url, filename)
                    if self._check(filename):
                        management.call_command('loaddata', filename,
                                                verbosity=0)
                except:
                    continue
                else:
                    break
                finally:
                    os.remove(filename)
            finally:
                os.rmdir(d)

    def _check(self, src):
        """
        Here we check the downloaded fixture.

        currently supported formats:
        * json
        * xml

        both can be compressed with zip, gz or bz2
        """
        import gzip
        import zipfile
        try:
            import bz2
            has_bz2 = True
        except ImportError:
            has_bz2 = False

        class SingleZipReader(zipfile.ZipFile):

            def __init__(self, *args, **kwargs):
                zipfile.ZipFile.__init__(self, *args, **kwargs)
                if settings.DEBUG:
                    assert len(self.namelist()) == 1, \
                          "Zip-compressed fixtures must contain only one file."

            def read(self):
                return zipfile.ZipFile.read(self, self.namelist()[0])

        compression_types = {
            None: file,
            'gz': gzip.GzipFile,
            'zip': SingleZipReader,
        }
        if has_bz2:
            compression_types['bz2'] = bz2.BZ2File

        parts = src.split('.')

        # get compression format
        if len(parts) > 1 and parts[-1] in compression_types:
            compression_format = parts[-1]
            parts = parts[:-1]
        else:
            compression_format = None

        # set open_method based on compression_format
        open_method = compression_types[compression_format]

        # get format
        if len(parts) == 1:
            fixture_name = parts[0]
            format = "json"
        else:
            fixture_name, format = '.'.join(parts[:-1]), parts[-1]

        # set check_method based on format
        format_types = {
            None: self._check_json,
            'json': self._check_json,
            'xml': self._check_xml,
        }
        check_method = format_types[format]

        # create file_name based on format and compression_format
        if compression_format:
            file_name = '.'.join([fixture_name, format, compression_format])
        else:
            file_name = '.'.join([fixture_name, format])

        try:
            fh = open_method(file_name, 'r')
        except:
            return False
        else:
            return check_method(fh)
        finally:
            fh.close()

    def _check_json(self, fh):
        """
        check if all objects encoded in json are from `iso3166` app.
        """
        from django.utils import simplejson

        try:
            objects = simplejson.load(fh)
        except:
            return False

        for obj in objects:
            if not obj['model'].startswith('iso3166.'):
                return False
        return True

    def _check_xml(self, fh):
        """
        check if all objects encoded in xml are from `iso3166` app.
        """
        from xml.dom.minidom import parse

        try:
            doc = parse(fh)
        except:
            return False

        for e in doc.childNodes[0].childNodes:
            if not e.getAttribute("model").startswith('iso3166.'):
                return False
        return True
