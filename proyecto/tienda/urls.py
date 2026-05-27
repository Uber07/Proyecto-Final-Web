from django.urls import path
from . import views


app_name = 'tienda'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('', views.catalogo, name = 'catalogo'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/quitar_uno/<int:item_id>/', views.quitar_uno_del_carrito, name='quitar_uno_del_carrito'),
    path('carrito/retirar/<int:item_id>/', views.retirar_del_carrito, name='retirar_del_carrito'),
    path('pedido/crear/', views.crear_pedido, name='crear_pedido'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/cancelar/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('admin-panel/productos/', views.admin_listar_productos, name='admin_listar_productos'),
    path('admin-panel/productos/crear/', views.admin_crear_producto, name='admin_crear_producto'),
    path('admin-panel/productos/editar/<int:producto_id>/', views.admin_editar_producto, name='admin_editar_producto'),
    path('admin-panel/productos/eliminar/<int:producto_id>/', views.admin_eliminar_producto, name='admin_eliminar_producto'),
    path('admin-panel/pedidos/', views.admin_listar_pedidos, name='admin_listar_pedidos'),
    path('admin-panel/pedidos/cambiar/<int:pedido_id>/', views.admin_cambiar_estado_pedido, name='admin_cambiar_estado'),
    path('admin-panel/categorias/', views.admin_listar_categorias, name='admin_listar_categorias'),
    path('admin-panel/categorias/crear/', views.admin_crear_categoria, name='admin_crear_categoria'),
    path('admin-panel/categorias/editar/<int:categoria_id>/', views.admin_editar_categoria, name='admin_editar_categoria'),
    path('admin-panel/categorias/eliminar/<int:categoria_id>/', views.admin_eliminar_categoria, name='admin_eliminar_categoria'),
    path('admin-panel/pedidos/eliminar/<int:pedido_id>/', views.admin_eliminar_pedido, name='admin_eliminar_pedido'),
]
