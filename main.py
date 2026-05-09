import os
os.environ["FLET_VIEW_WEB_RENDERER"] = "canvaskit"

import flet as ft
from supabase import create_client
from datetime import date, timedelta

# ================= CONFIGURACIÓN SUPABASE =================
SUPABASE_URL = "https://oyyjcqnnbvypxbuvvtst.supabase.co"
SUPABASE_KEY = "sb_publishable_R0gNH41T8sfy7v8jVbJbFw_W5-v3-cj"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= COLORES =================
COLOR_PRIMARY = "#6B21E6"
COLOR_SECONDARY = "#F97316"
COLOR_SUCCESS = "#10B981"
COLOR_DANGER = "#EF4444"
COLOR_INFO = "#3B82F6"

class AppSistemaDisfraces:
    def __init__(self):
        # Cliente
        self.cedula_input = ft.TextField(label="Cédula", width=300)
        self.nombre_input = ft.TextField(label="Nombre completo", width=300)
        self.telefono_input = ft.TextField(label="Teléfono", width=300)
        self.direccion_input = ft.TextField(label="Dirección", width=300)
        
        # Alquiler normal
        self.cedula_alquiler = ft.TextField(label="Cédula del cliente", width=300)
        self.disfraz_alquiler = ft.TextField(label="Nombre del disfraz", width=300)
        self.costo_alquiler = ft.TextField(label="Costo total (C$)", width=150)
        self.pago_alquiler = ft.TextField(label="Pago ahora (C$)", width=150)
        self.dias_alquiler = ft.TextField(label="Días", width=100, value="3")
        
        # Reserva
        self.cedula_reserva = ft.TextField(label="Cédula del cliente", width=300)
        self.disfraz_reserva = ft.TextField(label="Nombre del disfraz", width=300)
        self.costo_reserva = ft.TextField(label="Costo total (C$)", width=150)
        self.pago_reserva = ft.TextField(label="Pago ahora (mínimo 50%)", width=150)
        self.fecha_retiro_reserva = ft.TextField(label="Fecha de retiro (YYYY-MM-DD)", width=200, value=(date.today() + timedelta(days=1)).isoformat())
        self.dias_reserva = ft.TextField(label="Días", width=100, value="3")
        
        # Devolución
        self.cedula_devolucion = ft.TextField(label="Cédula del cliente", width=300)
        self.multa_retraso_input = ft.TextField(label="💰 Multa por retraso (C$)", width=200, visible=False)
        self.multa_perdida_input = ft.TextField(label="💰 Multa por pérdida/daño (C$)", width=200, visible=False)
        self.detalle_alquiler_card = ft.Container(visible=False)
        
        # Gastos
        self.gasto_desc = ft.TextField(label="Descripción", width=300)
        self.gasto_monto = ft.TextField(label="Monto (C$)", width=150)
        
        # Gestión reservas
        self.reserva_id_retirar = ft.TextField(label="ID de reserva", width=150)
        self.reserva_id_cancelar = ft.TextField(label="ID de reserva", width=150)
        
        self.resultado_texto = ft.Text("", size=14)
        self.alquiler_actual = None
        
        self.form_alquiler = ft.Column(visible=False)
        self.form_reserva = ft.Column(visible=False)
    
    def mostrar_resultado(self, mensaje, color):
        self.resultado_texto.value = mensaje
        self.resultado_texto.color = color
        self.resultado_texto.update()
    
    # ========== CLIENTES ==========
    def registrar_cliente(self, e):
        cedula = self.cedula_input.value
        if not cedula:
            self.mostrar_resultado("⚠️ Ingrese cédula", "red")
            return
        existe = supabase.table("clientes").select("*").eq("cedula", cedula).execute()
        if existe.data:
            self.mostrar_resultado(f"⚠️ Cliente {cedula} ya existe", "red")
            return
        nuevo = {
            "cedula": cedula,
            "nombre": self.nombre_input.value,
            "telefono": self.telefono_input.value,
            "direccion": self.direccion_input.value,
            "veces": 0
        }
        supabase.table("clientes").insert(nuevo).execute()
        self.mostrar_resultado(f"✅ Cliente {self.nombre_input.value} registrado", COLOR_SUCCESS)
        self.cedula_input.value = self.nombre_input.value = self.telefono_input.value = self.direccion_input.value = ""
        for campo in [self.cedula_input, self.nombre_input, self.telefono_input, self.direccion_input]:
            campo.update()
    
    # ========== ALQUILER NORMAL ==========
    def registrar_alquiler_normal(self, e):
        cedula = self.cedula_alquiler.value
        if not cedula:
            self.mostrar_resultado("⚠️ Ingrese cédula", "red")
            return
        cliente = supabase.table("clientes").select("*").eq("cedula", cedula).execute()
        if not cliente.data:
            self.mostrar_resultado("⚠️ Cliente no encontrado", "red")
            return
        cliente = cliente.data[0]
        
        disfraz = self.disfraz_alquiler.value
        if not disfraz:
            self.mostrar_resultado("⚠️ Ingrese disfraz", "red")
            return
        
        try:
            costo = float(self.costo_alquiler.value)
            pago = float(self.pago_alquiler.value) if self.pago_alquiler.value else 0
            dias = int(self.dias_alquiler.value)
        except:
            self.mostrar_resultado("⚠️ Verifique los montos", "red")
            return
        
        fecha_salida = date.today().isoformat()
        fecha_dev = (date.today() + timedelta(days=dias)).isoformat()
        saldo = costo - pago
        
        nuevo = {
            "cedula_cliente": cedula,
            "nombre_cliente": cliente["nombre"],
            "disfraz": disfraz,
            "tipo": "alquiler_normal",
            "fecha_salida": fecha_salida,
            "fecha_devolucion_esperada": fecha_dev,
            "costo_total": costo,
            "valor_pagado": pago,
            "monto_pagado": pago,
            "saldo_pendiente": saldo,
            "estado_pago": "pagado_completo" if saldo <= 0 else "pago_parcial",
            "multa_retraso": 0,
            "multa_perdida": 0,
            "total_pagado": pago
        }
        supabase.table("alquileres").insert(nuevo).execute()
        supabase.table("clientes").update({"veces": cliente["veces"] + 1}).eq("cedula", cedula).execute()
        
        self.mostrar_resultado(f"✅ Alquiler registrado! Devolución: {fecha_dev}\nPagado: C${pago:.2f} | Saldo: C${saldo:.2f}", COLOR_SUCCESS)
        self.cedula_alquiler.value = self.disfraz_alquiler.value = self.costo_alquiler.value = self.pago_alquiler.value = ""
        for campo in [self.cedula_alquiler, self.disfraz_alquiler, self.costo_alquiler, self.pago_alquiler]:
            campo.update()
    
    # ========== RESERVA ==========
    def registrar_reserva(self, e):
        cedula = self.cedula_reserva.value
        if not cedula:
            self.mostrar_resultado("⚠️ Ingrese cédula", "red")
            return
        cliente = supabase.table("clientes").select("*").eq("cedula", cedula).execute()
        if not cliente.data:
            self.mostrar_resultado("⚠️ Cliente no encontrado", "red")
            return
        cliente = cliente.data[0]
        
        disfraz = self.disfraz_reserva.value
        if not disfraz:
            self.mostrar_resultado("⚠️ Ingrese disfraz", "red")
            return
        
        try:
            costo = float(self.costo_reserva.value)
            pago = float(self.pago_reserva.value) if self.pago_reserva.value else 0
            dias = int(self.dias_reserva.value)
            fecha_retiro = date.fromisoformat(self.fecha_retiro_reserva.value)
            if fecha_retiro <= date.today():
                self.mostrar_resultado("⚠️ Fecha de retiro debe ser futura", "red")
                return
        except:
            self.mostrar_resultado("⚠️ Verifique los datos", "red")
            return
        
        if pago < costo * 0.5:
            self.mostrar_resultado("⚠️ Las reservas requieren mínimo 50% de anticipo", "red")
            return
        
        fecha_reserva = date.today().isoformat()
        fecha_retiro_str = fecha_retiro.isoformat()
        fecha_dev = (fecha_retiro + timedelta(days=dias)).isoformat()
        saldo = costo - pago
        
        nuevo = {
            "cedula_cliente": cedula,
            "nombre_cliente": cliente["nombre"],
            "disfraz": disfraz,
            "tipo": "reserva",
            "fecha_reserva": fecha_reserva,
            "fecha_retiro": fecha_retiro_str,
            "fecha_salida": fecha_retiro_str,
            "fecha_devolucion_esperada": fecha_dev,
            "costo_total": costo,
            "valor_pagado": pago,
            "monto_pagado": pago,
            "saldo_pendiente": saldo,
            "estado_pago": "pago_parcial",
            "estado_reserva": "activa",
            "multa_retraso": 0,
            "multa_perdida": 0,
            "total_pagado": pago
        }
        supabase.table("alquileres").insert(nuevo).execute()
        supabase.table("clientes").update({"veces": cliente["veces"] + 1}).eq("cedula", cedula).execute()
        
        self.mostrar_resultado(f"✅ Reserva registrada!\nRetiro: {fecha_retiro_str}\nPagado: C${pago:.2f} | Saldo: C${saldo:.2f}", COLOR_SUCCESS)
        self.cedula_reserva.value = self.disfraz_reserva.value = self.costo_reserva.value = self.pago_reserva.value = ""
        for campo in [self.cedula_reserva, self.disfraz_reserva, self.costo_reserva, self.pago_reserva]:
            campo.update()
    
    # ========== DEVOLUCIÓN ==========
    def verificar_devolucion(self, e):
        cedula = self.cedula_devolucion.value
        if not cedula:
            self.mostrar_resultado("⚠️ Ingrese la cédula", "red")
            return
        
        alquileres = supabase.table("alquileres").select("*").eq("cedula_cliente", cedula).eq("tipo", "alquiler_normal").is_("fecha_devolucion_real", "null").execute()
        
        if not alquileres.data:
            self.mostrar_resultado("⚠️ No hay alquileres activos para este cliente", "red")
            self.detalle_alquiler_card.visible = False
            self.detalle_alquiler_card.update()
            return
        
        self.alquiler_actual = alquileres.data[0]
        
        hoy = date.today()
        fecha_esperada = date.fromisoformat(self.alquiler_actual["fecha_devolucion_esperada"])
        
        if hoy > fecha_esperada:
            dias_retraso = (hoy - fecha_esperada).days
            dias_retraso_texto = f"⚠️ RETRASO: {dias_retraso} días"
            self.multa_retraso_input.visible = True
            self.multa_retraso_input.label = f"💰 Multa por {dias_retraso} días de retraso (C$)"
        else:
            dias_retraso = 0
            dias_retraso_texto = f"✅ A TIEMPO: Faltan {(fecha_esperada - hoy).days} días"
            self.multa_retraso_input.visible = False
        
        info_pago = ""
        if self.alquiler_actual["saldo_pendiente"] > 0:
            info_pago = f"💰 SALDO PENDIENTE: C${self.alquiler_actual['saldo_pendiente']:.2f} (DEBE PAGAR PARA DEVOLVER)"
        
        detalle_content = ft.Column([
            ft.Text(f"🎭 DISFRAZ: {self.alquiler_actual['disfraz']}", size=18, weight="bold", color=COLOR_PRIMARY),
            ft.Text(f"👤 Cliente: {self.alquiler_actual['nombre_cliente']}"),
            ft.Text(f"📅 Fecha salida: {self.alquiler_actual['fecha_salida']}"),
            ft.Text(f"⏰ Devolución esperada: {self.alquiler_actual['fecha_devolucion_esperada']}"),
            ft.Text(dias_retraso_texto, color=COLOR_DANGER if dias_retraso > 0 else COLOR_SUCCESS),
            ft.Text(f"💰 Costo total: C${self.alquiler_actual['costo_total']:.2f}"),
            ft.Text(f"💵 Pagado: C${self.alquiler_actual['monto_pagado']:.2f}"),
            ft.Text(info_pago, color=COLOR_DANGER if self.alquiler_actual["saldo_pendiente"] > 0 else COLOR_SUCCESS),
            ft.Divider(),
            ft.Text("🔍 Verifique que todas las piezas del disfraz estén completas", italic=True, size=12),
        ], spacing=8)
        
        self.detalle_alquiler_card.content = ft.Card(
            content=ft.Container(content=detalle_content, padding=15, bgcolor=ft.Colors.WHITE),
            elevation=3
        )
        self.detalle_alquiler_card.visible = True
        self.detalle_alquiler_card.update()
        
        self.multa_retraso_input.value = ""
        self.multa_perdida_input.visible = True
        self.multa_perdida_input.value = ""
        
        self.multa_retraso_input.update()
        self.multa_perdida_input.update()
        
        if self.alquiler_actual["saldo_pendiente"] > 0:
            self.mostrar_resultado(f"⚠️ El cliente debe pagar el saldo pendiente de C${self.alquiler_actual['saldo_pendiente']:.2f} antes de devolver", "red")
        else:
            self.mostrar_resultado("Ingrese montos adicionales por retraso o pérdida si corresponde", COLOR_INFO)
    
    def confirmar_devolucion(self, e):
        if not self.alquiler_actual:
            self.mostrar_resultado("⚠️ Primero verifique el alquiler", "red")
            return
        
        if self.alquiler_actual["saldo_pendiente"] > 0:
            self.mostrar_resultado(f"⚠️ El cliente debe pagar el saldo pendiente de C${self.alquiler_actual['saldo_pendiente']:.2f} antes de devolver", "red")
            return
        
        try:
            multa_retraso = float(self.multa_retraso_input.value) if self.multa_retraso_input.value else 0
        except:
            multa_retraso = 0
        
        try:
            multa_perdida = float(self.multa_perdida_input.value) if self.multa_perdida_input.value else 0
        except:
            multa_perdida = 0
        
        total_adicional = multa_retraso + multa_perdida
        total_pagado = self.alquiler_actual["monto_pagado"] + total_adicional
        
        supabase.table("alquileres").update({
            "fecha_devolucion_real": date.today().isoformat(),
            "multa_retraso": multa_retraso,
            "multa_perdida": multa_perdida,
            "total_pagado": total_pagado,
            "saldo_pendiente": 0,
            "estado_pago": "pagado_completo"
        }).eq("id", self.alquiler_actual["id"]).execute()
        
        self.mostrar_resultado(
            f"✅ Devolución registrada\n"
            f"   Alquiler: C${self.alquiler_actual['costo_total']:.2f}\n"
            f"   Pagado antes: C${self.alquiler_actual['monto_pagado']:.2f}\n"
            f"   Multa retraso: C${multa_retraso:.2f}\n"
            f"   Multa pérdida: C${multa_perdida:.2f}\n"
            f"   TOTAL COBRADO: C${total_pagado:.2f}",
            COLOR_SUCCESS
        )
        
        self.cedula_devolucion.value = ""
        self.cedula_devolucion.update()
        self.multa_retraso_input.visible = False
        self.multa_perdida_input.visible = False
        self.detalle_alquiler_card.visible = False
        self.multa_retraso_input.update()
        self.multa_perdida_input.update()
        self.detalle_alquiler_card.update()
        self.alquiler_actual = None
    
    # ========== RESERVAS ACTIVAS ==========
    def ver_reservas_activas(self, e):
        reservas = supabase.table("alquileres").select("*").eq("tipo", "reserva").eq("estado_reserva", "activa").is_("fecha_devolucion_real", "null").execute()
        if not reservas.data:
            self.mostrar_resultado("📭 No hay reservas activas", COLOR_INFO)
            return
        resultado = "📋 RESERVAS ACTIVAS\n" + "="*35 + "\n"
        for r in reservas.data:
            resultado += f"ID: {r['id']} | {r['nombre_cliente']}\n"
            resultado += f"   🎭 {r['disfraz']} | Retiro: {r['fecha_retiro']}\n"
            resultado += f"   💵 Pagado: C${r['monto_pagado']:.2f} | Saldo: C${r['saldo_pendiente']:.2f}\n---\n"
        self.mostrar_resultado(resultado, COLOR_INFO)
    
    def retirar_reserva(self, e):
        reserva_id = self.reserva_id_retirar.value
        if not reserva_id:
            self.mostrar_resultado("⚠️ Ingrese ID de reserva", "red")
            return
        try:
            reserva = supabase.table("alquileres").select("*").eq("id", int(reserva_id)).eq("tipo", "reserva").eq("estado_reserva", "activa").execute()
            if not reserva.data:
                self.mostrar_resultado("⚠️ Reserva no encontrada o ya cancelada", "red")
                return
            
            supabase.table("alquileres").update({
                "tipo": "alquiler_normal",
                "estado_reserva": None,
                "fecha_salida": date.today().isoformat(),
                "fecha_devolucion_esperada": (date.today() + timedelta(days=3)).isoformat()
            }).eq("id", reserva_id).execute()
            
            self.mostrar_resultado(f"✅ Reserva #{reserva_id} convertida a alquiler activo", COLOR_SUCCESS)
            self.reserva_id_retirar.value = ""
            self.reserva_id_retirar.update()
        except Exception as error:
            self.mostrar_resultado(f"❌ Error: {error}", "red")
    
    def cancelar_reserva(self, e):
        reserva_id = self.reserva_id_cancelar.value
        if not reserva_id:
            self.mostrar_resultado("⚠️ Ingrese ID de reserva", "red")
            return
        try:
            reserva = supabase.table("alquileres").select("*").eq("id", int(reserva_id)).eq("tipo", "reserva").eq("estado_reserva", "activa").execute()
            if not reserva.data:
                self.mostrar_resultado("⚠️ Reserva no encontrada", "red")
                return
            
            fecha_retiro = date.fromisoformat(reserva["fecha_retiro"])
            if (fecha_retiro - date.today()).days < 1:
                self.mostrar_resultado("⚠️ No se puede cancelar (menos de 1 día antes del retiro)", "red")
                return
            
            supabase.table("alquileres").delete().eq("id", reserva_id).execute()
            self.mostrar_resultado(f"✅ Reserva #{reserva_id} cancelada. El pago NO se registra como ingreso.", COLOR_INFO)
            self.reserva_id_cancelar.value = ""
            self.reserva_id_cancelar.update()
        except Exception as error:
            self.mostrar_resultado(f"❌ Error: {error}", "red")
    
    # ========== GASTOS ==========
    def registrar_gasto(self, e):
        desc = self.gasto_desc.value
        monto = self.gasto_monto.value
        if not desc or not monto:
            self.mostrar_resultado("⚠️ Complete descripción y monto", "red")
            return
        try:
            monto = float(monto)
        except:
            self.mostrar_resultado("⚠️ Monto inválido", "red")
            return
        nuevo = {"descripcion": desc, "monto": monto, "fecha": date.today().isoformat()}
        supabase.table("gastos").insert(nuevo).execute()
        self.mostrar_resultado(f"✅ Gasto registrado: {desc} - C${monto:.2f}", COLOR_SUCCESS)
        self.gasto_desc.value = self.gasto_monto.value = ""
        self.gasto_desc.update(), self.gasto_monto.update()
    
    # ========== CONSULTAS ==========
    def ver_clientes(self, e):
        clientes = supabase.table("clientes").select("*").execute()
        if not clientes.data:
            self.mostrar_resultado("No hay clientes", "orange")
            return
        texto = "📋 CLIENTES\n" + "="*35 + "\n"
        for c in clientes.data:
            texto += f"📌 {c['nombre']} - {c['cedula']}\n"
            texto += f"   📞 Teléfono: {c['telefono'] if c['telefono'] else 'No registrado'}\n"
            texto += f"   📍 Dirección: {c['direccion'] if c['direccion'] else 'No registrada'}\n"
            texto += f"   📊 {c['veces']} alquileres\n---\n"
        self.mostrar_resultado(texto, COLOR_INFO)
    
    def ver_activos(self, e):
        alquileres = supabase.table("alquileres").select("*").eq("tipo", "alquiler_normal").is_("fecha_devolucion_real", "null").execute()
        if not alquileres.data:
            self.mostrar_resultado("✅ No hay alquileres activos", COLOR_SUCCESS)
            return
        texto = "🎭 ALQUILERES ACTIVOS\n" + "="*35 + "\n"
        for a in alquileres.data:
            texto += f"👤 {a['nombre_cliente']} - {a['disfraz']}\n"
            texto += f"   ⏰ Devuelve: {a['fecha_devolucion_esperada']}\n"
            texto += f"   💰 Pagado: C${a['monto_pagado']:.2f} | Saldo: C${a['saldo_pendiente']:.2f}\n---\n"
        self.mostrar_resultado(texto, COLOR_INFO)
    
    def ver_moras(self, e):
        hoy = date.today().isoformat()
        moras = supabase.table("alquileres").select("*").eq("tipo", "alquiler_normal").is_("fecha_devolucion_real", "null").lt("fecha_devolucion_esperada", hoy).execute()
        if not moras.data:
            self.mostrar_resultado("✅ No hay disfraces en mora", COLOR_SUCCESS)
            return
        texto = "🔴 DISFRACES EN MORA\n" + "="*35 + "\n"
        for m in moras.data:
            texto += f"👤 {m['nombre_cliente']} - {m['disfraz']}\n"
            texto += f"   ⏰ Devuelve: {m['fecha_devolucion_esperada']}\n---\n"
        self.mostrar_resultado(texto, COLOR_DANGER)
    
    def ver_ingresos(self, e):
        alquileres = supabase.table("alquileres").select("*").execute()
        gastos = supabase.table("gastos").select("*").execute()
        hoy = date.today()
        
        ingresos_hoy = sum(a["monto_pagado"] for a in alquileres.data if a["fecha_salida"] == hoy.isoformat() and a.get("estado_reserva") != "cancelada")
        total_ingresos = sum(a["monto_pagado"] for a in alquileres.data if a.get("estado_reserva") != "cancelada")
        total_gastos = sum(g["monto"] for g in gastos.data)
        ganancia = total_ingresos - total_gastos
        
        resultado = f"""
🏪 TRAJES, DISFRACES Y MUCHO MÁS
{'='*35}

📆 INGRESOS DE HOY: C${ingresos_hoy:.2f}

{'='*35}
💰 TOTAL INGRESOS: C${total_ingresos:.2f}
💸 TOTAL GASTOS: C${total_gastos:.2f}
📈 GANANCIA REAL: C${ganancia:.2f}
"""
        color = COLOR_SUCCESS if ganancia >= 0 else COLOR_DANGER
        self.mostrar_resultado(resultado, color)
    
    # ========== INTERFAZ ==========
    def build(self):
        header = ft.Container(
            content=ft.Row([
                ft.Text("🎭", size=40),
                ft.Column([
                    ft.Text("TRAJES, DISFRACES Y MUCHO MÁS", size=24, weight="bold", color=COLOR_PRIMARY),
                    ft.Text("Sistema de Gestión", size=14, color=COLOR_SECONDARY),
                ], spacing=0),
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            margin=ft.margin.only(bottom=20),
        )
        
        clientes_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📝 REGISTRAR CLIENTE", size=18, weight="bold", color=COLOR_PRIMARY),
                    self.cedula_input, self.nombre_input, self.telefono_input, self.direccion_input,
                    ft.ElevatedButton("Guardar Cliente", on_click=self.registrar_cliente, bgcolor=COLOR_INFO, color="white"),
                ], spacing=15),
                padding=20,
            ),
            elevation=3,
        )
        
        btn_alquiler = ft.ElevatedButton("🎭 REGISTRAR ALQUILER", on_click=self.mostrar_form_alquiler, bgcolor=COLOR_SECONDARY, color="white", width=250)
        btn_reserva = ft.ElevatedButton("📅 REGISTRAR RESERVA", on_click=self.mostrar_form_reserva, bgcolor=COLOR_PRIMARY, color="white", width=250)
        
        self.form_alquiler = ft.Column([
            ft.Text("ALQUILER NORMAL", size=16, weight="bold", color=COLOR_SECONDARY),
            self.cedula_alquiler, self.disfraz_alquiler,
            ft.Row([self.costo_alquiler, self.pago_alquiler, self.dias_alquiler]),
            ft.ElevatedButton("Registrar Alquiler", on_click=self.registrar_alquiler_normal, bgcolor=COLOR_SECONDARY, color="white"),
        ], spacing=15)
        
        self.form_reserva = ft.Column([
            ft.Text("RESERVA (50% mínimo)", size=16, weight="bold", color=COLOR_PRIMARY),
            self.cedula_reserva, self.disfraz_reserva,
            ft.Row([self.costo_reserva, self.pago_reserva]),
            ft.Row([self.fecha_retiro_reserva, self.dias_reserva]),
            ft.ElevatedButton("Registrar Reserva", on_click=self.registrar_reserva, bgcolor=COLOR_PRIMARY, color="white"),
        ], spacing=15)
        
        self.form_alquiler.visible = False
        self.form_reserva.visible = False
        
        devolucion_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🔄 REGISTRAR DEVOLUCIÓN", size=18, weight="bold", color=COLOR_SUCCESS),
                    self.cedula_devolucion,
                    ft.ElevatedButton("🔍 Verificar Alquiler", on_click=self.verificar_devolucion, bgcolor=COLOR_INFO, color="white"),
                    self.detalle_alquiler_card,
                    ft.Row([self.multa_retraso_input, self.multa_perdida_input]),
                    ft.ElevatedButton("✅ Confirmar Devolución", on_click=self.confirmar_devolucion, bgcolor=COLOR_SUCCESS, color="white"),
                ], spacing=15),
                padding=20,
            ),
            elevation=3,
        )
        
        reservas_gestion = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📋 GESTIÓN DE RESERVAS", size=18, weight="bold", color=COLOR_INFO),
                    ft.Row([
                        ft.Column([
                            ft.Text("Retirar reserva (convertir a alquiler)", weight="bold"),
                            self.reserva_id_retirar,
                            ft.ElevatedButton("✅ Retirar", on_click=self.retirar_reserva, bgcolor=COLOR_SUCCESS, color="white"),
                        ], spacing=10),
                        ft.Column([
                            ft.Text("Cancelar reserva (eliminar sin ingreso)", weight="bold"),
                            self.reserva_id_cancelar,
                            ft.ElevatedButton("❌ Cancelar", on_click=self.cancelar_reserva, bgcolor=COLOR_DANGER, color="white"),
                        ], spacing=10),
                    ]),
                    ft.ElevatedButton("📋 Ver Reservas Activas", on_click=self.ver_reservas_activas, bgcolor=COLOR_INFO, color="white"),
                ], spacing=15),
                padding=20,
            ),
            elevation=3,
        )
        
        gastos_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("💸 REGISTRAR GASTO", size=18, weight="bold", color=COLOR_DANGER),
                    ft.Row([self.gasto_desc, self.gasto_monto]),
                    ft.ElevatedButton("Guardar Gasto", on_click=self.registrar_gasto, bgcolor=COLOR_DANGER, color="white"),
                ], spacing=15),
                padding=20,
            ),
            elevation=3,
        )
        
        consultas_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📊 CONSULTAS", size=18, weight="bold", color=COLOR_PRIMARY),
                    ft.Row([
                        ft.ElevatedButton("Ver Clientes", on_click=self.ver_clientes, bgcolor=COLOR_INFO, color="white"),
                        ft.ElevatedButton("Ver Activos", on_click=self.ver_activos, bgcolor=COLOR_INFO, color="white"),
                    ]),
                    ft.Row([
                        ft.ElevatedButton("Ver en Mora", on_click=self.ver_moras, bgcolor=COLOR_DANGER, color="white"),
                        ft.ElevatedButton("Ver Ingresos", on_click=self.ver_ingresos, bgcolor=COLOR_SUCCESS, color="white"),
                    ]),
                ], spacing=15),
                padding=20,
            ),
            elevation=3,
        )
        
        resultados_area = ft.Container(
            content=ft.Column([
                ft.Text("📋 RESULTADOS:", size=16, weight="bold", color=COLOR_PRIMARY),
                ft.Container(content=self.resultado_texto, padding=15, bgcolor=ft.Colors.GREY_100, border_radius=10),
            ], spacing=10),
            padding=20,
        )
        
        contenedor_tabs = ft.Column([
            header,
            clientes_card,
            ft.Row([btn_alquiler, btn_reserva], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            self.form_alquiler,
            self.form_reserva,
            devolucion_card,
            reservas_gestion,
            gastos_card,
            consultas_card,
            resultados_area,
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
        
        return ft.Container(content=contenedor_tabs, expand=True, padding=20, bgcolor=ft.Colors.GREY_50)
    
    def mostrar_form_alquiler(self, e):
        self.form_alquiler.visible = True
        self.form_reserva.visible = False
        self.form_alquiler.update()
        self.form_reserva.update()
        self.mostrar_resultado("Complete los datos del alquiler normal", COLOR_INFO)
    
    def mostrar_form_reserva(self, e):
        self.form_reserva.visible = True
        self.form_alquiler.visible = False
        self.form_reserva.update()
        self.form_alquiler.update()
        self.mostrar_resultado("Complete los datos de la reserva (mínimo 50% de anticipo)", COLOR_INFO)

def main(page: ft.Page):
    page.title = "TRAJES, DISFRACES Y MUCHO MÁS"
    page.window_width = 850
    page.window_height = 950
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.Colors.GREY_50

    app = AppSistemaDisfraces()
    page.add(app.build())

ft.app(target=main, view=ft.WEB_BROWSER, port=8000)
