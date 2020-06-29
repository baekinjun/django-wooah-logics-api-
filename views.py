import ast
from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.db.models import Q, F
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import ProductImage, Product, Profile, DeletedProfile, RelationShip, Transaction, Area, TempProfile, \
    RelationShip, ChatRoom, ChatMessage, Recommend, Evaluation, Comment, Report, Notice
from .serializers import ProductSerializers, ProfileSerializer, TransactionSerializer, \
    ChatRoomSerializer, ChatMessageSerializer, NoticeSerializer
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .response_handler import CommonResponse, custom_paginator, ResponseConstants
from .location import location
from django.contrib.auth.models import User


# Create your views here.


class Me(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = ProfileSerializer(request.user.profile)
        return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, serializer.data)

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, serializer.data)
        return CommonResponse(status.HTTP_400_BAD_REQUEST, ResponseConstants.DEFAULT_FAILED_MESSAGE, {})

    @transaction.atomic
    def delete(self, request):
        profile = request.user.profile
        del_profile = DeletedProfile(
            profile_id=profile.id,
            name=profile.name,
            phone_number=profile.phone_number,
            image=profile.image,
            score=profile.score,
            fcm_token=profile.fcm_token,
            platform=profile.platform,
            app_version=profile.app_version,
        )
        del_profile.save()

        profile.name = None
        profile.score = 0
        profile.fcm_token = None
        profile.app_version = None
        profile.platform = None
        profile.image = None
        profile.is_app_user = False
        profile.is_del = True

        if not RelationShip.objects.filter(object=profile).count() > 0:
            profile.phone_number = None
        profile.save()
        return CommonResponse(status.HTTP_204_NO_CONTENT, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE,
                                  ProfileSerializer(profile))
        except Profile.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, 'profile_id has not found', {})


# 상품등록 , 조회, 수정 , 삭제
class ProductView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ProductSerializers(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return CommonResponse(status.HTTP_201_CREATED, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, serializer.data)
        return CommonResponse(status.HTTP_400_BAD_REQUEST, serializer.errors['error'], {})

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, ResponseConstants.DEFAULT_FAILED_MESSAGE, {})
        serializer = ProductSerializers(product, context={'request': request})
        return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, serializer.data)

    def put(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, ResponseConstants.DEFAULT_FAILED_MESSAGE, {})

        serializer = ProductSerializers(product, data=request.data, context={'request': request}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, serializer.data)
        return CommonResponse(status.HTTP_400_BAD_REQUEST, serializer.errors, {})

    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, ResponseConstants.DEFAULT_FAILED_MESSAGE, {})
        product.delete()
        return CommonResponse(status.HTTP_204_NO_CONTENT, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})


class ProductImageView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, product_id, *args, **kwargs):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, ResponseConstants.DEFAULT_FAILED_MESSAGE, {})

        files = request.FILES

        ProductImage(
            product=product,
            image=files['image']
        ).save()
        return CommonResponse(status.HTTP_201_CREATED, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})


class TransactionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)

        try:
            buyer_id = request.data['buyer_id']
            buyer = Profile.objects.get(id=buyer_id)

            Transaction(
                seller=request.user.profile,
                buyer=buyer,
                product=product
            ).save()
            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})
        except KeyError as e:
            return CommonResponse(status.HTTP_400_BAD_REQUEST, f'{e} is essential field', {})
        except Profile.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, 'buyer has not found', {})


class AreaView(APIView):
    permission_classes = (AllowAny,)

    # TODO: 이거는 바꿔야 합니다.
    def post(self, request):
        lng = request.data.get('lng')
        lat = request.data.get('lat')
        owner = request.data.get('owner')
        owner_id = User.objects.get(username=owner).id
        try:
            locate = location(lng, lat)
            area, created = Area.objects.get_or_create(
                code=locate['code'],
                full_name=locate['full_name'][0],
                unit1=locate['unit1'],
                unit2=locate['unit2'],
                unit3=locate['unit3'],
                unit4=locate['unit4'],
            )
        except KeyError as e:
            return CommonResponse(status.HTTP_400_BAD_REQUEST, ResponseConstants.DEFAULT_FAILED_MESSAGE,
                                  {'존재하지않는 지역입니다.'})
        else:
            profile = Profile.objects.filter(owner=owner_id).values('area').update(
                area=area
            )

            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})


class AppInfoView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user_id = request.data.get('user_id')
        temp_id = request.data.get('temp_id')
        app_version = request.data.get('app_version')
        platform = request.data.get('platform')
        if user_id is None and temp_id is None:
            return CommonResponse(status.HTTP_400_BAD_REQUEST, 'temp_id or user_id have to fill in the blank', {})
        if app_version is None or platform is None:
            return CommonResponse(status.HTTP_400_BAD_REQUEST, 'app_version or platform is essential fields', {})
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                profile = user.profile
                profile.app_version = app_version
                profile.platform = platform
                profile.save()
                return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})
            except User.DoesNotExist as e:
                return CommonResponse(status.HTTP_404_NOT_FOUND, 'user has not found', {})
        else:
            TempProfile(
                temp_id=temp_id,
                app_version=app_version,
                platform=platform
            ).save()
            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})


