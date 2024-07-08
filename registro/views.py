from django.db import IntegrityError, transaction
from django.contrib.auth.models import User, Permission, Group
from django.utils.dateparse import parse_date
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework import viewsets, status
from .serializer import *
from .models import *
import threading
from rest_framework.views import APIView
import base64
from .middlewares.email import Email
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from datetime import datetime
import os

def formatearFecha(fecha):
    return (datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%S.%fZ")).date()

class Objeto:
    def __init__(self, diccionario):
        for clave, valor in diccionario.items():
            setattr(self, clave, valor)
            
    def __str__(self):
        atributos = ", ".join(f"{clave}={valor}" for clave, valor in self.__dict__.items())
        return f"Objeto({atributos})"

class VistaTipoDocumento(viewsets.ModelViewSet):
    serializer_class = TipoDocumentoSerializer
    queryset = TipoDocumento.objects.all()

class VistaTipoPersona(viewsets.ModelViewSet):
    serializer_class = TipoPersonaSerializer
    queryset = TipoPersona.objects.all()

class VistaCurso(viewsets.ModelViewSet):
    serializer_class = CursoSerializer
    queryset = Curso.objects.all()
    
    def list(self, request, *args, **kwargs):
        try:
            cursos = Curso.objects.filter(estado='A')
            serializer = self.get_serializer(cursos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class VistaMinisterio(viewsets.ModelViewSet):
    serializer_class = MinisterioSerializer
    queryset = Ministerio.objects.all()
    
    def list(self, request, *args, **kwargs):
        try:
            ministerios = Ministerio.objects.filter(estado='A')
            serializer = self.get_serializer(ministerios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class VistaCursoPersona(viewsets.ModelViewSet):
    queryset = CursoPersona.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CursoPersonaWriteSerializer
        return CursoPersonaReadSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            registros = CursoPersona.objects.all()
            response_data = []

            for registro in registros:
                serializer = self.get_serializer(registro)
                registro_data = serializer.data

                archivo = Archivo.objects.filter(modelo="CursoPersona", id_modelo=registro.id, subtipo="voucher").first()
                if archivo and os.path.exists(archivo.ruta):
                    registro_data['archivo'] = {"nombre": archivo.nombre}
                else:
                    registro_data['archivo'] = {"nombre": ""}
                
                persona = Persona.objects.get(pk=registro.persona.pk)
                if persona:
                    ministerio = Ministerio.objects.get(pk=persona.ministerio_id)
                    if ministerio:
                        registro_data["ministerio"] = MinisterioSerializer(ministerio).data
                    else: registro_data["ministerio"] = {}
                
                response_data.append(registro_data)

            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
       
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            # print(request.data)
            datos = request.data.copy()
            data_persona = datos.get('persona')
            data_curso = datos.get('curso')
            
            if data_curso:
                try:
                    curso_id = data_curso.get('id')
                    curso_instance = Curso.objects.get(pk=curso_id)
                except ObjectDoesNotExist:
                    print("Curso con este ID no existe.")
                    return Response({"detail": "Curso con este ID no existe."}, status=status.HTTP_400_BAD_REQUEST)
                
            if data_persona:
                fecha_nacimiento = data_persona.get('fecha_nacimiento')
                if fecha_nacimiento:
                    data_persona['fecha_nacimiento'] = formatearFecha(fecha_nacimiento)
                    
                fecha_bautismo = data_persona.get('fecha_bautismo')
                if fecha_bautismo:
                    data_persona['fecha_bautismo'] = formatearFecha(fecha_bautismo)
                    
                tipo_documento_data = data_persona.get('tipo_documento')
                if tipo_documento_data:
                    try:
                        tipo_documento_id = tipo_documento_data.get('id')
                        tipo_documento_instance = TipoDocumento.objects.get(pk=tipo_documento_id)
                    except ObjectDoesNotExist:
                        print("Tipo de documento con este ID no existe.")
                        return Response({"detail": "Tipo de documento con este ID no existe."}, status=status.HTTP_400_BAD_REQUEST)
                    data_persona['tipo_documento'] = tipo_documento_instance
                    
                ministerio_data = data_persona.get('ministerio', None)
                if ministerio_data:
                    try:
                        tipo_documento_id = tipo_documento_data.get('id')
                        ministerio_id = ministerio_data.get('id')
                        ministerio_instance = Ministerio.objects.get(pk=ministerio_id)
                    except ObjectDoesNotExist:
                        print("Ministerio con este ID no existe.")
                        return Response({"detail": "Ministerio con este ID no existe."}, status=status.HTTP_400_BAD_REQUEST)
                    data_persona['ministerio'] = ministerio_instance
                    
                PERSONA_FOLDER = f"{data_persona.get('nombres')}_{data_persona.get('apellido_paterno')}_{data_persona.get('apellido_materno')}_{data_persona.get('documento')}"
                persona_dir = os.path.join(settings.BASE_DIR, "archivos", PERSONA_FOLDER)
                data_persona["ruta_carpeta"]  = persona_dir
                
                try:
                    persona_existente = Persona.objects.filter(documento=data_persona.get('documento')).first()
                    if persona_existente:
                        for key, value in data_persona.items():
                            setattr(persona_existente, key, value)
                        persona_existente.save()
                        persona_creada = persona_existente
                    else:
                        persona_creada = Persona.objects.create(**data_persona)
                except Exception as e:
                    print(e)
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    
                    
                data_tipo_persona = datos.get('tipo_persona')
                try:
                    tipo_persona_id = data_tipo_persona.get('id')
                    tipo_persona = TipoPersona.objects.get(pk=tipo_persona_id)
                except Exception as e:
                    print("Tipo de persona con este ID no existe.")
                    return Response({"detail": "Tipo de persona con este ID no existe."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    data_persona_tipo_persona = {
                        "persona": persona_creada,
                        "tipo_persona": tipo_persona
                    }
                    persona_tipo_persona_creada = PersonaTipoPersona.objects.create(**data_persona_tipo_persona)
                except Exception as e:
                    print(e)
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

                # if not os.path.exists(persona_dir):
                #     os.makedirs(persona_dir)
                
                archivo_data = datos.get('archivo')
                archivo_adjunto = None
                if archivo_data:
                    archivo_adjunto = archivo_data
                    # format, imgstr = archivo_adjunto.split(';base64,') 
                    # ext = format.split('/')[-1] 
                    # nombre_archivo = f"voucher_{data_curso.get('nombre')}"
                    # decoded_data = base64.b64decode(imgstr)
                    # file_size = len(decoded_data) / 1024
                    # file_size_kb = f"{file_size:.2f} KB"
                    # data = ContentFile(base64.b64decode(imgstr), name=f"{nombre_archivo}.{ext}")
                    # archivo_path = os.path.join(persona_dir, f"{nombre_archivo}.{ext}")

                    # with open(archivo_path, 'wb') as f:
                    #     f.write(data.read())
                    
                    # archivo = Archivo.objects.create(
                    #     modelo="CursoPersona",
                    #     id_modelo=persona_creada.id, 
                    #     nombre=f"{nombre_archivo}.{ext}",
                    #     extension=ext,
                    #     tipo="image",
                    #     subtipo="voucher",
                    #     ruta=archivo_path,
                    #     estado="A",
                    #     tamanio=file_size_kb
                    # )
                    
                html=f"""
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="padding: 0; margin: 0; font-family: Roboto, sans-serif;">
    <div style="width: 100%; padding: 30px; background-color: #004c76; color: #fff; text-align: center; font-size: 24px;">
        SISTEMA DE REGISTRO IACYM MANCHAY
    </div>
    <div style="padding: 30px;">
        <h3 style="font-weight: bold; text-align: center; font-size: 20px;">
            Se ha detectado un nuevo registro en la academia biblica
        </h3>
        <table style="padding-top: 30px; width: 100%; max-width: 800px; margin: 0 auto 0 auto; border-collapse: collapse; text-align: left; border-radius: 5px;">
            <tr>
                <th style="border: 1px solid #ddd; border-radius: 5px; padding: 8px; background-color: #f2f2f2; font-weight: bold;">Campo</th>
                <th style="border: 1px solid #ddd; border-radius: 5px; padding: 8px; background-color: #f2f2f2; font-weight: bold;">Valor</th>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">Curso</td>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">{curso_instance.nombre}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">Alumno</td>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">{persona_creada.nombre_completo}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">Celular</td>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">{persona_creada.celular}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">Email</td>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">{persona_creada.email}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">Docmuento</td>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">{tipo_documento_instance.nombre} {persona_creada.documento}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">Edad</td>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">{persona_creada.edad}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">Ministerio</td>
                <td style="border: 1px solid #ddd; border-radius: 5px; padding: 8px;">{ministerio_instance.nombre}</td>
            </tr>
        </table>
    </div>
</body>
</html>
"""             
                print("Se enviara un correo")
                def enviar_correo_asincrono():
                    datos = {
                        "archivo": persona_creada.documento,
                        "email": persona_creada.email
                    }
                    email = Email()
                    email.enviar_html(datos, html=html, archivo_adjunto=archivo_adjunto)
                
                thread = threading.Thread(target=enviar_correo_asincrono)
                thread.start()
                print("Correo enviado en segundo plano.")
            try:
                dataPost = {
                    "curso": curso_instance,
                    "persona": persona_creada
                }
                curso_persona_creada = CursoPersona.objects.create(**dataPost)
            except IntegrityError as e:
                if e.args[0] == 1062:
                    print(e.args[0])
                    return Response({"detail": f"Una persona con estos datos ya está registrada al curso de {curso_instance.nombre}."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(e)
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            curso_persona_serializer = self.get_serializer(curso_persona_creada)
            
            return Response(curso_persona_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# =========================== APIS =======================
class VerArchivoApi(APIView):
    def post(self, request):
        try:
            datos = request.data
            print(datos)
            archivo = Archivo.objects.filter(
                modelo=datos.get("nombre_modelo"),
                id_modelo=datos.get("id_elemento"),
                tipo=datos.get("tipo"),
                subtipo=datos.get("subtipo")
            ).first()
            
            print(archivo)
            
            if archivo and os.path.exists(archivo.ruta):
                with open(archivo.ruta, 'rb') as image_file:
                    image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                return Response({'base64': image_base64})
            else:
                return Response({'error': 'Archivo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
        except KeyError as e:
            return Response({'error': f'Clave faltante: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ObtenerPermisosApi(APIView):
    def get(self, request):
        try:
            permisos_grupos = []
            PERMISOS = Permission.objects.all()
            CONTENT_TYPES = ContentType.objects.all()

            for tipo in CONTENT_TYPES:
                grupo_permiso = {
                    "key": str(tipo.id),
                    "label": tipo.model,
                    "data": f"{tipo.app_label}_{tipo.model}",
                    "children": []
                }
                for permiso in PERMISOS:
                    if tipo.id == permiso.content_type_id:
                        permiso_obj = {
                            "key":f"{tipo.id}-{permiso.id}",
                            "label": permiso.name,
                            "data": permiso.codename
                        }
                        grupo_permiso["children"].append(permiso_obj)
                
                permisos_grupos.append(grupo_permiso)
            return Response({'permisos': permisos_grupos}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ObtenerGruposApi(APIView):
    def get(self, request):
        try:
            grupos_ = []
            GRUPOS = Group.objects.all()
            
            # key_master = 0
            for grupo in GRUPOS:
                grupo_ = {
                    "key": str(grupo.id),
                    "label": grupo.name,
                    "data": grupo.name
                }
                
                # key_master += 1
                
                grupos_.append(grupo_)
            return Response({'grupos': grupos_}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ObtenerPermisosUsuarioApi(APIView):
    def post(self, request):
        try:
            datos = request.data
            print(datos)
            username = datos.get('username')
            if not username:
                return Response({'error': 'El nombre de usuario es requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            permisos = user.user_permissions.all() | Permission.objects.filter(group__user=user)
            permisos_distinct = permisos.distinct()
            permisos_serializados = PermisosSerializer(permisos_distinct, many=True).data

            permisos_usuario = []
            for permiso in permisos_distinct:
                permisos_usuario.append(permiso.codename)
            
            print("permisos_usuario")
            print(permisos_usuario)
            
            
            return Response({'permisos_usuario': permisos_usuario}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class RegistroCursoPersonaApi(APIView):
    def get(self, request):
        try:
            registros = CursoPersona.objects.all()
            registros_serializados = CursoPersonaReadSerializer(registros, many=True).data
            print("registros_serializados")
            print(registros_serializados)
            return Response({'registros': registros_serializados}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    @transaction.atomic
    def post(self, request):
        try:
            datos = request.data
            data_persona = datos.get('persona')
            print(1)
            fecha_nacimiento = data_persona.get('fecha_nacimiento')
            if fecha_nacimiento:
                data_persona['fecha_nacimiento'] = formatearFecha(fecha_nacimiento)
            fecha_bautismo = data_persona.get('fecha_bautismo')
            if fecha_bautismo:
                data_persona['fecha_bautismo'] = formatearFecha(fecha_bautismo)
            
            tipo_documento_data = data_persona.get('tipo_documento')
            if tipo_documento_data:
                tipo_documento_instance = TipoDocumento.objects.get(pk=tipo_documento_data.get('id'))
                data_persona['tipo_documento'] = tipo_documento_instance
                
            ministerio_data = data_persona.get('ministerio', None)
            if ministerio_data:
                ministerio_instance = Ministerio.objects.get(pk=ministerio_data.get('id'))
                data_persona['ministerio'] = ministerio_instance
                
            print("datos")
            print(datos)
            persona_serializer = PersonaWriteSerializer(data=data_persona)
            print(2)
            print(persona_serializer)
            
            if persona_serializer.is_valid():
                print(3)
                persona_instance = persona_serializer.save()
                print(4)
                
                persona_dir = os.path.join(settings.BASE_DIR, "archivos", f'{persona_instance.nombre_completo}_{persona_instance.documento}')
                os.makedirs(persona_dir, exist_ok=True)
                
                # Guardar archivo si existe
                archivo_data = datos.get('archivo')
                if archivo_data:
                    archivo_nombre = archivo_data.get('nombre', '')
                    archivo_extension = archivo_data.get('extension', '')
                    archivo_base64 = archivo_data.get('contenido_base64', '')
                    
                    if archivo_base64:
                        archivo_file = ContentFile(base64.b64decode(archivo_base64), name=f'{archivo_nombre}.{archivo_extension}')
                        archivo_ruta = os.path.join(persona_dir, archivo_file.name)
                        
                        with open(archivo_ruta, 'wb') as destination:
                            destination.write(archivo_file.read())
                        
                        # Crear instancia de Archivo
                        archivo_db_data = {
                            'modelo': 'Persona',
                            'id_modelo': persona_instance.id,
                            'nombre': archivo_nombre,
                            'extension': archivo_extension,
                            'tipo': archivo_data.get('tipo', ''),
                            'subtipo': archivo_data.get('subtipo', ''),
                            'ruta': archivo_ruta,
                            'estado': 'A',
                            'tamanio': str(os.path.getsize(archivo_ruta)),
                            'desc': archivo_data.get('desc', '')
                        }
                        archivo_serializer = ArchivoSerializer(data=archivo_db_data)
                        
                        if archivo_serializer.is_valid():
                            archivo_serializer.save()
                        else:
                            return Response({
                                'errors': archivo_serializer.errors
                            }, status=status.HTTP_400_BAD_REQUEST)
                
                # Crear CursoPersona usando curso existente
                curso_data = datos.get('curso')
                curso_instance = Curso.objects.get(id=curso_data.get('id'))
                curso_persona_data = {
                    'persona': persona_instance.id,
                    'curso': curso_instance.id,
                }
                curso_persona_serializer = CursoPersonaWriteSerializer(data=curso_persona_data)
                
                if curso_persona_serializer.is_valid():
                    curso_persona_instance = curso_persona_serializer.save()
                    return Response({
                        'persona': persona_serializer.data,
                        'curso_persona': curso_persona_serializer.data,
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'errors': curso_persona_serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                print(10)
                return Response({
                    'errors': persona_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



