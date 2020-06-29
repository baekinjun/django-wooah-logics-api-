from django.db import models
from django.contrib.auth.models import User
import uuid


def unique_profile_image_name(instance, filename):
    extension = filename.split('.')[-1]
    return f"profile/{instance.owner.id}/{uuid.uuid4()}.{extension}"


def unique_product_image_name(instance, filename):
    extension = filename.split('.')[-1]
    return f"product/{instance.product.id}/{uuid.uuid4()}.{extension}"


# Create your models here.
class TempProfile(models.Model):
    temp_id = models.TextField()
    app_version = models.CharField(max_length=20, null=True, blank=True)
    platform = models.CharField(max_length=10, null=True, blank=True)
    service_terms = models.BooleanField(default=False)
    privacy_terms = models.BooleanField(default=False)
    location_terms = models.BooleanField(default=False)


class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name='profile')
    name = models.CharField(max_length=20, null=True, blank=True)  # 닉네임
    area = models.ForeignKey('Area', on_delete=models.SET_NULL, related_name='profile_of_areas',
                             related_query_name='profile_of_area', null=True)
    score = models.FloatField(default=0)
    fcm_token = models.TextField(null=True, blank=True)
    app_version = models.CharField(max_length=20, null=True, blank=True)
    platform = models.CharField(max_length=10, null=True, blank=True)
    image = models.ImageField(upload_to=unique_profile_image_name, null=True,
                              blank=True)
    is_app_user = models.BooleanField(default=False)
    friends = models.ManyToManyField('self', through='RelationShip', symmetrical=False)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    is_del = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.owner.username

    @property
    def stamps_count(self):
        return self.object_of_stamps.all().count()


class DeletedProfile(models.Model):
    profile_id = models.IntegerField()
    name = models.CharField(max_length=10, null=True, blank=True)  # 닉네임
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    score = models.FloatField(default=0)
    fcm_token = models.TextField(null=True, blank=True)
    app_version = models.CharField(max_length=20, null=True, blank=True)
    platform = models.CharField(max_length=10, null=True, blank=True)
    image = models.ImageField(upload_to=unique_profile_image_name, null=True,
                              blank=True)
    dt_deleted = models.DateTimeField(auto_now_add=True)


class TermsAgreement(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_of_agrees',
                                related_query_name='profile_of_agree')
    service_terms = models.BooleanField(default=False)
    privacy_terms = models.BooleanField(default=False)
    location_terms = models.BooleanField(default=False)


class Recommend(models.Model):
    subject = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='subject_of_stamps',
                                related_query_name='subject_of_stamp')
    object = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='object_of_stamps',
                               related_query_name='object_of_stamp')
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class RelationShip(models.Model):
    subject = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                related_name='relationships',
                                related_query_name='relationship')
    object = models.ForeignKey(Profile, on_delete=models.CASCADE,
                               related_name='reverse_relationships',
                               related_query_name='reverse_relationship')
    object_name = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('subject', 'object')


class TestPhoneNumber(models.Model):
    phone_number = models.CharField(max_length=13, unique=True)


class Tester(models.Model):
    phone_number = models.ForeignKey(TestPhoneNumber, on_delete=models.CASCADE, related_name='testers', null=True)
    device = models.CharField(max_length=256, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tester')
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)


class BabyAge(models.Model):
    name = models.CharField(max_length=100)


class Product(models.Model):
    STATE_CHOICE = (
        (10, '판매중'),
        (20, '예약중'),
        (30, '거래완료')
    )

    QUALITY_CHOICE = (
        (10, '새제품'),
        (20, '거의없음'),
        (30, '보통'),
        (40, '많음')
    )
    area = models.ForeignKey('Area', on_delete=models.SET_NULL, related_name='area_of_products',
                             related_query_name='area_of_product', null=True)
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='seller_of_products',
                               related_query_name='seller_of_product')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True,
                                 related_name='category_of_products', related_query_name='category_of_product')
    start_baby_age = models.ForeignKey(BabyAge, on_delete=models.SET_NULL, null=True,
                                       related_name='start_baby_age_of_products',
                                       related_query_name='start_baby_age_of_product')
    end_baby_age = models.ForeignKey(BabyAge, on_delete=models.SET_NULL, null=True,
                                     related_name='end_baby_age_of_products',
                                     related_query_name='end_baby_age_of_product')
    title = models.CharField(max_length=50, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICE)
    price = models.IntegerField()
    state = models.CharField(max_length=10, choices=STATE_CHOICE, default=10)
    read_count = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images',
                                related_query_name='product_image')
    image = models.ImageField(upload_to=unique_product_image_name, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.image.name


class Area(models.Model):
    code = models.CharField(max_length=20)
    # full_name = models.CharField(max_length=200)
    unit1 = models.CharField(max_length=20, null=True)
    unit2 = models.CharField(max_length=20, null=True)
    unit3 = models.CharField(max_length=20, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f'{self.unit1} {self.unit2} {self.unit3}'


class Report(models.Model):
    subject = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='subject_of_reports',
                                related_query_name='subject_of_report')
    object = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='object_of_reports',
                               related_query_name='object_of_report')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='product_of_reports',
                                related_query_name='product_of_report')
    content = models.TextField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    seller = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='seller_transactions',
                               related_query_name='seller_transaction')
    buyer = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='buyer_transactions',
                              related_query_name='buyer_transaction')
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True, related_name='product_transaction')
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class Evaluation(models.Model):
    SCORE_CHOICE = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )
    subject = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='subject_of_evaluations',
                                related_query_name='subject_of_evaluation')
    object = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='object_of_evaluations',
                               related_query_name='object_of_evaluation')
    score = models.IntegerField(choices=SCORE_CHOICE)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='comments',
                                   related_query_name='comment')
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class ChatRoom(models.Model):
    seller = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='seller_of_chat_rooms',
                               related_query_name='seller_of_chat_room')
    buyer = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='buyer_of_chat_rooms',
                              related_query_name='buyer_of_chat_room')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='product_of_chat_rooms',
                                related_query_name='product_of_chat_room')
    seller_last_num = models.BigIntegerField(default=0)
    buyer_last_num = models.BigIntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='chat_messages',
                             related_query_name='chat_message')
    sender = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    readers = models.CharField(max_length=200)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class Notice(models.Model):
    title = models.CharField(max_length=200)
    link = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)