from django.contrib import admin
from django.urls import path
from pdf_generator.views import generate_pdf, download_pdf, home, check_status

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),

    # Frontend expected endpoints:
    path('urll', generate_pdf, name='generate_pdf'),  # Match frontend POST /urll
    path('status', check_status, name='check_status'),  # Match frontend GET /status
    path('pdfs', download_pdf, name='download_pdf'),  # Match frontend GET /pdfs
]
