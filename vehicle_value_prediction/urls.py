from django.contrib import admin
from django.urls import path
from admins import views as mainView
from users import views as usr
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',                       admin.site.urls),

    # ── Public ─────────────────────────────────────────────────────
    path('',                             mainView.index,           name='index'),
    path('index/',                       mainView.index,           name='index2'),
    path('about/',                       usr.about,                name='about'),

    # ── Admin flow ──────────────────────────────────────────────────
    path('AdminLogin/',                  mainView.AdminLogin,       name='AdminLogin'),
    path('AdminLoginCheck/',             mainView.AdminLoginCheck,  name='AdminLoginCheck'),
    path('AdminHome/',                   mainView.AdminHome,        name='AdminHome'),
    path('RegisterUsersView/',           mainView.RegisterUsersView,name='RegisterUsersView'),
    path('ActivaUsers/',                 mainView.ActivaUsers,      name='ActivaUsers'),

    # ── User auth ───────────────────────────────────────────────────
    path('UserLogin/',                   mainView.UserLogin,        name='UserLogin'),
    path('UserRegister/',                mainView.UserRegister,     name='UserRegister'),
    path('UserRegisterActions/',         usr.UserRegisterActions,   name='UserRegisterActions'),
    path('UserLoginCheck/',              usr.UserLoginCheck,        name='UserLoginCheck'),
    path('UserHome/',                    usr.UserHome,              name='UserHome'),
    path('logout/',                      usr.logout_user,           name='logout'),

    # ── Core features ───────────────────────────────────────────────
    path('DatasetView/',                 usr.DatasetView,           name='DatasetView'),
    path('training/',                    usr.training,              name='training'),
    path('prediction/',                  usr.prediction,            name='prediction'),
    path('prediction_history/',          usr.prediction_history,    name='prediction_history'),
    path('delete_prediction/<int:pk>/',  usr.delete_prediction,     name='delete_prediction'),
    path('history_detail/<int:pk>/',     usr.history_detail,        name='history_detail'),
    path('compare/',                     usr.compare_cars,          name='compare_cars'),
    path('compare_result/',              usr.compare_result,        name='compare_result'),
    path('how-it-works/',               usr.how_it_works,          name='how_it_works'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
