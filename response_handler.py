from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.settings import api_settings
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


class ResponseConstants:
    DEFAULT_SUCCESS_MESSAGE = '요청에 성공했습니다.'
    DEFAULT_FAILED_MESSAGE = '요청에 실패했습니다.'


class CommonResponse(Response):
    def __init__(self, status_code, message, data, code=None):
        if not code:
            code = '%s%s' % (str(status_code), '0000')
        response = {
            'code': str(code),
            'message': message,
            'payload': data
        }
        super().__init__(status=status_code, data=response)


def custom_paginator(request, queryset, serializer):
    page = request.query_params.get('page')
    base_url = request.build_absolute_uri().split('?')[0]
    p = Paginator(queryset, api_settings.PAGE_SIZE)
    if not page:
        page = 1
    prev_page = None
    next_page = None
    try:
        page_results = p.page(page)
        if page_results.has_previous():
            prev_page = '{}?page={}'.format(base_url,
                                            page_results.previous_page_number())

        if page_results.has_next():
            next_page = '{}?page={}'.format(base_url,
                                            page_results.next_page_number())

        result = {
            'count': p.count,
            'previous': prev_page,
            'next': next_page
        }
        if serializer:
            result['results'] = serializer(page_results.object_list, many=True,
                                           context={'request': request}).data
        else:
            result['results'] = page_results.object_list
        return CommonResponse(status.HTTP_200_OK, "요청에 성공했습니다.", result)
    except EmptyPage:
        return CommonResponse(status.HTTP_404_NOT_FOUND, "존재하지 않는 페이지입니다.",
                              {'detail': 'Invalid page.'})
    except PageNotAnInteger:
        return CommonResponse(status.HTTP_404_NOT_FOUND, "유효하지 않은 페이지입니다.",
                              {'detail': 'Invalid page.'})
