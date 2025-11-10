from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto, DetallesProducto, ProductoEtiqueta
from .forms import ProductoForm, DetallesProductoForm, ProductoEtiquetaFormSet
from categorias.models import Categoria
from etiquetas.models import Etiqueta
from django.db.models import Q

def index(request):

    context = {
        'total_productos': Producto.objects.count(),
        'total_categorias': Categoria.objects.count(),
        'total_etiquetas': Etiqueta.objects.count(),
    }

    return render(request, 'index.html', context)


def lista_productos(request):

    productos = Producto.objects.select_related('categoria').prefetch_related('etiquetas')
    
    query = request.GET.get('q')
    categoria_id = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    
    categorias = Categoria.objects.all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    
    return render(request, 'producto/lista.html', {
        'productos': productos,
        'categorias': categorias
    })


def detalle_producto(request, id):

    producto = get_object_or_404(Producto, id=id)
    return render(request, 'productos/detalle.html', {'producto': producto})


def crear_producto(request):

    if request.method == 'POST':
        producto_form = ProductoForm(request.POST)
        detalles_form = DetallesProductoForm(request.POST)
        
        if producto_form.is_valid() and detalles_form.is_valid():
            # Guardar detalles
            detalles = detalles_form.save()
            
            # Guardar producto
            producto = producto_form.save(commit=False)
            producto.detalles = detalles
            producto.save()
            
            # Guardar etiquetas usando el modelo through
            etiquetas_seleccionadas = producto_form.cleaned_data.get('etiquetas_seleccionadas')
            if etiquetas_seleccionadas:
                for orden, etiqueta in enumerate(etiquetas_seleccionadas):
                    ProductoEtiqueta.objects.create(
                        producto=producto,
                        etiqueta=etiqueta,
                        orden=orden
                    )
            
            messages.success(request, 'Producto creado exitosamente')
            return redirect('detalle_producto', id=producto.id)
    else:
        producto_form = ProductoForm()
        detalles_form = DetallesProductoForm()
    
    return render(request, 'producto/crear.html', {
        'producto_form': producto_form,
        'detalles_form': detalles_form
    })


def editar_producto(request, id):

    producto = get_object_or_404(Producto, id=id)
    detalles = producto.detalles
    
    if request.method == 'POST':
        producto_form = ProductoForm(request.POST, instance=producto)
        
        if detalles:
            detalles_form = DetallesProductoForm(request.POST, instance=detalles)
        else:
            detalles_form = DetallesProductoForm(request.POST)
        
        etiquetas_formset = ProductoEtiquetaFormSet(request.POST, instance=producto)
        
        if producto_form.is_valid() and detalles_form.is_valid() and etiquetas_formset.is_valid():
            if not detalles:
                detalles = detalles_form.save()
                producto.detalles = detalles
            else:
                detalles_form.save()
            
            producto_form.save()
            etiquetas_formset.save()  # Guarda las relaciones con through
            
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('detalle_producto', id=producto.id)
        
    else:
        producto_form = ProductoForm(instance=producto)
        detalles_form = DetallesProductoForm(instance=detalles) if detalles else DetallesProductoForm()
        etiquetas_formset = ProductoEtiquetaFormSet(instance=producto)
    
    return render(request, 'producto/editar.html', {
        'producto': producto,
        'producto_form': producto_form,
        'detalles_form': detalles_form,
        'etiquetas_formset': etiquetas_formset
    })

def eliminar_producto(request, id):

    producto = get_object_or_404(Producto, id=id)
    
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente')
        return redirect('lista_productos')
    
    return render(request, 'producto/eliminar.html', {'producto': producto})