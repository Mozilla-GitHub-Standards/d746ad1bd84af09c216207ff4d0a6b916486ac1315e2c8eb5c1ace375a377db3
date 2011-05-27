import urlparse
import datetime

from django.conf import settings
from django.http import QueryDict
from django.utils import translation
from django.utils.encoding import smart_unicode, smart_str
from django.utils.http import urlencode
from django.contrib.sites.models import Site

from jingo import register
import jinja2
from pytz import timezone
from babel import Locale, localedata
from babel.support import Format
from babel.dates import format_date, format_time, format_datetime
from babel.numbers import format_decimal
from tower import ugettext as _, ungettext as _ungettext

from .urlresolvers import reverse


@register.function
def is_translated(msg, locale):
    return _(msg) != msg or locale == 'en-US'

# Most of these functions are taken from kitsune


@register.function
def ungettext(singular, plural, number, context=None):
    return _ungettext(singular, plural, number, context)


@register.function
def url(viewname, *args, **kwargs):
    """Helper for Django's ``reverse`` in templates."""
    locale = kwargs.pop('locale', None)
    return reverse(viewname, locale=locale, args=args, kwargs=kwargs)


@register.filter
def label_with_help(f):
    """Print the label tag for a form field, including the help_text
    value as a title attribute."""
    label = u'<label for="%s" title="%s">%s</label>'
    return jinja2.Markup(label % (f.auto_id, f.help_text, f.label))


@register.filter
def secure_url(url):
    if settings.DEBUG:
        return url
    else:
        site = Site.objects.get_current()
        return u'https://%s%s' % (site, url)


@register.filter
def urlparams(url_, hash=None, query_dict=None, **query):
    """
    Add a fragment and/or query paramaters to a URL.

    New query params will be appended to exising parameters, except duplicate
    names, which will be replaced.
    """
    url_ = urlparse.urlparse(url_)
    fragment = hash if hash is not None else url_.fragment

    q = url_.query
    new_query_dict = (QueryDict(smart_str(q), mutable=True) if
                      q else QueryDict('', mutable=True))
    if query_dict:
        for k, l in query_dict.lists():
            new_query_dict[k] = None  # Replace, don't append.
            for v in l:
                new_query_dict.appendlist(k, v)

    for k, v in query.items():
        new_query_dict[k] = v  # Replace, don't append.

    query_string = urlencode([(k, v) for k, l in new_query_dict.lists() for
                              v in l if v is not None])
    new = urlparse.ParseResult(url_.scheme, url_.netloc, url_.path,
                               url_.params, query_string, fragment)
    return new.geturl()


def _babel_locale(locale):
    """Return the Babel locale code, given a normal one."""
    # Babel uses underscore as separator.
    return locale.replace('-', '_')


def _contextual_locale(context):
    """Return locale from the context, falling back to a default if invalid."""
    locale = context['request'].locale
    if not localedata.exists(locale):
        locale = settings.LANGUAGE_CODE
    return locale


@register.function
@jinja2.contextfunction
def datetimeformat(context, value, format='shortdatetime'):
    """
    Returns date/time formatted using babel's locale settings. Uses the
    timezone from settings.py
    """
    if not isinstance(value, datetime.datetime):
        # Expecting date value
        raise ValueError

    tzinfo = timezone(settings.TIME_ZONE)
    tzvalue = tzinfo.localize(value)
    locale = _babel_locale(_contextual_locale(context))

    # If within a day, 24 * 60 * 60 = 86400s
    if format == 'shortdatetime':
        # Check if the date is today
        if value.toordinal() == datetime.date.today().toordinal():
            formatted = _lazy(u'Today at %s') % format_time(
                                    tzvalue, format='short', locale=locale)
        else:
            formatted = format_datetime(tzvalue, format='short', locale=locale)
    elif format == 'longdatetime':
        formatted = format_datetime(tzvalue, format='long', locale=locale)
    elif format == 'date':
        formatted = format_date(tzvalue, locale=locale)
    elif format == 'time':
        formatted = format_time(tzvalue, locale=locale)
    elif format == 'datetime':
        formatted = format_datetime(tzvalue, locale=locale)
    else:
        # Unknown format
        raise DateTimeFormatError

    return jinja2.Markup('<time datetime="%s">%s</time>' % \
                         (tzvalue.isoformat(), formatted))


def _get_format():
    lang = translation.get_language()
    locale = Locale(translation.to_locale(lang))
    return Format(locale)


@register.filter
def numberfmt(num, format=None):
    return _get_format().decimal(num, format)
