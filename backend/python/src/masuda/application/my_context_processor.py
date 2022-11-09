from masuda import const
from django.conf import settings

import logging
def common(request):
  # logger = logging.getLogger(__name__)
  # logger.info(request.resolver_match.app_name)
  app_name = request.resolver_match.app_name
  site_name = ''
  company_name = ''
  if app_name == 'web':
    site_name = 'Masuda Deleter'
    company_name = ''
  if app_name == 'dummy':
    site_name = '縺ｯ縺ｦ縺ｪ蛹ｿ蜷ダイアリー'
    company_name = '縺ｯ縺ｦ縺ｪ'

  return {
    'current_hatena_id': const.HATENA['ID'],
    'app_name': request.resolver_match.app_name,
    'site_name': site_name,
    'company_name': company_name
  }