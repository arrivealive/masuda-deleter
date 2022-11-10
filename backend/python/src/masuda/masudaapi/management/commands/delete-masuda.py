from django.core.management.base import BaseCommand, CommandParser
from ...lib import Masuda
from masudaapi.models import Progress
import logging

class Command(BaseCommand):
    help = 'Delete a post'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('id', type=int)
        parser.add_argument('-p', '--progress', type=int, help='progress id')
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        try:
            masuda = Masuda.Masuda()
            id = options['id']
            progress_id = options['progress']
            if progress_id:
                progress = Progress.objects.filter(id=progress_id).first()
                if progress:
                    masuda.set_progress(progress)

            result = masuda.delete_one(id)
        except Exception as e:
            logger.exception('exception occurred')
            masuda.set_error_message(e)
            result = False

        if result:
            return 'success'
        return 'failure'