# brands関係のテストコードを書くファイル
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Vehicle, Brand, Segment
from .serializers import VehicleSerializer
from decimal import Decimal

# エンドポイントをあらかじめ定義しておく
VEHICLES_URL = '/api/vehicles/'
BRANDS_URL = '/api/brands/'
SEGMENTS_URL = '/api/segments/'


# segmentを作成する関数
def create_segment(segment_name):
    return Segment.objects.create(segment_name=segment_name)

# brandを作成する関数
def create_brand(brand_name):
    return Brand.objects.create(brand_name=brand_name)

def create_vehicle(user, **params):
    defaults = {
        'vehicle_name': 'MODEL S',
        'release_year': 2019,
        'price': 500.00,
    }
    defaults.update(params)

    return Vehicle.objects.create(user=user, **defaults)


def detail_seg_url(segment_id):
    return reverse('api:segment-detail', args=[segment_id])

def detail_brand_url(brand_id):
    return reverse('api:brand-detail', args=[brand_id])

def detail_vehicle_url(vehicle_id):
    return reverse('api:vehicle-detail', args=[vehicle_id])


class AuthorizedVehicleApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # GETでvehicle一覧を取得できるか
    def test_4_1_should_get_vehicles(self):
        # vehicleを作るためには、brandとsegmentが存在する必要がある
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        # vehicleを2つ作る
        create_vehicle(user=self.user, segment=segment, brand=brand)
        create_vehicle(user=self.user, segment=segment, brand=brand)
        # エンドポイントへアクセス
        res = self.client.get(VEHICLES_URL)
        vehicles = Vehicle.objects.all().order_by('id')
        serializer = VehicleSerializer(vehicles, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_4_2_get_single_vehicle(self):
        # vehicleを作るためには、brandとsegmentが存在する必要がある
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        # vehicle作る
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)
        # urlを取得し、GETする
        url = detail_vehicle_url(vehicle.id)
        res = self.client.get(url)
        serializer = VehicleSerializer(vehicle)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # POSTで新規Vehicle作成できるか
    def test_4_3_should_create_new_vehicle_successfully(self):
        # vehicleを作るためには、brandとsegmentが存在する必要がある
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        # POST
        payload = {
            'vehicle_name': 'MODEL S',
            'release_year': 2019,
            'price': 500.12,
            'segment': segment.id,
            'brand': brand.id,
        }
        res = self.client.post(VEHICLES_URL, payload)
        # DB内容を取得
        vehicle = Vehicle.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # DB内容とpayloadで渡したparamsが一致するか確認
        self.assertEqual(payload['vehicle_name'], vehicle.vehicle_name)
        self.assertEqual(payload['release_year'], vehicle.release_year)

        # self.assertEqual(payload['price'], vehicle.price)
        # priceの判定がDecimalとFloatが比較できずに上手くテスト出来ていませんでした。
        # 【対策】
        # Step 1. import Decimalの追加
        # price の assertion 式の変更
        # ・assertEqual から assertAlmostEqualへ変更
        # ・payload['price']をDecimalにキャスト
        # ・第三引数に 2 を追加 -> 小数点2桁まで一致しているか評価してくれます。
        self.assertAlmostEqual(Decimal(payload['price']),  vehicle.price, 2)

        self.assertEqual(payload['segment'], vehicle.segment.id)
        self.assertEqual(payload['brand'], vehicle.brand.id)

    # vehicle作成できない
    def test_4_4_should_not_create_vehicle_with_invalid(self):
        payload = {
            'vehicle_name': 'MODEL S',
            'release_year': 2019,
            'price': 500.00,
            'segment': '',
            'brand': '',
        }
        res = self.client.post(VEHICLES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Patch
    def test_4_5_should_partial_update_vehicle(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)

        payload = {'vehicle_name': 'MODE X'}
        url = detail_vehicle_url(vehicle.id)

        self.client.patch(url, payload)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.vehicle_name, payload['vehicle_name'])

    # PUT
    def test_4_6_should_update_vehicle(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)

        payload = {
            'vehicle_name': 'MODEL X',
            'release_year': 2019,
            'price': 500.00,
            'segment': segment.id,
            'brand': brand.id,
        }

        url = detail_vehicle_url(vehicle.id)
        self.assertEqual(vehicle.vehicle_name, 'MODEL S')

        self.client.put(url, payload)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.vehicle_name, payload['vehicle_name'])

    # Deleteのテスト
    def test_4_7_should_delete_vehicle(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)
        # DB内のvehicleの数が1かどうか判定
        self.assertEqual(1, Vehicle.objects.count())
        # URLを取得
        url = detail_vehicle_url(vehicle.id)
        self.client.delete(url)
        # Deleteがうまくいっていれば、DB内のvehicleの数は0になっているはず
        self.assertEqual(0, Vehicle.objects.count())


    # カスケードdelete(1)
    def test_4_8_should_cascade_delete_vehicle_by_segment_delete(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)
        # DB内のvehicleの数が1かどうか判定
        self.assertEqual(1, Vehicle.objects.count())

        # segment='Sedan'のセグメントが削除されたら、vehicleも削除されるか
        url = detail_seg_url(segment.id)
        self.client.delete(url)
        self.assertEqual(0, Vehicle.objects.count())

    # カスケードdelete(2)
    def test_4_9_should_cascade_delete_vehicle_by_brand_delete(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)
        # DB内のvehicleの数が1かどうか判定
        self.assertEqual(1, Vehicle.objects.count())

        # segment='Sedan'のセグメントが削除されたら、vehicleも削除されるか
        url = detail_brand_url(brand.id)
        self.client.delete(url)
        self.assertEqual(0, Vehicle.objects.count())


class UnauthorizedVehicleApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_4__10_should_not_get_vehicles_when_unauthorized(self):
        res = self.client.get(VEHICLES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

