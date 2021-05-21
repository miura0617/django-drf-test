from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Segment(models.Model):
    segment_name = models.CharField(max_length=100)

    def __str__(self):
        return self.segment_name

class Brand(models.Model):
    brand_name = models.CharField(max_length=100)

    def __str__(self):
        return self.brand_name

class Vehicle(models.Model):
    # userの属性にDjangoのUserモデルを適用する
    # CASCADEを設定してUserが削除された場合、関連付けられたuser属性も削除されるようにする
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    vehicle_name = models.CharField(max_length=100)
    release_year = models.IntegerField()
    # priceは小数点以下も使用できるようにdecimalを使う
    # decimal_placesは、小数点以下の桁数を意味する
    # max_digitsは、上記の小数点2桁も含めた最大桁数を意味する
    # 上記より, 9999.99まで表現できるようになっています
    price = models.DecimalField(max_digits=6, decimal_places=2)
    segment = models.ForeignKey(
        Segment,
        on_delete=models.CASCADE
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.vehicle_name
