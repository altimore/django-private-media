# -*- coding: utf-8 -*-
import mimetypes
import os

from django.conf import settings
from django.http import HttpResponse


class NginxXAccelRedirectServer(object):
    def serve(self, request, path):
        response = HttpResponse()
        fullpath = os.path.join(settings.PRIVATE_MEDIA_ROOT, path)
        response["X-Accel-Redirect"] = fullpath
        response["Content-Type"] = (
            mimetypes.guess_type(path)[0] or "application/octet-stream"
        )
        return response


class ApacheXSendfileServer(object):
    def serve(self, request, path):
        fullpath = os.path.join(settings.PRIVATE_MEDIA_ROOT, path)
        response = HttpResponse()
        response["X-Sendfile"] = fullpath

        # From django-filer (https://github.com/stefanfoulis/django-filer/):
        # This is needed for lighttpd, hopefully this will
        # not be needed after this is fixed:
        # http://redmine.lighttpd.net/issues/2076
        response["Content-Type"] = (
            mimetypes.guess_type(path)[0] or "application/octet-stream"
        )

        # filename = os.path.basename(path)
        # response['Content-Disposition'] = smart_str(u'attachment; filename={0}'.format(filename))

        return response


import stat

from django.http import Http404, HttpResponseNotModified
from django.utils.http import http_date
from django.views.static import was_modified_since


class DefaultServer(object):
    """
    Serve static files from the local filesystem through django.
    This is a bad idea for most situations other than testing.

    This will only work for files that can be accessed in the local filesystem.
    """

    def serve(self, request, path):
        # the following code is largely borrowed from `django.views.static.serve`
        # and django-filetransfers: filetransfers.backends.default
        fullpath = os.path.join(settings.PRIVATE_MEDIA_ROOT, path)
        if not os.path.exists(fullpath):
            raise Http404('"{0}" does not exist'.format(fullpath))
        # Respect the If-Modified-Since header.
        statobj = os.stat(fullpath)
        content_type = mimetypes.guess_type(fullpath)[0] or "application/octet-stream"
        if not was_modified_since(
            request.META.get("HTTP_IF_MODIFIED_SINCE"), statobj[stat.ST_MTIME]
        ):
            return HttpResponseNotModified(content_type=content_type)
        response = HttpResponse(open(fullpath, "rb").read(), content_type=content_type)
        response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
        # filename = os.path.basename(path)
        # response['Content-Disposition'] = smart_str(u'attachment; filename={0}'.format(filename))
        return response
