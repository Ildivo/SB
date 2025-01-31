from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include


from .views import (
    login_view,
    get_cookie_view,
    set_cookie_view,
    get_session_view,
    set_session_view,
    logout_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    FooBarView,
    HelloView
)

app_name = 'myauth'

urlpatterns = [
    #path('login/', login_view, name='login'),
    path('hello/', HelloView.as_view(), name='hello'),
    path(
        'login/',
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name='login'
    ),
    path('logout/', logout_view, name='logout'),
    #path('logout/', MyLogoutView.as_view(), name='logout'),
    path('about-me/', AboutMeView.as_view(), name='about-me'),
    path('register/', RegisterView.as_view(), name='register'),

    path('cookies/get/', get_cookie_view, name='cookies_get'),
    path('cookies/set/', set_cookie_view, name='cookies_set'),

    path('session/set/', set_session_view, name='session_set'),
    path('session/get/', get_session_view, name='session_get'),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]
