from django.shortcuts import render
from rest_framework import generics, permissions, viewsets, status
# 作成したserializerをインポート
from .serializers import UserSerializer, SegmentSerializer, BrandSerializer, VehicleSerializer
# 作成したモデルもインポート
from .models import User, Segment, Brand, Vehicle
# DRFのresponseをインポート
from rest_framework.response import Response


# Create your views here.

#　新規ユーザを作成するView
## 継承元にはgenerics配下とviewsets配下の2通りある
## CRUDのうち特定の機能だけを実装したいときはgenericsから
## CRUD全部を実装したいときはviewsetsから継承するとよい
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    # settins.pyのREST_FRAMEWORK変数で設定した認証を上書きする
    # 新規ユーザ作成するときは、ログインユーザ以外でも作れるようにしたいから
    permission_classes = (permissions.AllowAny,)

# ログインしているユーザ情報を返すView
# ログインしているユーザ情報を検索して返したいので、RetrieveUpdateAPIViewを継承
class ProfileUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    # ログインしているユーザのオブジェクトを返したいのでget_object()を上書き
    def get_object(self):
        # request.userがログインしているユーザを意味している
        return self.request.user

    # RetrieveUpdateAPIViewを継承しているが、
    # UpdateとPatchメソッドは使わないので、エラーを返すように上書きする
    def update(self, request, *args, **kwargs):
        response = {'message': 'PUT method is not allowed'}
        # ステータスを405番のMETHOD_NOT_ALLOWEDを返す
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        response = {'message': 'PATCH method is not allowed'}
        # ステータスを405番のMETHOD_NOT_ALLOWEDを返す
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# SegmentのViewにはCRUDすべて使用できるようにしたいので、viewsetsから継承する
class SegmentViewSet(viewsets.ModelViewSet):
    # querysetにオブジェクト一覧を割り当てる
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer

# BrandのViewも同様にCRUDすべて使用
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

# VehicleのView
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    # Vehicleを新規作成するとき、Vehicleのuser属性にDjango側でログイン中のユーザを自動的に設定して作成するには
    # perform_create()メソッドをオーバライトする
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




