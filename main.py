import flet as ft
from supabase import create_client
from datetime import date, timedelta
import sys
import traceback

# ================= SUPABASE =================
SUPABASE_URL = "https://oyyjcqnnbvypxbuvvtst.supabase.co"
SUPABASE_KEY = "sb_publishable_R0gNH41T8sfy7v8jVbJbFw_W5-v3-cj"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Sistema de Disfraces"
    page.window_width = 800
    page.window_height = 900
    page.padding = 20
    page.bgcolor = "#F3F4F6"
    
    resultado = ft.Text("", size=14)
    
    # ========== REGISTRAR CLIENTE ==========
    cedula = ft.TextField(label="Cédula", width=300)
    nombre = ft.TextField(label="Nombre completo", width=300)
    telefono = ft.TextField(label="Teléfono", width=300)
    direccion = ft.TextField(label="Dirección", width=300)
    
    def registrar_cliente(e):
        if not cedula.value:
            resultado.value = "⚠️ Ingrese cédula"
            resultado.color = "red"
            resultado.update()
            return
        existe = supabase.table("clientes").select("*").eq("cedula", cedula.value).execute()
        if existe.data:
            resultado.value = f"⚠️ Cliente {cedula.value} ya existe"
            resultado.color = "red"
            resultado.update()
            return
        nuevo = {
            "cedula": cedula.value,
            "nombre": nombre.value,
            "telefono": telefono.value,
            "direccion": direccion.value,
            "veces": 0
        }
        supabase.table("clientes").insert(nuevo).execute()
        resultado.value = f"✅ Cliente {nombre.value} registrado"
        resultado.color = "green"
        resultado.update()
        cedula.value = nombre.value = telefono.value = direccion.value = ""
        for campo in [cedula, nombre, telefono, direccion]:
            campo.update()
    
    # ========== ALQUILER ==========
    cedula_alq = ft.TextField(label="Cédula del cliente", width=300)
    disfraz_alq = ft.TextField(label="Nombre del disfraz", width=300)
    costo_alq = ft.TextField(label="Costo total (C$)", width=150)
    pago_alq = ft.TextField(label="Pago ahora (C$)", width=150)
    dias_alq = ft.TextField(label="Días", width=100, value="3")
    
    def registrar_alquiler(e):
        if not cedula_alq.value:
            resultado.value = "⚠️ Ingrese cédula"
            resultado.color = "red"
            resultado.update()
            return
        cliente = supabase.table("clientes").select("*").eq("cedula", cedula_alq.value).execute()
        if not cliente.data:
            resultado.value = "⚠️ Cliente no encontrado"
            resultado.color = "red"
            resultado.update()
            return
        cliente = cliente.data[0]
        
        try:
            costo_v = float(costo_alq.value) if costo_alq.value else 0
            pago_v = float(pago_alq.value) if pago_alq.value else 0
            dias_v = int(dias_alq.value)
        except:
            resultado.value = "⚠️ Verifique los montos"
            resultado.color = "red"
            resultado.update()
            return
        
        saldo = costo_v - pago_v
        fecha_dev = (date.today() + timedelta(days=dias_v)).isoformat()
        
        nuevo = {
            "cedula_cliente": cedula_alq.value,
            "nombre_cliente": cliente["nombre"],
            "disfraz": disfraz_alq.value,
            "tipo": "alquiler_normal",
            "fecha_salida": date.today().isoformat(),
            "fecha_devolucion_esperada": fecha_dev,
            "costo_total": costo_v,
            "monto_pagado": pago_v,
            "saldo_pendiente": saldo,
            "multa_retraso": 0,
            "multa_perdida": 0
        }
        supabase.table("alquileres").insert(nuevo).execute()
        supabase.table("clientes").update({"veces": cliente["veces"] + 1}).eq("cedula", cedula_alq.value).execute()
        
        resultado.value = f"✅ Alquiler registrado\n🎭 {disfraz_alq.value}\n⏰ Devuelve: {fecha_dev}\n💰 Pagado: C${pago_v:.2f} | Saldo: C${saldo:.2f}"
        resultado.color = "green"
        resultado.update()
        cedula_alq.value = disfraz_alq.value = costo_alq.value = pago_alq.value = ""
        for campo in [cedula_alq, disfraz_alq, costo_alq, pago_alq]:
            campo.update()
    
    # ========== DEVOLUCIÓN ==========
    cedula_dev = ft.TextField(label="Cédula del cliente", width=300)
    multa_retraso = ft.TextField(label="Multa por retraso (C$)", width=200)
    multa_perdida = ft.TextField(label="Multa por pérdida/daño (C$)", width=200)
    
    def verificar_devolucion(e):
        if not cedula_dev.value:
            resultado.value = "⚠️ Ingrese cédula"
            resultado.color = "red"
            resultado.update()
            return
        alquileres = supabase.table("alquileres").select("*").eq("cedula_cliente", cedula_dev.value).eq("tipo", "alquiler_normal").is_("fecha_devolucion_real", "null").execute()
        if not alquileres.data:
            resultado.value = "⚠️ No hay alquileres activos"
            resultado.color = "red"
            resultado.update()
            return
        alq = alquileres.data[0]
        resultado.value = f"🎭 {alq['disfraz']}\n💰 Costo: C${alq['costo_total']:.2f}\n💵 Pagado: C${alq['monto_pagado']:.2f}\n💸 Saldo: C${alq['saldo_pendiente']:.2f}"
        resultado.color = "blue"
        resultado.update()
    
    def confirmar_devolucion(e):
        resultado.value = "Función en desarrollo"
        resultado.color = "orange"
        resultado.update()
    
    # ========== CONSULTAS ==========
    def ver_clientes(e):
        clientes = supabase.table("clientes").select("*").execute()
        if not clientes.data:
            resultado.value = "No hay clientes"
            resultado.color = "orange"
            resultado.update()
            return
        texto = "📋 CLIENTES\n" + "="*35 + "\n"
        for c in clientes.data:
            texto += f"👤 {c['nombre']} - {c['cedula']}\n"
            texto += f"   📞 {c.get('telefono', 'No registrado')}\n"
            texto += f"   📍 {c.get('direccion', 'No registrada')}\n---\n"
        resultado.value = texto
        resultado.color = "blue"
        resultado.update()
    
    def ver_activos(e):
        alquileres = supabase.table("alquileres").select("*").eq("tipo", "alquiler_normal").is_("fecha_devolucion_real", "null").execute()
        if not alquileres.data:
            resultado.value = "✅ No hay alquileres activos"
            resultado.color = "green"
            resultado.update()
            return
        texto = "🎭 ALQUILERES ACTIVOS\n" + "="*35 + "\n"
        for a in alquileres.data:
            texto += f"👤 {a['nombre_cliente']} - {a['disfraz']}\n"
            texto += f"   ⏰ Devuelve: {a['fecha_devolucion_esperada']}\n---\n"
        resultado.value = texto
        resultado.color = "blue"
        resultado.update()
    
    def ver_ingresos(e):
        alquileres = supabase.table("alquileres").select("*").execute()
        total = sum(a["monto_pagado"] for a in alquileres.data)
        resultado.value = f"💰 TOTAL INGRESOS: C${total:.2f}"
        resultado.color = "green"
        resultado.update()
    
    # ========== INTERFAZ ==========
    page.add(
        ft.Container(
            content=ft.Row([ft.Text("🎭", size=45), ft.Text("TRAJES, DISFRACES Y MUCHO MÁS", size=22, weight="bold", color="white")], alignment="center"),
            padding=20, bgcolor="#6B21E6", border_radius=15
        ),
        ft.Card(ft.Container(ft.Column([
            ft.Text("📝 REGISTRAR CLIENTE", weight="bold"),
            cedula, nombre, telefono, direccion,
            ft.ElevatedButton("Guardar Cliente", on_click=registrar_cliente)
        ], spacing=15), padding=20)) if True else ft.Text(""),
        ft.Card(ft.Container(ft.Column([
            ft.Text("🎭 REGISTRAR ALQUILER", weight="bold"),
            cedula_alq, disfraz_alq, ft.Row([costo_alq, pago_alq, dias_alq]),
            ft.ElevatedButton("Registrar Alquiler", on_click=registrar_alquiler)
        ], spacing=15), padding=20)) if True else ft.Text(""),
        ft.Card(ft.Container(ft.Column([
            ft.Text("🔄 REGISTRAR DEVOLUCIÓN", weight="bold"),
            cedula_dev,
            ft.ElevatedButton("Verificar Alquiler", on_click=verificar_devolucion),
            ft.Row([multa_retraso, multa_perdida]),
            ft.ElevatedButton("Confirmar Devolución", on_click=confirmar_devolucion)
        ], spacing=15), padding=20)) if True else ft.Text(""),
        ft.Card(ft.Container(ft.Column([
            ft.Text("📊 CONSULTAS", weight="bold"),
            ft.Row([
                ft.ElevatedButton("Ver Clientes", on_click=ver_clientes),
                ft.ElevatedButton("Ver Activos", on_click=ver_activos),
                ft.ElevatedButton("Ver Ingresos", on_click=ver_ingresos)
            ])
        ], spacing=15), padding=20)) if True else ft.Text(""),
        ft.Container(content=resultado, padding=20)
    )

if __name__ == "__main__":
    ft.app(target=main, host="0.0.0.0", port=8000)
