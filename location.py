import json
from pyproj import Proj, transform
import requests


def location(lng, lat):
    key = 'your key'
    secret = 'your secret key'
    req_url = f'https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json'
    params = {
        'consumer_key': key,
        'consumer_secret': secret,
    }

    response = requests.get(req_url, params=params)
    con = json.loads(response.text)
    accesstoken = con['result']['accessToken']

    proj_WGS84 = Proj(init='epsg:4326')
    proj_UTMK = Proj(init='epsg:5178')
    t_lng, t_lat = transform(proj_WGS84, proj_UTMK, lng, lat)
    req_url1 = f'https://sgisapi.kostat.go.kr/OpenAPI3/addr/rgeocode.json'
    params1 = {
        'accessToken': accesstoken,
        'x_coor': t_lng,
        'y_coor': t_lat,
        'addr_type': 21,
    }

    response = requests.get(req_url1, params=params1)
    con = json.loads(response.text)
    sgg_nm = ""
    try:
        results = con['result']
        if results:
            adm_cd = results[0]['adm_dr_cd']
            sido_nm = results[0]['sido_nm']
            for n in results[0]['sgg_nm'].split(" "):
                sgg_nm += n
            emdong_nm = results[0]['emdong_nm']
        result = {
            'adm_cd': adm_cd,
            'sido_nm': sido_nm,
            'sgg_nm': sgg_nm,
            'emdong_nm': emdong_nm
        }
        return result
    except KeyError as e:
        return "잘못된 정보를 입력하셨습니다. ", {'detail': 'KeyError'}