from django.urls import path, include
# DRFのtoken認証するため
from rest_framework.authtoken.views import obtain_auth_token
# DRFのrouterを使う
from rest_framework.routers import DefaultRouter
# Viewのインポート
from . import views


# viewでviewsets配下を継承してきたものは、DRFのrouterを使ってエンドポイントを決める
router = DefaultRouter()
router.register('segments', views.SegmentViewSet)
router.register('brands', views.BrandViewSet)
router.register('vehicles', views.VehicleViewSet)

app_name = 'api'

# viewでgenerics配下を継承してきたものは、urlpatternsに設定していく
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('profile/', views.ProfileUserView.as_view(), name='profile'),
    # tokenを返してくれるエンドポイント
    # usernameとpasswordでアクセスしたときに、そのユーザのtokenを取得する
    # DRFで標準で備わっているobtain_auth_tokenというviewを紐付けることで実現可能
    path('auth/', obtain_auth_token, name='auth'),
    # routerのパスへアクセスがあった場合、routerに飛ばす
    path('', include(router.urls)),
]
