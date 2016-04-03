# -*- coding: utf-8 -*-


import atexit


try:
    import pgi
except ImportError:
    pgi = None
else:
    pgi.install_as_gi()

    import gi

    gi.require_version("Notify", "0.7")

    from gi.repository import Notify

    Notify.init("concierge")
    atexit.register(Notify.uninit)


def dummy_notifier(_):
    pass


notifier = dummy_notifier

if pgi:
    def libnotify_notifier(problem):
        Notify.Notification.new("concierge", problem, None).show()

    notifier = libnotify_notifier
