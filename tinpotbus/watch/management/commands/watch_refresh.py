import logging
from optparse import make_option
import sys
import time

from django.core.management.base import NoArgsCommand
from watch.models import Watch


class Command(NoArgsCommand):
    help = 'Updates all the watched routes/stops.'

    option_list = NoArgsCommand.option_list + (
        make_option('--loop',
                    action='store',
                    dest='loop',
                    type='int',
                    default=None,
                    help='Refresh continously every LOOP seconds.',
                    metavar='LOOP'),
    )

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
        L = logging.getLogger('tinpotbus')
        L.addHandler(h)
        L.setLevel(log_level)

        MAX_BACKOFF = 20  # multiple of the loop time
        loop_time = options['loop']
        while True:
            # do stuff
            stats = Watch.objects.refresh()

            if not loop_time:
                break
            else:
                if stats == 0.0:
                    loop_time = min(loop_time * 2, options['loop'] * MAX_BACKOFF)
                else:
                    loop_time = options['loop']

                if verbosity >= 2:
                    print >>sys.stderr, "Sleeping for %d seconds" % loop_time

                try:
                    time.sleep(loop_time)
                except KeyboardInterrupt:
                    break
