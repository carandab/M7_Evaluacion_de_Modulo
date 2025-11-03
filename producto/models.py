from django.db import models
from categorias.models import Categoria
from etiquetas.models import Etiqueta


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2) 
    
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='productos'
    )
    
    detalles = models.OneToOneField(
        'DetallesProducto',
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
        related_name='producto'
    )

    etiquetas = models.ManyToManyField(
        Etiqueta, 
        blank=True, 
        related_name='productos'
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre

class DetallesProducto(models.Model):
    peso = models.DecimalField(max_digits=6, decimal_places=2, help_text="Peso en kg")
    dimensiones = models.CharField(max_length=100, blank=True, help_text="Ej: 10x20x5 cm")

    class Meta:
        verbose_name = "Detalles del Producto"
        verbose_name_plural = "Detalles de Productos"

    def __str__(self):
        return f"Detalles (Peso: {self.peso} kg)"