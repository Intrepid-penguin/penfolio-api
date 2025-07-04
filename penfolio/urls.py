"""
URL configuration for penfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from journals_api.v1.journal_api import router as journals_router
from journals_api.v1.base import router as base_router
from journals_api.v1.user_api import router as users_router

api = NinjaAPI(title="MyJournal API")

api.add_router("/", base_router, tags=["Home"])
api.add_router("/journals/", journals_router, tags=["Journals"])
api.add_router("/auth/", users_router, tags=["Users & Auth"])

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]

