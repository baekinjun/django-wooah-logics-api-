from rest_framework import serializers
from .models import Profile, ChatRoom, ChatMessage, Notice
from django.contrib.auth.models import User
from .models import Product, ProductCategory, ProductImage, BabyAge, Transaction, Area, TempProfile, \
    RelationShip
import logging

logger = logging.getLogger(__name__)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        extra_kwargs = {
            'fcm_token': {'write_only': True},
            'app_version': {'write_only': True},
            'platform': {'write_only': True},
        }
        fields = ('id', 'owner', 'name', 'area', 'fcm_token', 'app_version', 'platform',
                  'image', 'friends', 'phone_number', 'score', 'stamps_count')


class ProductCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class BabyAgeSerializers(serializers.ModelSerializer):
    class Meta:
        model = BabyAge
        fields = '__all__'


class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def is_valid(self, raise_exception=False):
        attrs = self.initial_data

        essential_fields = ['title', 'content', 'category', 'quality', 'start_baby_age',
                            'end_baby_age', 'state', 'price']
        for field in essential_fields:
            if field not in attrs.keys():
                self._errors = {'error': f'{field} is essential field'}
                return False
        category_ids = list(ProductCategory.objects.all().values_list('id', flat=True))
        if attrs['category'] not in [str(id) for id in category_ids]:
            self._errors = {'error': 'category field out of range'}
            return False
        baby_age_ids = list(BabyAge.objects.all().values_list('id', flat=True))
        if attrs['start_baby_age'] not in [str(id) for id in baby_age_ids]:
            self._errors = {'error': 'start_baby_age field out of range'}
            return False
        if attrs['end_baby_age'] not in [str(id) for id in baby_age_ids]:
            self._errors = {'error': 'end_baby_age field out of range'}
            return False
        if attrs['quality'] not in [str(c[0]) for c in Product.QUALITY_CHOICE]:
            self._errors = {'error': 'quality field out of range'}
            return False

        if attrs['state'] not in [str(c[0]) for c in Product.STATE_CHOICE]:
            self._errors = {'error': 'state field out of range'}
            return False

        self._errors = {}
        self._validated_data = attrs
        return True

    def create(self, validated_data):
        request = self.context['request']
        # seller = request.user.profile
        seller = Profile.objects.get(id=1)
        self.validate(validated_data)
        product = Product(
            title=validated_data['title'],
            content=validated_data['content'],
            area=seller.area,
            seller=seller,
            category_id=validated_data['category'],
            quality=validated_data['quality'],
            start_baby_age_id=validated_data['start_baby_age'],
            end_baby_age_id=validated_data['end_baby_age'],
            state=validated_data['state'],
            price=validated_data['price'],
        )
        product.save()
        return product

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.quality = validated_data.get('quality', instance.quality)
        instance.price = validated_data.get('price', instance.price)
        instance.state = validated_data.get('state', instance.state)
        instance.category_id = validated_data.get('category', instance.category_id)
        instance.start_baby_age_id = validated_data.get('start_baby_age', instance.start_baby_age_id)
        instance.end_baby_age_id = validated_data.get('end_baby_age', instance.end_baby_age_id)

        instance.save()

        return instance


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

    def is_valid(self, raise_exception=False):
        attrs = self.initial_data

        essential_fields = ['buyer', 'product']
        for field in essential_fields:
            if field not in attrs.keys():
                self._errors = {'error': f'{field} is essential field'}
                return False
        try:
            Product.objects.get(id=attrs['product'])
        except Product.DoesNotExist as e:
            self._errors = {'error': 'product does not exist'}
            return False
        try:
            Profile.objects.get(id=attrs['buyer'])
        except Profile.DoesNotExist as e:
            self._errors = {'error': 'buyer does not exist'}
            return False
        state = Product.objects.filter(id=attrs['product']).values('state')
        if state[0]['state'] == 30:
            self._errors = {'error': 'already state is complete'}
            return False

        self._errors = {}
        self._validated_data = attrs
        return True

    def create(self, validated_data):
        request = self.context['request']
        # seller = request.user.profile
        seller = Profile.objects.get(id=1)
        self.validate(validated_data)
        transaction = Transaction(
            seller=seller,
            product=validated_data['product'],
            buyer=validated_data['buyer']
        )
        transaction.save()

        return transaction


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'

    def is_valid(self, raise_exception=False):
        attrs = self.initial_data

        essential_fields = ['product_id']
        for field in essential_fields:
            if field not in attrs.keys():
                self._errors = {'error': f'{field} is essential field'}
                return False

        try:
            Product.objects.get(id=attrs['product_id'])
        except Product.DoesNotExist as e:
            self._errors = {'error': 'product does not exist'}
            return False

        self._errors = {}
        self._validated_data = attrs
        return True

    def create(self, validated_data):
        request = self.context['request']
        product_id = validated_data['product_id']
        product = Product.objects.get(id=product_id)
        chat_room = ChatRoom(
            seller=product.seller,
            buyer=request.user.profile,
            product_id=product_id
        )
        chat_room.save()

        return chat_room


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

    def is_valid(self, raise_exception=False):
        attrs = self.initial_data
        room_id = self.context['room_id']

        essential_fields = ['content']
        for field in essential_fields:
            if field not in attrs.keys():
                self._errors = {'error': f'{field} is essential field'}
                return False

        # Check content is empty
        if not attrs['content']:
            self._errors = {'error': 'content is empty'}
            return False
        # Check Room Id
        try:
            chat_room = ChatRoom.objects.get(id=room_id)
            attrs['room'] = chat_room
        except ChatRoom.DoesNotExist as e:
            self._errors = {'error': 'room_id does not exist'}
            return False

        self._errors = {}
        self._validated_data = attrs
        return True

    def create(self, validated_data):
        request = self.context['request']

        chat_message = ChatMessage(
            room=validated_data['room'],
            sender=request.user.profile,
            content=validated_data['content']
        )
        chat_message.save()
        return chat_message


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'