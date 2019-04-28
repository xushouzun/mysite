from django.urls import path
from . import views

urlpatterns = [
    path('', views.HelloWorld.as_view()),
    # path('select/', views.Select.as_view()),
    # path('update/', views.Update.as_view()),
    # path('delete/', views.Delete.as_view()),
    # path('insert/', views.Insert.as_view()),
    # path('login/', views.Login.as_view())
    path('CheckMaterial/', views.CheckMaterial.as_view())
]
