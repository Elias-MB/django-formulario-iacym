from django.contrib.auth.models import Permission, Group
from rest_framework import serializers
from django.utils.dateparse import parse_date
from .models import *

""" ====== ====== ====== ====== GENERAL ====== ====== ====== ====== """
class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = '__all__'

class TipoPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPersona
        fields = '__all__'

class MinisterioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ministerio
        fields = '__all__'
        
class PersonaParejaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaPareja
        fields = '__all__'

""" ====== ====== ====== ====== PRINCIPALES ====== ====== ====== ====== """
class PersonaWriteSerializer(serializers.ModelSerializer):
    ministerio = MinisterioSerializer()
    tipo_documento = TipoDocumentoSerializer()
    
    class Meta:
        model = Persona
        fields = '__all__'

class PersonaReadSerializer(serializers.ModelSerializer):
    tipo_documento = TipoDocumentoSerializer(read_only = True)

    class Meta:
        model = Persona
        fields = '__all__'

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'
        
""" ====== ====== ====== ====== RELACIONES ====== ====== ====== ====== """
class PersonaTipoPersonaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaTipoPersona
        fields = '__all__'

class PersonaTipoPersonaReadSerializer(serializers.ModelSerializer):
    persona = PersonaReadSerializer(read_only = True)
    tipo_persona = TipoPersonaSerializer(read_only = True)

    class Meta:
        model = PersonaTipoPersona
        fields = '__all__'

class CursoPersonaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CursoPersona
        fields = '__all__'

class CursoPersonaReadSerializer(serializers.ModelSerializer):
    persona = PersonaReadSerializer(read_only = True)
    curso = CursoSerializer(read_only = True)

    class Meta:
        model = CursoPersona
        fields = '__all__'

class ParejaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pareja
        fields = '__all__'

class ParejaReadSerializer(serializers.ModelSerializer):
    idoneo = PersonaParejaSerializer(read_only = True)
    idonea = PersonaParejaSerializer(read_only = True)

    class Meta:
        model = Pareja
        fields = '__all__'
        
""" ====== ====== ====== ====== USUARIOS ====== ====== ====== ====== """
class UsuarioWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class UsuarioReadSerializer(serializers.ModelSerializer):
    sucursal = PersonaReadSerializer(read_only = True)

    class Meta:
        model = Usuario
        fields = '__all__'
    
""" ====== ====== ====== ====== PERMISOS ====== ====== ====== ====== """
class PermisosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
        
""" ====== ====== ====== ====== GRUPOS PERMISO ====== ====== ====== ====== """
class GruposSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

""" ====== ====== ====== ====== ARCHIVOS ====== ====== ====== ====== """
class ArchivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archivo
        fields = '__all__'
