from masuda import const
from masudaapi.models import HatenaUser

def get():
    user = HatenaUser.objects.filter(hatena_id=const.HATENA['ID']).first()
    return user

def get_or_create():
    user = get()
    if not user:
        user = HatenaUser.objects.create(hatena_id=const.HATENA["ID"])
    return user