# brands関係のテストコードを書くファイル
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Brand
from .serializers import BrandSerializer

# エンドポイントをあらかじめ定義しておく

BRANDS_URL = '/api/brands/'


# brandを作成する関数
def create_brand(brand_name):
    return Brand.objects.create(brand_name=brand_name)

# ★★urlのパスを生成する
def detail_url(brand_id):
    # ★★★reverseメソッドにbrand-detailとすると、「api/brands/2/」の形のURLを自動的に生成してくれる
    return reverse('api:brand-detail', args=[brand_id])

# 認証済みの状態のテスト
class AuthorizedBrandApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # GETでbrand一覧を取得する
    def test_3_1_should_get_brand(self):
        create_brand(brand_name='Tesla')
        create_brand(brand_name='Toyota')
        res = self.client.get(BRANDS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        brands = Brand.objects.all().order_by('id')
        serializer = BrandSerializer(brands, many=True)
        self.assertEqual(res.data, serializer.data)


    # GETメソッドで特定のbrand情報を取得する
    def test_3_2_should_get_single_brand(self):
        brand = create_brand(brand_name="Tesla")
        # URL取得(/api/brands/2 )
        url = detail_url(brand.id)
        print(url)
        res = self.client.get(url)

        # DBの内容とresの内容が一致するか確認する
        serializer = BrandSerializer(brand)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # 新規でbrandを作成できるか
    def test_3_3_should_create_new_brand_successfully(self):
        payload = {'brand_name': 'Audi'}
        res = self.client.post(BRANDS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # POSTしたpayloadがDBに書き込まれているか検索する
        exists = Brand.objects.filter(
            brand_name=payload['brand_name']
        ).exists()
        self.assertTrue(exists)

    # 新しいbrandを作成するときに、空名を使うとBad requestになることを確認
    def test_3_4_should_not_create_new_brand_with_invalid(self):
        payload = {'brand_name': ''}
        res = self.client.post(BRANDS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # PATCHのテスト
    def test_3_5_should_partial_update_brand(self):
        # PATCHメソッドをテストするため、既存のbrandを作成しておく
        brand = create_brand(brand_name="Toyota")
        payload = {'brand_name': 'Lexus'}
        url = detail_url(brand.id)
        self.client.patch(url, payload)
        # brand変数は、create_brand（）したときの"SUV"が入ったままなので
        # 最新のDBの状態に更新する
        brand.refresh_from_db()
        self.assertEqual(brand.brand_name, payload['brand_name'])

    # PUTのテスト
    def test_3_6_should_update_brand(self):
        # PATCHメソッドをテストするため、既存のbrandを作成しておく
        brand = create_brand(brand_name="Toyota")
        payload = {'brand_name': 'Lexus'}
        url = detail_url(brand.id)
        self.client.put(url, payload)
        # brand変数は、create_brand（）したときの"SUV"が入ったままなので
        # 最新のDBの状態に更新する
        brand.refresh_from_db()
        self.assertEqual(brand.brand_name, payload['brand_name'])

    # Deleteのテスト
    def test_3_7_should_delete_brand(self):
        brand = create_brand(brand_name="Toyota")
        # DB内のbrandの数が1かどうか判定
        self.assertEqual(1, Brand.objects.count())
        # URLを取得
        url = detail_url(brand.id)
        self.client.delete(url)
        # Deleteがうまくいっていれば、DB内のbrandの数は0になっているはず
        self.assertEqual(0, Brand.objects.count())


# ログイン認証されていない場合のテスト
class UnauthorizedBrandApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    # Token認証が通っていないユーザでGETメソッドでbrand一覧を取得してもとれないこと
    def test_3_8_should_not_get_brands_when_unautherized(self):
        res = self.client.get(BRANDS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
