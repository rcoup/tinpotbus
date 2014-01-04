from django.core.management.base import NoArgsCommand
from watch.models import Watch


class Command(NoArgsCommand):
    help = 'Updates all the watched routes/stops.'

    def handle_noargs(self, **options):
        Watch.objects.refresh()
