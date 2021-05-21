# User関係のテストコードを書くファイル
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

# エンドポイントをあらかじめ定義しておく

CREATE_USER_URL = '/api/create/'
PROFILE_URL = '/api/profile/'
TOKEN_URL = '/api/auth/'

###########################33##########3
# テストケース
###########################33##########3

# Token認証が終わったあとの処理についてテスト
# 各テストはメソッドの形で書くことができる
class AuthorizedUserApiTests(TestCase):
    # setupは各テストのはじめに絶対実行されるメソッド
    def setUp(self):
        # dummyユーザを作成
        self.user = get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        # clienntを作る
        self.client = APIClient()
        # dummyユーザで認証を強制的に通す
        self.client.force_authenticate(user=self.user)

    # profileエンドポイントでユーザ情報取得できるか確認する
    def test_1_1_should_get_user_profile(self):
        # GETメソッドで/api/profile/にアクセスし、情報を取得できるか確認する
        res = self.client.get(PROFILE_URL)
        # ステータスコードをチェック
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # ユーザ情報(id, username)が一致するか確認する
        self.assertEqual(res.data, {
            'id': self.user.id,
            'username': self.user.username,
        })

    # profileエンドポイントへのアクセスは、Update/Patchは禁止にしたことを確認
    def test_1_2_should_not_allowed_by_PUT(self):
        # PUTで渡すJSON内容をpayloadで定義
        payload = {
            'username': 'dummy',
            'password': 'dummy_pw',
        }
        res = self.client.put(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_1_3_should_not_allowed_by_PATCH(self):
        # PATCHで渡すJSON内容をpayloadで定義
        payload = {
            'username': 'dummy',
            'password': 'dummy_pw',
        }
        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

# Token認証が通っていないユーザに対するテスト
class UnauthorizedUserApiTests(TestCase):
    def setUp(self):
        # 認証の必要がないので、clientだけ用意
        self.client = APIClient()

    # POSTメソッドでcreateエンドポイントにアクセスし、ユーザ作成できるか確認する
    def test_1_4_should_create_new_user(self):
        payload = {
            'username': 'dummy',
            'password': 'dummy_pw',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # DBからユーザオブジェクトを取得してくる
        user = get_user_model().objects.get(**res.data)
        # usernameとハッシュ化されたpasswordが格納される
        # userで持ってきたpasswordと、payloadのpasswordが一致するか確認
        self.assertTrue(
            user.check_password(payload['password'])
        )
        # passwordはwrite_onlyでレスポンスにはpasswordが入ってこないことを確認
        self.assertNotIn('password', res.data)

    # usernameがDB上にすでに存在する場合にcreateするとはじくか確認する
    def test_1_5_should_not_create_user_by_same_credentials(self):
        payload = {
            'username': 'dummy',
            'password': 'dummy_pw',
        }
        # dummyユーザを事前に作成しておく
        get_user_model().objects.create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        # BAD requestが返ってくるか確認
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # passowrdに入力最低文字数を6に指定していたことを確認する
    def test_1_6_should_not_create_user_with_short_pw(self):
        payload = {
            'username': 'dummy',
            'password': 'pw',
        }
        # passwordが6文字未満であれば、ユーザ作成できないはずなので確認する
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Tokenを取得できるかテスト
    def test_1_7_should_response_token(self):
        # token取得するためにはユーザを作成しておく必要がある
        payload = {
            'username': 'dummy',
            'password': 'pw',
        }
        get_user_model().objects.create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        # res.dataの中に'token'という要素があるか確認しています
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # Tokenを取得できないことを確認
    # 正しくないpasswordでPOSTしたときに、Tokenが取得できないことを確認する
    def test_1_8_should_not_response_token_with_invalid_credentials(self):
        get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        payload = {
            'username': 'dummy',
            'password': 'wrong',
        }
        res = self.client.post(TOKEN_URL, payload)
        # res.dataに'token'が含まれないことを確認
        self.assertNotIn('token', res.data)
        # status_codeが400のBad requestであることを確認
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # 存在しないユーザでPOSTしても、TOKENが返ってこないことを確認
    def test_1_9_should_not_response_token_with_non_exist_credentials(self):
        payload = {'username': 'dummy', 'password': 'dummy_pw'}
        res = self.client.post(TOKEN_URL, payload)

        # res.dataに'token'が含まれないことを確認
        self.assertNotIn('token', res.data)
        # status_codeが400のBad requestであることを確認
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # usernameはあるか、passwordが空の場合も、Tokenが返ってこないことを確認する
    def test_1__10_should_not_response_token_with_missing_field(self):
        payload = {'username': 'dummy', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)
        # res.dataに'token'が含まれないことを確認
        self.assertNotIn('token', res.data)
        # status_codeが400のBad requestであることを確認
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # usernameが空、passwordも空の場合も、Tokenが返ってこないことを確認する
    def test_1__11_should_not_response_token_with_missing_field(self):
        payload = {'username': '', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)
        # res.dataに'token'が含まれないことを確認
        self.assertNotIn('token', res.data)
        # status_codeが400のBad requestであることを確認
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Token認証していないときにprofileエンドポイントにアクセスできないことを確認する
    def test_1__12_should_not_get_user_profile_when_unauthorized(self):
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
