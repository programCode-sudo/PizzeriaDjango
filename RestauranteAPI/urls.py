# RestauranteAPI/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Importar las vistas necesarias de drf_yasg
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configurar el esquema de drf_yasg
schema_view = get_schema_view(
    openapi.Info(
        title="API de la Pizzería Django",
        default_version='v1',
        description="Esta es la documentación de la API para la Pizzería Django.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contacto@tusitio.com"),
        license=openapi.License(name="Licencia MIT"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Authentication.urls')),
    path('administrator/', include('Administrator.urls')),
    path('menu_manager/', include('Menu_Manager.urls')),
    path('customer/', include('Customer.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('pedidos/', include('Pedidos.urls')),
    path('order_manager/', include('Order_Manager.urls')),
    path('delivery_person/', include('Delivery_Person.urls')),
    path('order_dispatcher/', include('Order_Dispatcher.urls')),

    # Rutas para la documentación de la API
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
