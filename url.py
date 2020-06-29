from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.contrib import admin
from django.conf import settings
from django.conf.urls import include
from api import views
from rest_framework.routers import DefaultRouter
import firebase_phone_oauth2.urls
from django.conf.urls.static import static

router = DefaultRouter()

router.register('notice', views.NoticeViewSet)

include_doc_urlpatterns = [
    path('', include(router.urls)),
    path('o/', include(firebase_phone_oauth2.urls.urlpatterns)),
    path('me/', views.Me.as_view()),
    path('product/', views.ProductView.as_view(),name = 'product'),
    path('product/<int:product_id>/', views.ProductView.as_view()),
    path('product_attach/<int:product_id>/', views.ProductImageView.as_view()),
    path('product/complete/<int:product_id>/', views.TransactionView.as_view()),
    path('location/', views.AreaView.as_view(),name = 'location'),
    path('app_info/', views.AppInfoView.as_view()),
    path('term_agreement/', views.TermsAgreeView.as_view()),
    path('friends/', views.FriendView.as_view()),
    path('review/check/<int:profile_id>/', views.CheckReviewView.as_view()),
    path('review/<int:profile_id>/', views.ReviewView.as_view()),
    path('chat/', views.ChatRoomView.as_view()),
    path('chat/<int:room_id>/', views.ChatView.as_view()),
    path('profile/<int:profile_id>/', views.ProfileView.as_view()),
    path('share/product/<int:product_id>/', views.ShareProductView.as_view()),
    path('recommend/<int:profile_id>/', views.RecommendView.as_view()),
    path('sell_history/', views.SellHistory.as_view()),
    path('sell_history/<int:transaction_id>/', views.SellHistory.as_view()),
    path('buy_history/', views.BuyHistory.as_view()),
    path('buy_history/<int:transaction_id>/', views.BuyHistory.as_view()),
    path('product/friends/', views.ProductOfFriendsView.as_view()),
    path('product/location/', views.ProductOfLocationView.as_view()),
    path('report/<int:product_id>/', views.ReportView.as_view()),
]

exclude_doc_url_patterns = [
]

urlpatterns = include_doc_urlpatterns + exclude_doc_url_patterns
