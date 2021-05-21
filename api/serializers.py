from rest_framework import serializers
from .models import Segment, Brand, Vehicle
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    # serializerの設定は、Metaクラスの中に書いていく決まり
    class Meta:
        # UserSerializerに対応するモデルを指定
        model = User
        fields = ['id', 'username', 'password']
        # 追加の設定は、extra_kwargsにする
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True,
                'min_length': 5,
            }
        }

    def create(self, validated_data):
        # Userのcreate_userメソッドがパスワードのハッシュ化を行ってくれる
        # 引数validated_dataは、usernameとpasswordが入ってきます
        # 辞書型をメソッドの引数に直接入れることができないので、**validated_dataというような表記をする
        user = User.objects.create_user(**validated_data)
        return user

class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ['id', 'segment_name']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'brand_name']

class VehicleSerializer(serializers.ModelSerializer):
    # ReadOnlyFieldメソッドを使って、紐付いているオブジェクトが持っている特定の属性にアクセスできます
    segment_name = serializers.ReadOnlyField(source='segment.segment_name', read_only=True)
    brand_name = serializers.ReadOnlyField(source='brand.brand_name', read_only=True)

    class Meta:
        model = Vehicle
        # ForeignKeyのsegment, brandはIDなので、名前を取得するために'segment_name'と'brand_name'をカスタムで作る
        fields = ['id', 'vehicle_name', 'release_year', 'price', 'segment', 'brand', 'segment_name', 'brand_name']
        # Vehicleオブジェクトを新規作成したとき、ログインしているユーザをUserに自動的に設定する
        extra_kwargs = {
            'user': {
                'read_only': True
            }
        }
