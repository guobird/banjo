from banjo import Router
from . import views

router = Router()

router.url('/about', views.user_view, 'get')