import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

env_path = os.path.join(Path(__file__).resolve().parent, 'secret_key.env')
if not os.path.isfile(env_path):
    secret_key = get_random_secret_key()
    print(secret_key)
    with open(env_path, mode='w') as f:
        f.write('SECRET_KEY=' + secret_key)