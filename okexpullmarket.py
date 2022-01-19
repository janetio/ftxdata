import time
import urllib.parse
from typing import Optional, Dict, Any, List

from requests import Request, Session, Response
import hmac
from ciso8601 import parse_datetime
import json



class OkexClient:
    _ENDPOINT = 'https://www.okex.com'

    def __init__(self, api_key=None, api_secret=None, subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name

    def _get(self, path: str, private_data=True, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, private_data, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('DELETE', path, json=params)

    def _request(self, method: str, path: str, private_data=True, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        if private_data:
            self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
            print("data", data)
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if data['code'] != '0':
                raise Exception(data['msg'])
            with open('data.json', 'w') as f:
                json.dump(data['data'], f)
            return data['data']

    def get_oi(self):
        return self._get(
            "/api/v5/rubik/stat/contracts/open-interest-volume",
            private_data=False,
            params={"ccy": "BTC", "period": "4H", "begin": 1632011600000, "end":1639911600000},
        )

if __name__ == "__main__":
    client = OkexClient()
    print(client.get_oi())