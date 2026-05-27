from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .decorators import admin_requerido
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from .models import Producto, Categoria, Carrito, ItemCarrito, Pedido, DetallePedido

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tienda:home')
    else:
        form = UserCreationForm()
    return render(request, 'tienda/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tienda:home')
        else:
            return render(request, 'tienda/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'tienda/login.html')

def logout_view(request):
    logout(request)
    return redirect('tienda:catalogo')

# Redirige al panel correspondiente según el rol
@login_required
def home(request):
    if request.user.is_staff:
        return redirect('tienda:admin_listar_pedidos')  # panel de administrador
    else:
        return redirect('tienda:catalogo')              # catálogo para cliente

def catalogo(request):
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q', '')

    productos = Producto.objects.all()
    categorias = Categoria.objects.all()

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda)
        )

    contexto = {
        'productos': productos,
        'categorias': categorias,
        'busqueda': busqueda,
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
    }
    return render(request, 'tienda/catalogo.html', contexto)

@login_required
@never_cache
def ver_carrito(request):
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    total = sum(item.subtotal() for item in items)
    return render(request, 'tienda/carrito.html', {'items': items, 'total': total})

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))
    if cantidad < 1:
        cantidad = 1

    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    item, creado = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    if not creado:
        item.cantidad += cantidad
    else:
        item.cantidad = cantidad
    item.save()

    # Calcular total de unidades en el carrito
    total_unidades = sum(it.cantidad for it in carrito.items.all())

    # Si la petición es AJAX, devolver JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"Se agregó {producto.nombre} (x{cantidad}) al carrito.",
            'total_unidades': total_unidades
        })

    # Fallback para navegadores sin JavaScript
    messages.success(request, f"Se agregó {producto.nombre} (x{cantidad}) al carrito.")
    return redirect('tienda:catalogo')

@login_required
def quitar_uno_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, pk=item_id, carrito__usuario=request.user)
    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
    else:
        item.delete()
    return redirect('tienda:ver_carrito')

@login_required
def retirar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, pk=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect('tienda:ver_carrito')

@login_required
def crear_pedido(request):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    if not carrito or not carrito.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect('tienda:ver_carrito')

    # Crear el pedido
    pedido = Pedido.objects.create(usuario=request.user, estado='pendiente')

    # Pasar los items del carrito al pedido
    for item in carrito.items.all():
        DetallePedido.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio
        )

    # Vaciar el carrito
    carrito.items.all().delete()

    messages.success(request, "Pedido creado exitosamente.")
    return redirect('tienda:mis_pedidos')

@login_required
def mis_pedidos(request):

    pedidos = request.user.pedidos.order_by('-fecha')
    return render(request, 'tienda/mis_pedidos.html', {'pedidos': pedidos})

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
    if pedido.estado in ['pendiente']:
        pedido.estado = 'cancelado'
        pedido.save()
        messages.success(request, f"Pedido #{pedido.id} cancelado.")
    else:
        messages.error(request, "No se puede cancelar un pedido que ya ha sido enviado o entregado.")
    return redirect('tienda:mis_pedidos')

# ---------- ADMINISTRADOR (sin mensajes) ----------
@admin_requerido
def admin_listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/listar_productos.html', {'productos': productos})

@admin_requerido
def admin_crear_producto(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST['precio']
        stock = request.POST.get('stock', 0)
        categoria_id = request.POST.get('categoria')
        categoria = Categoria.objects.get(pk=categoria_id) if categoria_id else None
        imagen = request.FILES.get('imagen')

        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria,
            imagen=imagen
        )
        return redirect('tienda:admin_listar_productos')
    return render(request, 'tienda/crear_producto.html', {'categorias': categorias})

@admin_requerido
def admin_editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST.get('descripcion', '')
        producto.precio = request.POST['precio']
        producto.stock = request.POST.get('stock', 0)
        categoria_id = request.POST.get('categoria')
        if categoria_id:
            producto.categoria = get_object_or_404(Categoria, pk=categoria_id)
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
        producto.save()
        return redirect('tienda:admin_listar_productos')
    return render(request, 'tienda/editar_producto.html', {'producto': producto, 'categorias': categorias})

@admin_requerido
def admin_eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    producto.delete()
    return redirect('tienda:admin_listar_productos')

@admin_requerido
def admin_listar_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha')
    return render(request, 'tienda/listar_pedidos.html', {'pedidos': pedidos})

@admin_requerido
def admin_cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADOS):
            pedido.estado = nuevo_estado
            pedido.save()
        return redirect('tienda:admin_listar_pedidos')
    return render(request, 'tienda/cambiar_estado.html', {'pedido': pedido, 'estados': Pedido.ESTADOS})

@admin_requerido
def admin_eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    pedido.delete()
    return redirect('tienda:admin_listar_pedidos')

@admin_requerido
def admin_listar_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'tienda/listar_categorias.html', {'categorias': categorias})

@admin_requerido
def admin_crear_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            Categoria.objects.create(nombre=nombre)
            return redirect('tienda:admin_listar_categorias')
    return render(request, 'tienda/crear_categoria.html')

@admin_requerido
def admin_editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            categoria.nombre = nombre
            categoria.save()
            return redirect('tienda:admin_listar_categorias')
    return render(request, 'tienda/editar_categoria.html', {'categoria': categoria})

@admin_requerido
def admin_eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    categoria.delete()
    return redirect('tienda:admin_listar_categorias')