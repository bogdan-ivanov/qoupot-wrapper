import json
import requests
import logging


class QoupotResource(dict):
    key_name = None
    list_url = None
    detail_url = None

    @classmethod
    def get_list(cls, page=None, api_key=None, url_prefix='http://app.qoupot.io'):
        url = url_prefix + cls.list_url
        params = {'page': page, 'token': api_key}
        url += '?' + '&'.join('%s=%s' % (key, value) for key, value in params.items() if value is not None)

        response = requests.get(url)
        if response.status_code != 200:
            return []

        try:
            data = json.loads(response.content)
        except ValueError:
            return []

        return [cls(api_key, url_prefix, obj) for obj in data['results']]

    @classmethod
    def get_detail(cls, key, api_key=None, url_prefix='http://app.qoupot.io'):
        url = url_prefix + (cls.detail_url % key)

        params = {'token': api_key}
        url += '?' + '&'.join('%s=%s' % (key, value) for key, value in params.items() if value is not None)

        response = requests.get(url)
        if response.status_code != 200:
            return None

        try:
            data = json.loads(response.content)
        except ValueError:
            return None

        return cls(data)

    def __init__(self, api_key, url_prefix, *args, **kwargs):
        self.api_key = api_key
        self.url_prefix = url_prefix
        super(QoupotResource, self).__init__(*args, **kwargs)

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)

    def to_dict(self):
        return dict(self)


class DiscountCode(QoupotResource):
    key_name = 'code'
    list_url = '/api/v1/coupons/'
    detail_url = '/api/v1/coupons/%s/'


class RedeemRecord(QoupotResource):
    key_name = 'uuid'
    list_url = '/api/v1/records/'
    detail_url = '/api/v1/records/%s/'


class QoupotAPI(object):
    def __init__(self, api_key):
        self.API_KEY = api_key
        self.URL_PREFIX = 'http://localhost:8000'

    def get(self, code):
        response = requests.get(self.URL_PREFIX + "/api/v1/coupons/%s/?token=%s" % (code, self.API_KEY),
                                headers={'content-type': 'application/json'})

        try:
            data = json.loads(response.content)
        except ValueError:
            return None

        if response.status_code == 200:
            discount_code = DiscountCode(self.API_KEY, self.URL_PREFIX, data)
            return discount_code

    def check(self, code, client=None, product=None, **kwargs):
        """
        :param code:
        :param client:
        :param product:
        :param kwargs:
        :return:
        """

        data = {}
        if client:
            data['client'] = client

        if product:
            data['product'] = product

        response = requests.post(self.URL_PREFIX + "/api/v1/coupons/%s/check/?token=%s" % (code, self.API_KEY),
                                 headers={'content-type': 'application/json'},
                                 data=json.dumps(data))

        try:
            redeem_data = json.loads(response.content)
        except ValueError:
            redeem_data = {}

        if response.status_code != 200:
            logging.warning("Code \"%s\" could not be redeemed - code=%s - message=\"%s\"" % (
                code, redeem_data.get('code', 100), redeem_data.get('message', '')))

            return None, redeem_data.get('code', 100), redeem_data.get('message', '')

        # If the discount is redeemable, retrieve it
        discount_code = self.get(code)
        return discount_code, None, None

    def redeem(self, code, client=None, product=None, **kwargs):
        data = {}
        if client:
            data['client'] = client

        if product:
            data['product'] = product

        response = requests.post(self.URL_PREFIX + "/api/v1/coupons/%s/redeem/?token=%s" % (code, self.API_KEY),
                                 headers={'content-type': 'application/json'},
                                 data=json.dumps(data))

        try:
            redeem_data = json.loads(response.content)
        except ValueError:
            redeem_data = {}

        if response.status_code != 200:
            logging.warning("Code \"%s\" could not be redeemed - code=%s - message=\"%s\"" % (
                code, redeem_data.get('code', 100), redeem_data.get('message', '')))

            return None, redeem_data.get('code', 100), redeem_data.get('message', '')

        return RedeemRecord(self.API_KEY, self.URL_PREFIX, redeem_data), None, None





api = QoupotAPI('e0d02ab510e4e3954931f9d5c3d214e318a35373')

print api.check('AAAA')
print api.get('DISCOUNT10')
print api.check('DISCOUNT10')

dc, status, message = api.check('DISCOUNT10')

record, code, msg = api.redeem('DISCOUNT10')
print record

# print api.redeem('XXX')

print DiscountCode.get_list(api_key='e0d02ab510e4e3954931f9d5c3d214e318a35373', url_prefix='http://localhost:8000')
print DiscountCode.get_list(page=3, api_key='e0d02ab510e4e3954931f9d5c3d214e318a35373', url_prefix='http://localhost:8000')
