import time
import urllib.parse
from typing import Optional, Dict, Any, List

from requests import Request, Session, Response
import json



class CoinglassClient:
    _ENDPOINT = 'https://open-api.coinglass.com'

    def __init__(self, api_key=None, api_secret=None, subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = "82ae5b6cbfdb4840a4a5ffc0413ae4bf"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('DELETE', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        request.headers['coinglassSecret'] = self._api_key

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
            "/api/pro/v1/futures/openInterest",
            params={"interval": 0, "symbol": "BTC"},
        )

if __name__ == "__main__":
    client = CoinglassClient()
    print(client.get_oi())