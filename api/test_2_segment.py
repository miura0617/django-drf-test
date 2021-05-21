# Segments関係のテストコードを書くファイル
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Segment
from .serializers import SegmentSerializer

# エンドポイントをあらかじめ定義しておく

SEGMENTS_URL = '/api/segments/'

# segmentを作成する関数
def create_segment(segment_name):
    return Segment.objects.create(segment_name=segment_name)

# ★★urlのパスを生成する
def detail_url(segment_id):
    # ★★★reverseメソッドにsegment-detailとすると、「api/segments/2/」の形のURLを自動的に生成してくれる
    return reverse('api:segment-detail', args=[segment_id])

# 認証済みの状態のテスト
class AuthorizedSegmentApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # GETメソッドによるsegment一覧の取得をテスト
    def test_2_1_should_get_all_segments(self):
        # あらかじめ2つsegmentを作成
        create_segment(segment_name="SUV")
        create_segment(segment_name="Sedan")

        res = self.client.get(SEGMENTS_URL)
        # reseの内容が、あらかじめ定義した2つのsegment名と一致するか
        # resはdict型
        # DBの中身は取り出したあと、serializerを通してdict型にする必要あり
        segments = Segment.objects.all().order_by('id')
        serializer = SegmentSerializer(segments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # dict型同士の比較
        self.assertEqual(res.data, serializer.data)

    # GETメソッドで特定のsegment情報を取得する
    def test_2_2_should_get_single_segment(self):
        segment = create_segment(segment_name="SUV")
        # URL取得(/api/segments/2 )
        url = detail_url(segment.id)
        print(url)
        res = self.client.get(url)

        # DBの内容とresの内容が一致するか確認する
        serializer = SegmentSerializer(segment)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # 新しいsegmentを作成できるか確認する
    def test_2_3_should_create_new_segment_successfully(self):
        payload = {'segment_name': 'K-Car'}
        res = self.client.post(SEGMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # POSTしたpayloadがDBに書き込まれているか検索する
        exists = Segment.objects.filter(
            segment_name=payload['segment_name']
        ).exists()
        self.assertTrue(exists)

    # 新しいsegmentを作成するときに、空名を使うとBad requestになることを確認
    def test_2_4_should_not_create_new_segment_with_invalid(self):
        payload = {'segment_name': ''}
        res = self.client.post(SEGMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # PATCHのテスト
    def test_2_5_should_partial_update_segment(self):
        # PATCHメソッドをテストするため、既存のsegmentを作成しておく
        segment = create_segment(segment_name="SUV")
        payload = {'segment_name': 'Compact SUV'}
        url = detail_url(segment.id)
        self.client.patch(url, payload)
        # segment変数は、create_segment（）したときの"SUV"が入ったままなので
        # 最新のDBの状態に更新する
        segment.refresh_from_db()
        self.assertEqual(segment.segment_name, payload['segment_name'])

    # PUTのテスト
    def test_2_6_should_update_segment(self):
        # PATCHメソッドをテストするため、既存のsegmentを作成しておく
        segment = create_segment(segment_name="SUV")
        payload = {'segment_name': 'Compact SUV'}
        url = detail_url(segment.id)
        self.client.put(url, payload)
        # segment変数は、create_segment（）したときの"SUV"が入ったままなので
        # 最新のDBの状態に更新する
        segment.refresh_from_db()
        self.assertEqual(segment.segment_name, payload['segment_name'])

    # Deleteのテスト
    def test_2_7_should_delete_segment(self):
        segment = create_segment(segment_name="SUV")
        # DB内のsegmentの数が1かどうか判定
        self.assertEqual(1, Segment.objects.count())
        # URLを取得
        url = detail_url(segment.id)
        self.client.delete(url)
        # Deleteがうまくいっていれば、DB内のsegmentの数は0になっているはず
        self.assertEqual(0, Segment.objects.count())


# ログイン認証されていない場合のテスト
class UnauthorizedSegmentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    # Token認証が通っていないユーザでGETメソッドでsegment一覧を取得してもとれないこと
    def test_2_8_should_not_get_segments_when_unautherized(self):
        res = self.client.get(SEGMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
