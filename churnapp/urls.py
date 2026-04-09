from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('predict/', views.predict_churn, name='predict'),
    path('customers/', views.customers_view, name='customers'),       # ✅ Add this
    path('add-customer/', views.add_customer_view, name='add_customer'), # ✅ Add this
    path('upload-data/', views.upload_csv, name='upload_data'),   # ✅ Use the correct view
    path("dashboard/data/", views.dashboard_data, name="dashboard_data"),  # ✅ Add this
    path('customers/edit/<int:id>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:id>/', views.delete_customer, name='delete_customer'),


               
]