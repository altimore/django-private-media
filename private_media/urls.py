from django.conf import settings
from django.urls import re_path

from .views import serve_private_file

urlpatterns = [
    re_path(
        r"^{0}(?P<path>.*)$".format(settings.PRIVATE_MEDIA_URL.lstrip("/")),
        serve_private_file,
    ),
]
