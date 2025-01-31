from django.urls import path

from .views import proccess_get_view, user_form, handle_file_upload

app_name = "requestdataapp"
urlpatterns = [
    path("get/", proccess_get_view, name="get-view"),
    path("bio/", user_form, name="user-form"),
    path("upload/", handle_file_upload, name="file-upload"),
]
