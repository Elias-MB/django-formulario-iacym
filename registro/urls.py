from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls
from registro.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
# router.register(r'para la url', vista, 'nombre')
router.register(r'tipos-documento', VistaTipoDocumento, 'tipos-documento')
router.register(r'tipos-persona', VistaTipoPersona, 'tipos-persona')
router.register(r'cursos', VistaCurso, 'cursos')
router.register(r'ministerios', VistaMinisterio, 'ministerios')
router.register(r'registros', VistaCursoPersona, 'registros')
router.register(r'registros-parejas', VistaPareja, 'registros-pareja')

# router.register(r'permiso', VistaPermisos, 'permisos')

url_api = [
    path('api/v1/archivo/ver/', VerArchivoApi.as_view(), name='ver_archivo'),
    path('api/v1/login/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/login/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/usuarios/permisos/', ObtenerPermisosApi.as_view(), name='obtener_permisos'),
    path('api/v1/usuarios/grupos/', ObtenerGruposApi.as_view(), name='obtener_grupos'),
    path('api/v1/usuarios/logeado/permisos/', ObtenerPermisosUsuarioApi.as_view(), name='obtener_permisos_usuario'),
    # path('api/v1/registros/', RegistroCursoPersonaApi.as_view(), name='regristro_curso_persona'),
]

urlpatterns = url_api +[
    path('docs/', include_docs_urls(title = "Formulario Api's")),
    path('api/v1/', include(router.urls)),
]
