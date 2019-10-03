# -*- coding: utf-8 -*-
from django.dispatch import Signal


user_logged_in = Signal(providing_args=['instance', 'request'])
