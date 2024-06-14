from datetime import timezone
from django.db import models
from django.contrib.auth import User


class Especialidad(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    
    def __str__(self):
        return (f"{self.name}-{self.code}")
    
class Doctor(models.Model):
    TIPOS_DE_MEDICO=[
        ("Residente","Residente"),
        ("Becario","Becario"),
        ("Adscrito","Adscrito"),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPOS_DE_MEDICO)
    especialidad =  models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    email = models.EmailField()
    
    def __str__(self):
        return (f"D.{self.user.username} {self.user.last_name} - {self.tipo}")
    
class Resumen(models.Model):

    ESTADO_CHOICES = [
        ('Solicitud', 'Solicitud'),
        ('En revisión', 'En revisión'),
        ('Listo para enviar', 'Listo para enviar'),
        ('Enviado','Enviado'),
    ]
     
    paciente_nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    numero_expediente = models.CharField(max_length=100)
    motivo_solicitud = models.TextField(max_length=500)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    correo_electronico = models.EmailField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    texto = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Solicitud')
    medico_residente = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='resumenes_por_residente')
    medico_adscrito = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='resumenes_por_adscrito')
    
    def __str__(self):
        return (f"{self.numero_expediente}-{self.especialidad}-{self.estado}")
    
    def save(self, *args, **kwargs):
        if self.pk:
            old_resumen = Resumen.objects.get(pk=self.pk)
            if old_resumen.estado != self.estado:
                EstadoHistorial.objects.create(
                    resumen=self,
                    estado_anterior=old_resumen.estado,
                    estado_nuevo=self.estado,
                    fecha_cambio=timezone.now(),
                    usuario=self.medico_residente.user if self.medico_residente else None  # Ajusta según el usuario que hace el cambio
                )
        super().save(*args, **kwargs)


class EstadoHistorial(models.Model):
    resumen = models.ForeignKey(Resumen, on_delete=models.CASCADE, related_name='historial_estados')
    estado_anterior = models.CharField(max_length=20, choices=Resumen.ESTADO_CHOICES)
    estado_nuevo = models.CharField(max_length=20, choices=Resumen.ESTADO_CHOICES)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.resumen.numero_expediente} cambió de {self.estado_anterior} a {self.estado_nuevo} el {self.fecha_cambio}"