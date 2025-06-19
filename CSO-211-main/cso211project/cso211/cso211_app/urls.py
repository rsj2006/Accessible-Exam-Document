from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
import os

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('upload/', views.upload_file, name='upload'),
    
] + static('/uploads/', document_root=os.path.join(settings.BASE_DIR, 'uploads'))
