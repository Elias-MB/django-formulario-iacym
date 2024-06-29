from django.db import models
from datetime import date

class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=8)
    desc = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        db_table = 'tbtipodoc'
        managed = True
        verbose_name = 'TipoDocumento'
        verbose_name_plural = 'TipoDocumentos'
        
class TipoPersona(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=8)
    desc = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        db_table = 'tbtipoper'
        managed = True
        verbose_name = 'TipoPersona'
        verbose_name_plural = 'TipoPersonas'        

class Ministerio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    dia_reunion = models.CharField(max_length=100)
    horario_reunion = models.TimeField(auto_now=False, auto_now_add=False)
    estado = models.CharField(max_length=8)
    desc = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        db_table = 'tbminis'
        managed = True
        verbose_name = 'Ministerio'
        verbose_name_plural = 'Ministerios'        

class Persona(models.Model):
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    nombre_completo = models.CharField(max_length=200, blank=True)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    ministerio = models.ForeignKey(Ministerio, on_delete=models.CASCADE)
    documento = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    fecha_conversion = models.DateField(blank=True, null=True)
    fecha_bautismo = models.DateField(blank=True, null=True)
    celular = models.CharField(max_length=15)
    email = models.EmailField(max_length=80)
    estado = models.CharField(max_length=8)
    ruta_carpeta = models.CharField(max_length=250, blank=True, null=True)
    desc = models.TextField(blank=True)
    edad = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.nombre_completo = f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"
        if self.fecha_nacimiento:
            hoy = date.today()
            self.edad = hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        else:
            self.edad = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_completo} » {self.documento}"

    class Meta:
        db_table = 'tmper10'
        managed = True
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

class PersonaTipoPersona(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    tipo_persona = models.ForeignKey(TipoPersona, on_delete=models.CASCADE)
    desc = models.TextField(blank=True)
    
    class Meta:
        db_table = 'tmper20'
        managed = True
        verbose_name = "PersonaTipoPersona"
        verbose_name_plural = "PersonaTipoPersonas"

    def __str__(self):
        return f"{self.persona.nombre_completo}, {self.tipo_persona.nombre}"

class Usuario(models.Model):
    usuario_id = models.CharField(max_length=20, unique=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    estado = models.CharField(max_length=8)
    desc = models.TextField(blank=True)

    def __str__(self):
        return f"{self.persona.nombre_completo} » {self.persona.documento}"

    class Meta:
        db_table = 'tmusu10'
        managed = True
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    nivel = models.CharField(max_length=50)
    duracion = models.CharField(max_length=50, blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    desc = models.TextField(blank=True)
    estado = models.CharField(max_length=8)
    
    class Meta:
        db_table = 'tmcur10'
        managed = True
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return f"{self.nombre}"

class CursoPersona(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    desc = models.TextField(blank=True)
    
    class Meta:
        db_table = 'tmper30'
        managed = True
        verbose_name = "CursoPersona"
        verbose_name_plural = "CursoPersonas"

    def __str__(self):
        return f"{self.curso.nombre}, {self.persona.nombre_completo}"

class Archivo(models.Model):
    modelo = models.CharField(max_length=30)
    id_modelo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=50)
    extension = models.CharField(max_length=5)
    tipo = models.CharField(max_length=20)
    subtipo = models.CharField(max_length=20)
    ruta = models.CharField(max_length=200)
    estado = models.CharField(max_length=8)
    tamanio = models.CharField(max_length=10)
    desc = models.TextField(blank=True)
    
    class Meta:
        db_table = 'tmarch10'
        managed = True
        verbose_name = "Archivo"
        verbose_name_plural = "Archivos"

    def __str__(self):
        return f"{self.nombre}, {self.ruta}"
