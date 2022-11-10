from django.core.management.base import BaseCommand, CommandParser
from ...lib import Masuda
from masudaapi.models import Progress
import logging

class Command(BaseCommand):
    help = 'Fetch posts'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('page_from', type=int)
        parser.add_argument('page_to', type=int)
        parser.add_argument('-p', '--progress', type=int, help='progress id')
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        try:
            masuda = Masuda.Masuda()
            page_from = options['page_from']
            page_to = options['page_to']
            progress_id = options['progress']
            if progress_id:
                progress = Progress.objects.filter(id=progress_id).first()
                if progress:
                    masuda.set_progress(progress)

            result = masuda.fetch(page_from, page_to)
        except Exception as e:
            logger.exception('exception occurred')
            masuda.set_error_message(e)
            result = False

        if result:
            return 'success'
        return 'failure'