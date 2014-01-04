import logging

from django.core.management.base import NoArgsCommand
from watch.models import Watch


class Command(NoArgsCommand):
    help = 'Updates all the watched routes/stops.'

    def handle_noargs(self, **options):

        # setup logging
        verbosity = int(options['verbosity'])

        if verbosity >= 2:
            log_level = logging.DEBUG
        elif verbosity >= 1:
            log_level = logging.INFO
        else:
            log_level = logging.ERROR

        h = logging.StreamHandler()
        h.setLevel(log_level)
        h.setFormatter(logging.Formatter('%(asctime)s %(name)s[%(levelname)s]: %(message)s'))
        logging.getLogger().addHandler(h)

        # do stuff
        Watch.objects.refresh()
