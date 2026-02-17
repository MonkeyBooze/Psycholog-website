from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book, name='book'),
    path('kontakt/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('terms/', views.terms, name='terms'),
    path('data-subject-rights/', views.data_subject_rights, name='data_subject_rights'),
    path('thanks/', views.thanks, name='thanks'),
    path('o-nas/', views.about_us, name='about_us'),
    path('cennik/', views.pricing, name='pricing'),
    path('diagnoza-adhd/', views.diagnoza_adhd, name='diagnoza_adhd'),
    path('diagnoza-autyzmu/', views.diagnoza_autyzmu, name='diagnoza_autyzmu'),
    path('szkolenia-dla-firm/', views.trainings, name='trainings'),
    path('blog/', views.blog, name='blog'),
    path('blog/kategoria/<slug:slug>/', views.blog_category, name='blog_category'),
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'),
    path('health/', views.healthcheck, name='healthcheck'),
    path('api/log-cookie-consent/', views.log_cookie_consent, name='log_cookie_consent'),
]
