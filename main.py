import flet as ft
from supabase import create_client
from datetime import date, timedelta

# ================= SUPABASE =================
SUPABASE_URL = "https://oyyjcqnnbvypxbuvvtst.supabase.co"
SUPABASE_KEY = "sb_publishable_R0gNH41T8sfy7v8jVbJbFw_W5-v3-cj"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Sistema de Disfraces"
    page.window_width = 750
    page.window_height = 850
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
    
    # ========== REGISTRAR ALQUILER ==========
    cedula_alq = ft.TextField(label="Cédula del cliente", width=300)
    disfraz = ft.TextField(label="Nombre del disfraz", width=300)
    costo = ft.TextField(label="Costo total (C$)", width=150)
    pago = ft.TextField(label="Pago ahora (C$)", width=150)
    dias = ft.TextField(label="Días", width=100, value="3")
    
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
            costo_v = float(costo.value) if costo.value else 0
            pago_v = float(pago.value) if pago.value else 0
            dias_v = int(dias.value)
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
            "disfraz": disfraz.value,
            "fecha_salida": date.today().isoformat(),
            "fecha_devolucion_esperada": fecha_dev,
            "costo_total": costo_v,
            "monto_pagado": pago_v,
            "saldo_pendiente": saldo,
            "multa_retraso": 0.0,
            "multa_perdida": 0.0
        }
        supabase.table("alquileres").insert(nuevo).execute()
        supabase.table("clientes").update({"veces": cliente["veces"] + 1}).eq("cedula", cedula_alq.value).execute()
        
        resultado.value = f"✅ Alquiler registrado\n🎭 {disfraz.value}\n⏰ Devuelve: {fecha_dev}\n💵 Pagado: C${pago_v:.2f} | Saldo: C${saldo:.2f}"
        resultado.color = "green"
        resultado.update()
        
        cedula_alq.value = disfraz.value = costo.value = pago.value = ""
        for campo in [cedula_alq, disfraz, costo, pago]:
            campo.update()
    
    # ========== REGISTRAR DEVOLUCIÓN ==========
    cedula_dev = ft.TextField(label="Cédula del cliente", width=300)
    multa_retraso = ft.TextField(label="Multa por retraso (C$)", width=200)
    multa_perdida = ft.TextField(label="Multa por pérdida/daño (C$)", width=200)
    alquiler_actual = None
    
    def verificar_alquiler(e):
        nonlocal alquiler_actual
        if not cedula_dev.value:
            resultado.value = "⚠️ Ingrese cédula"
            resultado.color = "red"
            resultado.update()
            return
        
        alquileres = supabase.table("alquileres").select("*").eq("cedula_cliente", cedula_dev.value).is_("fecha_devolucion_real", "null").execute()
        if not alquileres.data:
            resultado.value = "⚠️ No hay alquileres activos para este cliente"
            resultado.color = "red"
            resultado.update()
            return
        
        alquiler_actual = alquileres.data[0]
        
        # Calcular días de retraso
        fecha_esperada = date.fromisoformat(alquiler_actual["fecha_devolucion_esperada"])
        hoy = date.today()
        if hoy > fecha_esperada:
            dias_retraso = (hoy - fecha_esperada).days
            retraso_texto = f"⚠️ Retraso: {dias_retraso} días"
            multa_retraso.visible = True
            multa_retraso.update()
        else:
            retraso_texto = f"✅ A tiempo. Faltan {(fecha_esperada - hoy).days} días"
            multa_retraso.visible = False
            multa_retraso.update()
        
        resultado.value = f"🎭 {alquiler_actual['disfraz']}\n👤 {alquiler_actual['nombre_cliente']}\n📅 Salida: {alquiler_actual['fecha_salida']}\n⏰ Devuelve: {alquiler_actual['fecha_devolucion_esperada']}\n{retraso_texto}\n💰 Costo: C${alquiler_actual['costo_total']:.2f}\n💵 Pagado: C${alquiler_actual['monto_pagado']:.2f}\n💸 Saldo: C${alquiler_actual['saldo_pendiente']:.2f}"
        resultado.color = "blue"
        resultado.update()
        
        multa_perdida.visible = True
        multa_perdida.update()
    
    def confirmar_devolucion(e):
        nonlocal alquiler_actual
        if not alquiler_actual:
            resultado.value = "⚠️ Primero verifique el alquiler"
            resultado.color = "red"
            resultado.update()
            return
        
        if alquiler_actual.get("saldo_pendiente", 0) > 0:
            resultado.value = f"⚠️ El cliente debe pagar el saldo pendiente de C${alquiler_actual['saldo_pendiente']:.2f}"
            resultado.color = "red"
            resultado.update()
            return
        
        try:
            retraso = float(multa_retraso.value) if multa_retraso.value else 0
            perdida = float(multa_perdida.value) if multa_perdida.value else 0
        except:
            retraso = perdida = 0
        
        total = alquiler_actual["monto_pagado"] + retraso + perdida
        
        supabase.table("alquileres").update({
            "fecha_devolucion_real": date.today().isoformat(),
            "multa_retraso": retraso,
            "multa_perdida": perdida,
            "saldo_pendiente": 0
        }).eq("id", alquiler_actual["id"]).execute()
        
        resultado.value = f"✅ Devolución registrada\n💰 Total cobrado: C${total:.2f}\n   Alquiler: C${alquiler_actual['monto_pagado']:.2f}\n   Multa retraso: C${retraso:.2f}\n   Multa pérdida: C${perdida:.2f}"
        resultado.color = "green"
        resultado.update()
        
        cedula_dev.value = ""
        multa_retraso.value = ""
        multa_perdida.value = ""
        multa_retraso.visible = False
        multa_perdida.visible = False
        for campo in [cedula_dev, multa_retraso, multa_perdida]:
            campo.update()
        alquiler_actual = None
    
    # ========== CONSULTAS ==========
    def ver_clientes(e):
        clientes = supabase.table("clientes").select("*").execute()
        if not clientes.data:
            resultado.value = "No hay clientes registrados"
            resultado.color = "orange"
            resultado.update()
            return
        
        texto = "📋 LISTA DE CLIENTES\n" + "="*45 + "\n"
        for c in clientes.data:
            texto += f"👤 {c['nombre']}\n"
            texto += f"   📌 Cédula: {c['cedula']}\n"
            texto += f"   📞 Teléfono: {c.get('telefono', 'No registrado')}\n"
            texto += f"   📍 Dirección: {c.get('direccion', 'No registrada')}\n"
            texto += f"   📊 Alquileres: {c['veces']}\n---\n"
        resultado.value = texto
        resultado.color = "blue"
        resultado.update()
    
    def ver_activos(e):
        alquileres = supabase.table("alquileres").select("*").is_("fecha_devolucion_real", "null").execute()
        if not alquileres.data:
            resultado.value = "✅ No hay alquileres activos"
            resultado.color = "green"
            resultado.update()
            return
        
        texto = "🎭 ALQUILERES ACTIVOS\n" + "="*45 + "\n"
        for a in alquileres.data:
            texto += f"👤 {a['nombre_cliente']}\n"
            texto += f"   🎭 {a['disfraz']}\n"
            texto += f"   ⏰ Devuelve: {a['fecha_devolucion_esperada']}\n"
            texto += f"   💰 Pagado: C${a['monto_pagado']:.2f}\n"
            texto += f"   💸 Saldo: C${a['saldo_pendiente']:.2f}\n---\n"
        resultado.value = texto
        resultado.color = "blue"
        resultado.update()
    
    def ver_moras(e):
        hoy = date.today().isoformat()
        moras = supabase.table("alquileres").select("*").is_("fecha_devolucion_real", "null").lt("fecha_devolucion_esperada", hoy).execute()
        if not moras.data:
            resultado.value = "✅ No hay disfraces en mora"
            resultado.color = "green"
            resultado.update()
            return
        
        texto = "🔴 DISFRACES EN MORA\n" + "="*45 + "\n"
        for m in moras.data:
            texto += f"👤 {m['nombre_cliente']}\n"
            texto += f"   🎭 {m['disfraz']}\n"
            texto += f"   ⏰ Debía devolver: {m['fecha_devolucion_esperada']}\n---\n"
        resultado.value = texto
        resultado.color = "red"
        resultado.update()
    
    def ver_ingresos(e):
        alquileres = supabase.table("alquileres").select("*").execute()
        gastos = supabase.table("gastos").select("monto").execute()
        
        total_meses = {}
        for a in alquileres.data:
            fecha = a["fecha_salida"][:7]
            total_meses[fecha] = total_meses.get(fecha, 0) + a["monto_pagado"]
        
        total_ingresos = sum(a["monto_pagado"] for a in alquileres.data)
        total_gastos = sum(g["monto"] for g in gastos.data) if gastos.data else 0
        ganancia = total_ingresos - total_gastos
        
        texto = f"""
🏪 SISTEMA DE DISFRACES
{'='*45}

📊 HISTORIAL MENSUAL:
"""
        for fecha, monto in sorted(total_meses.items()):
            texto += f"   {fecha}: C${monto:,.2f}\n"
        
        texto += f"""
{'='*45}
💰 TOTAL INGRESOS: C${total_ingresos:.2f}
💸 TOTAL GASTOS: C${total_gastos:.2f}
📈 GANANCIA REAL: C${ganancia:.2f}
"""
        resultado.value = texto
        resultado.color = "green" if ganancia >= 0 else "red"
        resultado.update()
    
    # ========== INTERFAZ ==========
    page.add(
        ft.Container(
            content=ft.Row([ft.Text("🎭", size=45), ft.Column([
                ft.Text("TRAJES, DISFRACES Y MUCHO MÁS", size=22, weight="bold", color="white"),
                ft.Text("Sistema de Gestión", size=14, color="white")
            ], spacing=0)], alignment="center"),
            padding=20,
            bgcolor="#6B21E6",
            border_radius=15
        ),
        ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text("📝 REGISTRAR CLIENTE", size=18, weight="bold", color="#6B21E6"),
                    cedula, nombre, telefono, direccion,
                    ft.ElevatedButton("Guardar Cliente", on_click=registrar_cliente, bgcolor="#3B82F6", color="white")
                ], spacing=15),
                padding=20
            ),
            elevation=3
        ),
        ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text("🎭 REGISTRAR ALQUILER", size=18, weight="bold", color="#F97316"),
                    cedula_alq, disfraz,
                    ft.Row([costo, pago, dias]),
                    ft.ElevatedButton("Registrar Alquiler", on_click=registrar_alquiler, bgcolor="#F97316", color="white")
                ], spacing=15),
                padding=20
            ),
            elevation=3
        ),
        ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text("🔄 REGISTRAR DEVOLUCIÓN", size=18, weight="bold", color="#10B981"),
                    cedula_dev,
                    ft.ElevatedButton("Verificar Alquiler", on_click=verificar_alquiler, bgcolor="#3B82F6", color="white"),
                    multa_retraso,
                    multa_perdida,
                    ft.ElevatedButton("Confirmar Devolución", on_click=confirmar_devolucion, bgcolor="#10B981", color="white")
                ], spacing=15),
                padding=20
            ),
            elevation=3
        ),
        ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text("📊 CONSULTAS", size=18, weight="bold", color="#6B21E6"),
                    ft.Row([
                        ft.ElevatedButton("Ver Clientes", on_click=ver_clientes, bgcolor="#3B82F6", color="white"),
                        ft.ElevatedButton("Ver Activos", on_click=ver_activos, bgcolor="#3B82F6", color="white"),
                    ]),
                    ft.Row([
                        ft.ElevatedButton("Ver en Mora", on_click=ver_moras, bgcolor="#EF4444", color="white"),
                        ft.ElevatedButton("Ver Ingresos", on_click=ver_ingresos, bgcolor="#10B981", color="white"),
                    ]),
                ], spacing=15),
                padding=20
            ),
            elevation=3
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("📋 RESULTADOS:", size=16, weight="bold", color="#6B21E6"),
                ft.Container(content=resultado, padding=15, bgcolor="#F9FAFB", border_radius=10)
            ], spacing=10),
            padding=20
        )
    )

ft.app(target=main, port=8000)
