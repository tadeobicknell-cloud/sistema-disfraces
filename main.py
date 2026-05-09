import flet as ft
from supabase import create_client
from datetime import date, timedelta
from calendar import monthrange

# ================= SUPABASE =================
SUPABASE_URL = "https://oyyjcqnnbvypxbuvvtst.supabase.co"
SUPABASE_KEY = "sb_publishable_R0gNH41T8sfy7v8jVbJbFw_W5-v3-cj"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Variables globales para mantener estado entre funciones
alquiler_actual = None

def main(page: ft.Page):
    page.title = "Sistema de Disfraces"
    page.window_width = 800
    page.window_height = 950
    page.padding = 20
    page.bgcolor = "#F3F4F6"
    
    resultado = ft.Text("", size=14)
    
    # ========== CAMPOS ==========
    # Cliente
    cedula = ft.TextField(label="Cédula", width=300)
    nombre = ft.TextField(label="Nombre completo", width=300)
    telefono = ft.TextField(label="Teléfono", width=300)
    direccion = ft.TextField(label="Dirección", width=300)
    
    # Alquiler
    cedula_alq = ft.TextField(label="Cédula del cliente", width=300)
    disfraz_alq = ft.TextField(label="Nombre del disfraz", width=300)
    costo_alq = ft.TextField(label="Costo total (C$)", width=150)
    pago_alq = ft.TextField(label="Pago ahora (C$)", width=150)
    dias_alq = ft.TextField(label="Días", width=100, value="3")
    
    # Reserva
    cedula_res = ft.TextField(label="Cédula del cliente", width=300)
    disfraz_res = ft.TextField(label="Nombre del disfraz", width=300)
    costo_res = ft.TextField(label="Costo total (C$)", width=150)
    pago_res = ft.TextField(label="Anticipo (mínimo 50%)", width=150)
    fecha_retiro_res = ft.TextField(label="Fecha de retiro (YYYY-MM-DD)", width=200, value=(date.today() + timedelta(days=1)).isoformat())
    dias_res = ft.TextField(label="Días de alquiler", width=100, value="3")
    
    # Devolución
    cedula_dev = ft.TextField(label="Cédula del cliente", width=300)
    multa_retraso = ft.TextField(label="Multa por retraso (C$)", width=200, visible=False)
    multa_perdida = ft.TextField(label="Multa por pérdida/daño (C$)", width=200, visible=False)
    pago_saldo = ft.TextField(label="Pago de saldo pendiente (C$)", width=200, visible=False)
    
    # Gestión reservas
    reserva_id_retirar = ft.TextField(label="ID de reserva", width=150)
    pago_retiro = ft.TextField(label="Pago adicional al retirar (C$)", width=200)
    reserva_id_cancelar = ft.TextField(label="ID de reserva", width=150)
    
    # Gastos
    gasto_desc = ft.TextField(label="Descripción del gasto", width=300)
    gasto_monto = ft.TextField(label="Monto (C$)", width=150)
    
    # Calendario
    fecha_calendario = ft.TextField(label="Fecha (YYYY-MM-DD)", width=200, value=date.today().isoformat())
    
    # ========== FUNCIONES ==========
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
    
    def registrar_reserva(e):
        if not cedula_res.value:
            resultado.value = "⚠️ Ingrese cédula"
            resultado.color = "red"
            resultado.update()
            return
        cliente = supabase.table("clientes").select("*").eq("cedula", cedula_res.value).execute()
        if not cliente.data:
            resultado.value = "⚠️ Cliente no encontrado"
            resultado.color = "red"
            resultado.update()
            return
        cliente = cliente.data[0]
        
        try:
            costo_v = float(costo_res.value) if costo_res.value else 0
            pago_v = float(pago_res.value) if pago_res.value else 0
            dias_v = int(dias_res.value)
            fecha_retiro_obj = date.fromisoformat(fecha_retiro_res.value)
            if fecha_retiro_obj <= date.today():
                resultado.value = "⚠️ Fecha de retiro debe ser futura"
                resultado.color = "red"
                resultado.update()
                return
        except:
            resultado.value = "⚠️ Verifique los datos"
            resultado.color = "red"
            resultado.update()
            return
        
        if pago_v < costo_v * 0.5:
            resultado.value = f"⚠️ El anticipo debe ser al menos el 50% (mínimo C${costo_v * 0.5:.2f})"
            resultado.color = "red"
            resultado.update()
            return
        
        fecha_dev = (fecha_retiro_obj + timedelta(days=dias_v)).isoformat()
        saldo = costo_v - pago_v
        
        nuevo = {
            "cedula_cliente": cedula_res.value,
            "nombre_cliente": cliente["nombre"],
            "disfraz": disfraz_res.value,
            "tipo": "reserva",
            "fecha_retiro": fecha_retiro_res.value,
            "fecha_salida": fecha_retiro_res.value,
            "fecha_devolucion_esperada": fecha_dev,
            "costo_total": costo_v,
            "monto_pagado": pago_v,
            "saldo_pendiente": saldo,
            "estado_reserva": "activa",
            "multa_retraso": 0,
            "multa_perdida": 0
        }
        supabase.table("alquileres").insert(nuevo).execute()
        supabase.table("clientes").update({"veces": cliente["veces"] + 1}).eq("cedula", cedula_res.value).execute()
        
        resultado.value = f"✅ Reserva registrada!\n🎭 {disfraz_res.value}\n📅 Retiro: {fecha_retiro_res.value}\n⏰ Devuelve: {fecha_dev}\n💰 Anticipo: C${pago_v:.2f} | Saldo: C${saldo:.2f}"
        resultado.color = "green"
        resultado.update()
        cedula_res.value = disfraz_res.value = costo_res.value = pago_res.value = ""
        for campo in [cedula_res, disfraz_res, costo_res, pago_res]:
            campo.update()
    
    def ver_reservas_activas(e):
        reservas = supabase.table("alquileres").select("*").eq("tipo", "reserva").eq("estado_reserva", "activa").is_("fecha_devolucion_real", "null").execute()
        if not reservas.data:
            resultado.value = "📭 No hay reservas activas"
            resultado.color = "blue"
            resultado.update()
            return
        texto = "📋 RESERVAS ACTIVAS\n" + "="*45 + "\n"
        for r in reservas.data:
            texto += f"ID: {r['id']} | 👤 {r['nombre_cliente']}\n"
            texto += f"   🎭 {r['disfraz']} | Retiro: {r['fecha_retiro']}\n"
            texto += f"   💰 Anticipo: C${r['monto_pagado']:.2f} | Saldo: C${r['saldo_pendiente']:.2f}\n---\n"
        resultado.value = texto
        resultado.color = "blue"
        resultado.update()
    
    def retirar_reserva(e):
        if not reserva_id_retirar.value:
            resultado.value = "⚠️ Ingrese ID de reserva"
            resultado.color = "red"
            resultado.update()
            return
        try:
            reserva = supabase.table("alquileres").select("*").eq("id", int(reserva_id_retirar.value)).eq("tipo", "reserva").eq("estado_reserva", "activa").execute()
            if not reserva.data:
                resultado.value = "⚠️ Reserva no encontrada"
                resultado.color = "red"
                resultado.update()
                return
            reserva = reserva.data[0]
            
            try:
                pago_adicional = float(pago_retiro.value) if pago_retiro.value else 0
            except:
                pago_adicional = 0
            
            nuevo_pagado = reserva["monto_pagado"] + pago_adicional
            nuevo_saldo = reserva["costo_total"] - nuevo_pagado
            
            if nuevo_saldo < 0:
                resultado.value = f"⚠️ El pago excede el saldo. Saldo pendiente: C${reserva['saldo_pendiente']:.2f}"
                resultado.color = "red"
                resultado.update()
                return
            
            supabase.table("alquileres").update({
                "tipo": "alquiler_normal",
                "estado_reserva": None,
                "monto_pagado": nuevo_pagado,
                "saldo_pendiente": nuevo_saldo,
                "fecha_salida": date.today().isoformat(),
                "fecha_devolucion_esperada": (date.today() + timedelta(days=3)).isoformat()
            }).eq("id", int(reserva_id_retirar.value)).execute()
            
            resultado.value = f"✅ Reserva #{reserva_id_retirar.value} retirada\n💰 Pagado ahora: C${pago_adicional:.2f}\n💵 Total pagado: C${nuevo_pagado:.2f} | Saldo: C${nuevo_saldo:.2f}"
            resultado.color = "green"
            resultado.update()
            reserva_id_retirar.value = ""
            pago_retiro.value = ""
            reserva_id_retirar.update()
            pago_retiro.update()
        except Exception as error:
            resultado.value = f"❌ Error: {error}"
            resultado.color = "red"
            resultado.update()
    
    def cancelar_reserva(e):
        if not reserva_id_cancelar.value:
            resultado.value = "⚠️ Ingrese ID de reserva"
            resultado.color = "red"
            resultado.update()
            return
        try:
            reserva = supabase.table("alquileres").select("*").eq("id", int(reserva_id_cancelar.value)).eq("tipo", "reserva").eq("estado_reserva", "activa").execute()
            if not reserva.data:
                resultado.value = "⚠️ Reserva no encontrada"
                resultado.color = "red"
                resultado.update()
                return
            reserva = reserva.data[0]
            
            fecha_retiro = date.fromisoformat(reserva["fecha_retiro"])
            if (fecha_retiro - date.today()).days < 1:
                resultado.value = "⚠️ No se puede cancelar (menos de 1 día antes del retiro)"
                resultado.color = "red"
                resultado.update()
                return
            
            supabase.table("alquileres").delete().eq("id", int(reserva_id_cancelar.value)).execute()
            resultado.value = f"✅ Reserva #{reserva_id_cancelar.value} cancelada"
            resultado.color = "green"
            resultado.update()
            reserva_id_cancelar.value = ""
            reserva_id_cancelar.update()
        except Exception as error:
            resultado.value = f"❌ Error: {error}"
            resultado.color = "red"
            resultado.update()
    
    def verificar_devolucion(e):
        nonlocal alquiler_actual
        if not cedula_dev.value:
            resultado.value = "⚠️ Ingrese cédula"
            resultado.color = "red"
            resultado.update()
            return
        
        alquileres = supabase.table("alquileres").select("*").eq("cedula_cliente", cedula_dev.value).eq("tipo", "alquiler_normal").is_("fecha_devolucion_real", "null").execute()
        if not alquileres.data:
            resultado.value = "⚠️ No hay alquileres activos para este cliente"
            resultado.color = "red"
            resultado.update()
            return
        
        alquiler_actual = alquileres.data[0]
        
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
        
        saldo_actual = alquiler_actual["saldo_pendiente"]
        pago_saldo.visible = saldo_actual > 0
        pago_saldo.label = f"Pago de saldo pendiente (C${saldo_actual:.2f})"
        pago_saldo.update()
        
        resultado.value = f"🎭 {alquiler_actual['disfraz']}\n👤 {alquiler_actual['nombre_cliente']}\n📅 Salida: {alquiler_actual['fecha_salida']}\n⏰ Devuelve: {alquiler_actual['fecha_devolucion_esperada']}\n{retraso_texto}\n💰 Costo: C${alquiler_actual['costo_total']:.2f}\n💵 Pagado: C${alquiler_actual['monto_pagado']:.2f}\n💸 Saldo pendiente: C${saldo_actual:.2f}"
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
        
        saldo_actual = alquiler_actual["saldo_pendiente"]
        
        try:
            pago_saldo_v = float(pago_saldo.value) if pago_saldo.value else 0
        except:
            pago_saldo_v = 0
        
        if saldo_actual > 0 and pago_saldo_v < saldo_actual:
            resultado.value = f"⚠️ Debe pagar el saldo pendiente de C${saldo_actual:.2f}"
            resultado.color = "red"
            resultado.update()
            return
        
        try:
            retraso = float(multa_retraso.value) if multa_retraso.value else 0
            perdida = float(multa_perdida.value) if multa_perdida.value else 0
        except:
            retraso = perdida = 0
        
        nuevo_pagado = alquiler_actual["monto_pagado"] + pago_saldo_v
        total_cobrado = nuevo_pagado + retraso + perdida
        
        supabase.table("alquileres").update({
            "fecha_devolucion_real": date.today().isoformat(),
            "monto_pagado": nuevo_pagado,
            "saldo_pendiente": 0,
            "multa_retraso": retraso,
            "multa_perdida": perdida
        }).eq("id", alquiler_actual["id"]).execute()
        
        resultado.value = f"✅ Devolución registrada\n💰 Total cobrado: C${total_cobrado:.2f}"
        resultado.color = "green"
        resultado.update()
        
        cedula_dev.value = ""
        multa_retraso.value = ""
        multa_perdida.value = ""
        pago_saldo.value = ""
        multa_retraso.visible = False
        multa_perdida.visible = False
        pago_saldo.visible = False
        for campo in [cedula_dev, multa_retraso, multa_perdida, pago_saldo]:
            campo.update()
        alquiler_actual = None
    
    def registrar_gasto(e):
        if not gasto_desc.value or not gasto_monto.value:
            resultado.value = "⚠️ Complete descripción y monto"
            resultado.color = "red"
            resultado.update()
            return
        try:
            monto_v = float(gasto_monto.value)
        except:
            resultado.value = "⚠️ Monto inválido"
            resultado.color = "red"
            resultado.update()
            return
        nuevo = {
            "descripcion": gasto_desc.value,
            "monto": monto_v,
            "fecha": date.today().isoformat()
        }
        supabase.table("gastos").insert(nuevo).execute()
        resultado.value = f"✅ Gasto registrado: {gasto_desc.value} - C${monto_v:.2f}"
        resultado.color = "green"
        resultado.update()
        gasto_desc.value = ""
        gasto_monto.value = ""
        gasto_desc.update()
        gasto_monto.update()
    
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
        alquileres = supabase.table("alquileres").select("*").eq("tipo", "alquiler_normal").is_("fecha_devolucion_real", "null").execute()
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
        moras = supabase.table("alquileres").select("*").eq("tipo", "alquiler_normal").is_("fecha_devolucion_real", "null").lt("fecha_devolucion_esperada", hoy).execute()
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
    
    def ver_ingresos_por_fecha(e):
        try:
            fecha_sel = date.fromisoformat(fecha_calendario.value)
        except:
            resultado.value = "⚠️ Formato de fecha inválido. Use YYYY-MM-DD"
            resultado.color = "red"
            resultado.update()
            return
        
        alquileres = supabase.table("alquileres").select("*").execute()
        gastos = supabase.table("gastos").select("monto").execute()
        
        ingresos_dia = sum(a["monto_pagado"] for a in alquileres.data if a["fecha_salida"] == fecha_sel.isoformat())
        
        lunes = fecha_sel - timedelta(days=fecha_sel.weekday())
        domingo = lunes + timedelta(days=6)
        ingresos_semana = sum(a["monto_pagado"] for a in alquileres.data if lunes <= date.fromisoformat(a["fecha_salida"]) <= domingo)
        
        primer_dia_mes = date(fecha_sel.year, fecha_sel.month, 1)
        ultimo_dia_mes = date(fecha_sel.year, fecha_sel.month, monthrange(fecha_sel.year, fecha_sel.month)[1])
        ingresos_mes = sum(a["monto_pagado"] for a in alquileres.data if primer_dia_mes <= date.fromisoformat(a["fecha_salida"]) <= ultimo_dia_mes)
        gastos_mes = sum(g["monto"] for g in gastos.data if primer_dia_mes <= date.fromisoformat(g["fecha"]) <= ultimo_dia_mes)
        
        total_ingresos = sum(a["monto_pagado"] for a in alquileres.data)
        total_gastos = sum(g["monto"] for g in gastos.data) if gastos.data else 0
        ganancia_total = total_ingresos - total_gastos
        
        lunes_str = lunes.strftime("%d/%m/%Y")
        domingo_str = domingo.strftime("%d/%m/%Y")
        mes_str = fecha_sel.strftime("%B %Y")
        
        texto = f"""
🏪 TRAJES, DISFRACES Y MUCHO MÁS
{'='*50}

📆 INGRESOS POR FECHA
   Fecha: {fecha_sel.strftime('%d/%m/%Y')}
   💰 Total del día: C${ingresos_dia:.2f}

📅 INGRESOS DE LA SEMANA
   Período: {lunes_str} al {domingo_str}
   💰 Total de la semana: C${ingresos_semana:.2f}

📆 CIERRE MENSUAL - {mes_str}
   💰 Ingresos del mes: C${ingresos_mes:.2f}
   💸 Gastos del mes: C${gastos_mes:.2f}
   📊 Flujo del mes: C${ingresos_mes - gastos_mes:.2f}

{'='*50}
💰 TOTAL INGRESOS (histórico): C${total_ingresos:.2f}
💸 TOTAL GASTOS (histórico): C${total_gastos:.2f}
📈 GANANCIA REAL TOTAL: C${ganancia_total:.2f}
"""
        resultado.value = texto
        resultado.color = "green" if ganancia_total >= 0 else "red"
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
        
        ft.Card(ft.Container(ft.Column([
            ft.Text("📝 REGISTRAR CLIENTE", size=18, weight="bold", color="#6B21E6"),
            cedula, nombre, telefono, direccion,
            ft.ElevatedButton("Guardar Cliente", on_click=registrar_cliente, bgcolor="#3B82F6", color="white")
        ], spacing=15), padding=20), elevation=3),
        
        ft.Card(ft.Container(ft.Column([
            ft.Text("📅 REGISTRAR RESERVA (50% mínimo)", size=18, weight="bold", color="#6B21E6"),
            cedula_res, disfraz_res, ft.Row([costo_res, pago_res]), fecha_retiro_res, dias_res,
            ft.ElevatedButton("Registrar Reserva", on_click=registrar_reserva, bgcolor="#6B21E6", color="white"),
            ft.ElevatedButton("Ver Reservas Activas", on_click=ver_reservas_activas, bgcolor="#3B82F6", color="white"),
            ft.Row([reserva_id_retirar, pago_retiro]),
            ft.ElevatedButton("Retirar Reserva (convertir a alquiler)", on_click=retirar_reserva, bgcolor="#10B981", color="white"),
            ft.Row([reserva_id_cancelar]),
            ft.ElevatedButton("Cancelar Reserva", on_click=cancelar_reserva, bgcolor="#EF4444", color="white")
        ], spacing=15), padding=20), elevation=3),
        
        ft.Card(ft.Container(ft.Column([
            ft.Text("🎭 REGISTRAR ALQUILER", size=18, weight="bold", color="#F97316"),
            cedula_alq, disfraz_alq, ft.Row([costo_alq, pago_alq, dias_alq]),
            ft.ElevatedButton("Registrar Alquiler", on_click=registrar_alquiler, bgcolor="#F97316", color="white")
        ], spacing=15), padding=20), elevation=3),
        
        ft.Card(ft.Container(ft.Column([
            ft.Text("🔄 REGISTRAR DEVOLUCIÓN", size=18, weight="bold", color="#10B981"),
            cedula_dev,
            ft.ElevatedButton("Verificar Alquiler", on_click=verificar_devolucion, bgcolor="#3B82F6", color="white"),
            pago_saldo,
            ft.Row([multa_retraso, multa_perdida]),
            ft.ElevatedButton("Confirmar Devolución", on_click=confirmar_devolucion, bgcolor="#10B981", color="white")
        ], spacing=15), padding=20), elevation=3),
        
        ft.Card(ft.Container(ft.Column([
            ft.Text("💸 REGISTRAR GASTO", size=18, weight="bold", color="#EF4444"),
            ft.Row([gasto_desc, gasto_monto]),
            ft.ElevatedButton("Guardar Gasto", on_click=registrar_gasto, bgcolor="#EF4444", color="white")
        ], spacing=15), padding=20), elevation=3),
        
        ft.Card(ft.Container(ft.Column([
            ft.Text("📊 CONSULTAS", size=18, weight="bold", color="#6B21E6"),
            ft.Row([
                ft.ElevatedButton("Ver Clientes", on_click=ver_clientes, bgcolor="#3B82F6", color="white"),
                ft.ElevatedButton("Ver Activos", on_click=ver_activos, bgcolor="#3B82F6", color="white"),
            ]),
            ft.Row([
                ft.ElevatedButton("Ver en Mora", on_click=ver_moras, bgcolor="#EF4444", color="white"),
            ]),
        ], spacing=15), padding=20), elevation=3),
        
        ft.Card(ft.Container(ft.Column([
            ft.Text("📆 REPORTE DE INGRESOS", size=18, weight="bold", color="#6B21E6"),
            ft.Row([fecha_calendario, ft.ElevatedButton("Ver Ingresos", on_click=ver_ingresos_por_fecha, bgcolor="#10B981", color="white")]),
        ], spacing=15), padding=20), elevation=3),
        
        ft.Container(content=ft.Column([
            ft.Text("📋 RESULTADOS:", size=16, weight="bold", color="#6B21E6"),
            ft.Container(content=resultado, padding=15, bgcolor="#F9FAFB", border_radius=10)
        ], spacing=10), padding=20)
    )

if __name__ == "__main__":
    ft.app(target=main, host="0.0.0.0", port=8000)