class FriendView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        subject = request.user.profile  # 나자신
        phone_num = request.data.get('phone_num')  # 친구번호
        name = request.data.get('name')  # 친구이름
        phonelist = ast.literal_eval(phone_num)  # 친구번호 리스트
        namelist = ast.literal_eval(name)  # 친구이름 리스트
        user_list = []  # bulk_create 하기위한 리스트
        uid_list = []  # user가 저장을해야지 객체가 생겨서 uid는 계속 바뀌어서 uid를 저장하기위해 만들었습니다.
        phone_list = []  # bulk_create 하기위한 리스트
        relate_list = []  # bulk_create하기위한 리스
        owner_list = []
        for i in range(len(phonelist)):  # 먼저 객체를 생성해야됨
            username = uuid4()
            user = User(
                username=username
            )
            user_list.append(user)
            uid_list.append(username)
        User.objects.bulk_create(user_list)
        owner = User.objects.filter(username__in=uid_list)
        for owner_id, number in zip(owner, phonelist):
            profile = Profile(
                owner=owner_id,
                phone_number=number
            )
            phone_list.append(profile)
            owner_list.append(owner_id)
        Profile.objects.bulk_create(phone_list)
        object = Profile.objects.filter(owner__in=owner_list).values('id')
        for Name, object_id in zip(namelist, object):
            relate = RelationShip(
                subject_id=subject,
                object_name=Name,
                object_id=object_id['id']
            )
            relate_list.append(relate)
        RelationShip.objects.bulk_create(relate_list)
        return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})

    def get(self, request):
        subject = request.user.profile
        queryset = subject.friends.filter(is_app_user=1)
        result = ProfileSerializer(queryset, many=True).data
        return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, result)


class TermsAgreeView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        temp_id = request.data.get('temp_id')
        service_terms = request.data.get('service_terms')
        privacy_terms = request.data.get('privacy_terms')
        location_terms = request.data.get('location_terms')
        boolchecker = [0, 1]
        if temp_id is None:
            return CommonResponse(status.HTTP_400_BAD_REQUEST, "temp_id is essential fields", {})
        if int(service_terms) not in boolchecker or int(privacy_terms) not in boolchecker or int(
                location_terms) not in boolchecker:
            return CommonResponse(status.HTTP_400_BAD_REQUEST, 'type is invalid', {})
        try:
            TempProfile.objects.filter(temp_id=temp_id).values('service_terms', 'privacy_terms',
                                                               'location_terms').update(
                service_terms=True if int(service_terms) else False,
                privacy_terms=True if int(privacy_terms) else False,
                location_terms=True if int(location_terms) else False
            )
            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})
        except TempProfile.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, ResponseConstants.DEFAULT_FAILED_MESSAGE, {})


class ChatRoomView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return CommonResponse(status.HTTP_201_CREATED, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, serializer.data)

        return CommonResponse(status.HTTP_400_BAD_REQUEST, serializer.errors['error'], {})

    def get(self, request):
        profile = request.user.profile
        queryset = ChatRoom.objects.select_related('seller', 'buyer', 'product'). \
            filter(Q(seller=profile) | Q(buyer=profile)).order_by('-created_time')

        return custom_paginator(request, queryset, ChatRoomSerializer)


class ChatView(APIView):

    def get(self, request, room_id):
        messages = ChatMessage.objects.filter(room_id=room_id).order_by('created_time')
        return custom_paginator(request, messages, ChatMessageSerializer)

    def post(self, request, room_id):
        serializer = ChatMessageSerializer(data=request.data, context={'request': request, 'room_id': room_id})
        if serializer.is_valid():
            return CommonResponse(status.HTTP_201_CREATED, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})

        return CommonResponse(status.HTTP_400_BAD_REQUEST, serializer.errors['error'], {})


class ShareProductView(APIView):
    permission_classes = (IsAuthenticated,)

    def make_share_url(self, product_id):
        return f'{settings.API_URL}/product/{product_id}/'

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            share_url = self.make_share_url(product_id)

            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE,
                                  {'share_url': share_url})
        except Product.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, 'product has not found', {})


class RecommendView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, profile_id):
        try:
            subject = request.user.profile
            relationship = RelationShip.objects.get(subject=subject, object_id=profile_id)
            Recommend(
                subject=request.user.profile,
                object=relationship.object
            ).save()
            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})
        except RelationShip.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, 'relationship has not found', {})


class SellHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Transaction.objects.filter(seller=request.user.profile)
        return custom_paginator(request, queryset, TransactionSerializer)

    def delete(self, request, transaction_id):
        profile = request.user.profile
        try:
            instance = Transaction.objects.get(seller=profile, id=transaction_id)
            instance.delete()
            return CommonResponse(status.HTTP_204_NO_CONTENT, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})
        except Transaction.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, 'transaction has not found', {})


class BuyHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Transaction.objects.filter(buyer=request.user.profile)
        return custom_paginator(request, queryset, TransactionSerializer)

    def delete(self, request, transaction_id):
        profile = request.user.profile
        try:
            instance = Transaction.objects.get(buyer=profile, id=transaction_id)
            instance.delete()
            return CommonResponse(status.HTTP_204_NO_CONTENT, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})
        except Transaction.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, 'transaction has not found', {})


class CheckReviewView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, profile_id):
        try:
            object = Profile.objects.get(id=profile_id)
            eval = Evaluation.objects.get(subject=request.user.profile, object=object)
            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {'check': True})
        except Profile.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, 'profile has not found', {})
        except Evaluation.DoesNotExist as e:
            return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {'check': False})


class ReviewView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, profile_id):
        data = request.data
        try:
            object = Profile.objects.get(id=profile_id)
            eval = Evaluation(subject=request.user.profile, object=object, score=data['score'])

            content = data.get('content')
            if content:
                Comment(
                    evaluation=eval,
                    content=content
                ).save()
            eval.save()
        except Profile.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, 'profile has not found', {})
        except KeyError as e:
            return CommonResponse(status.HTTP_400_BAD_REQUEST, f'{e.__str__()} field is essential', {})
        return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})


class ReportView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, product_id):
        data = request.data
        try:
            product = Product.objects.get(id=product_id)

            Report(
                subject=request.user.profile,
                object=product.seller,
                product=product,
                content=data.get('content', '')
            ).save()
            return CommonResponse(status.HTTP_201_CREATED, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})
        except Product.DoesNotExist as e:
            return CommonResponse(status.HTTP_404_NOT_FOUND, ResponseConstants.DEFAULT_SUCCESS_MESSAGE, {})


class ProductOfFriendsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # profile = request.user.profile
        profile = Profile.objects.get(id=6)

        friends = []
        # 1->2 step
        active_object_id_list = list(RelationShip.objects.select_related('object') \
                                     .filter(subject=profile, object__is_app_user=True) \
                                     .values_list('object_id', flat=True))
        inactive_object_id_list = list(RelationShip.objects.select_related('object') \
                                       .filter(subject=profile, object__is_app_user=False) \
                                       .values_list('object_id', flat=True))

        friends.extend(active_object_id_list)

        # 2->3 step
        object_id_list = list(RelationShip.objects.select_related('object') \
                              .filter(subject_id__in=active_object_id_list, object__is_app_user=True) \
                              .exclude(object_id=profile.id) \
                              .values_list('object_id', flat=True))

        friends.extend(object_id_list)

        object_id_list = list(RelationShip.objects.select_related('subject') \
                              .filter(object_id__in=inactive_object_id_list) \
                              .exclude(subject_id=profile.id) \
                              .values_list('object_id', flat=True))

        friends.extend(object_id_list)

        # 3->4 step
        object_id_list = list(RelationShip.objects.select_related('object') \
                              .filter(subject_id__in=object_id_list, object__is_app_user=True) \
                              .values_list('object_id', flat=True))

        friends.extend(object_id_list)

        friends = list(set(friends))

        products = Product.objects.select_related('seller', 'category') \
            .filter(seller_id__in=friends) \
            .prefetch_related('product_images') \
            .order_by('-modified_time')

        return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE,
                              ProductSerializers(products, many=True).data)


class ProductOfLocationView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = request.user.profile
        area = profile.area
        if not area:
            return CommonResponse(status.HTTP_202_ACCEPTED, 'user location info empty', {})
        products = Product.objects.select_related('area', 'seller', 'category', 'start_baby_age', 'end_baby_age') \
            .filter(area__unit1=area.unit1, area__unit2=area.unit2, area__unit3=area.unit3) \
            .prefetch_related('product_images') \
            .order_by('-modified_time')

        return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE,
                              ProductSerializers(products, many=True).data)


class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = NoticeSerializer
    queryset = Notice.objects.all()

    def list(self, request, *args, **kwargs):
        data = self.get_serializer(self.paginate_queryset(self.queryset), many=True).data
        response = self.get_paginated_response(data)
        return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE,
                              response.data)

    def retrieve(self, request, *args, **kwargs):
        return CommonResponse(status.HTTP_200_OK, ResponseConstants.DEFAULT_SUCCESS_MESSAGE,
                              self.get_serializer(self.get_object()).data)
