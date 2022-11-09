from rest_framework import routers
from .views import HatenaUserViewSet, PostViewSet

router = routers.DefaultRouter()
router.register(r'hatena_users', HatenaUserViewSet)
router.register(r'posts', PostViewSet)