from django.contrib import admin
from .models import Categoria, Producto, Carrito, ItemCarrito, Pedido, DetallePedido

admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Pedido)
admin.site.register(DetallePedido)