# -*- coding: utf-8 -*-

import os
import re

import six
from django.conf import settings
from django.core.validators import EMPTY_VALUES

from .remove import remove_media
from .utils import get_file_fields


def get_used_media():
    """
        Get media which are still used in models
    """

    media = set()

    for field in get_file_fields():
        print("Examining {0}".format(field))
        is_null = {
            '%s__isnull' % field.name: True,
        }
        is_empty = {
            '%s' % field.name: '',
        }

        storage = field.storage

        for file_model_obj in field.model.objects \
                .exclude(**is_empty).exclude(**is_null):
            this_file = getattr(file_model_obj, field.name)
            if this_file.name not in EMPTY_VALUES:
                media.add(storage.path(this_file.name))
            if hasattr(field, "variations"):
                print("Considering variations for {0}".format(field))
                for v in field.variations.keys():
                    variation_name = this_file.get_variation_name(this_file.name, v)
                    media.add(storage.path(variation_name))

    return media


def get_all_media(exclude=None):
    """
        Get all media from MEDIA_ROOT
    """

    if not exclude:
        exclude = []

    media = set()

    for root, dirs, files in os.walk(six.text_type(settings.MEDIA_ROOT)):
        for name in files:
            path = os.path.abspath(os.path.join(root, name))
            relpath = os.path.relpath(path, settings.MEDIA_ROOT)
            for e in exclude:
                if re.match(r'^%s$' % re.escape(e).replace('\\*', '.*'), relpath):
                    break
            else:
                media.add(path)

    return media


def get_unused_media(exclude=None):
    """
        Get media which are not used in models
    """

    if not exclude:
        exclude = []

    all_media = get_all_media(exclude)
    used_media = get_used_media()

    return all_media - used_media


def remove_unused_media():
    """
        Remove unused media
    """
    remove_media(get_unused_media())
