import customtkinter as ctk
import os
from tkinter import messagebox
from datetime import datetime
from data_manager import DataManager

# Config
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

# --- THEME COLORS ---
COLORS = {
    "bg_main": "#111827",      # Very dark blue/black
    "bg_sidebar": "#1f2937",   # Dark gray/blue
    "bg_card": "#1f2937",      # Same as sidebar for cards
    "bg_card_hover": "#374151",
    "text_main": "#f9fafb",    # White-ish
    "text_sec": "#9ca3af",     # Gray
    "accent": "#3b82f6",       # Blue
    "success": "#10b981",      # Green
    "warning": "#f59e0b",      # Orange
    "danger": "#ef4444",       # Red
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Recibos Alquiler V2")
        self.geometry("1400x900")

        self.data_manager = DataManager()
        self.data_manager.load_data()

        # Config base theme
        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg_main"])
        self.container.pack(fill="both", expand=True)
        
        # State
        self.current_user = self.data_manager.user

        # Init UI
        if self.current_user:
            self.show_main_view()
        else:
            self.show_login()

    def show_login(self):
        self.clean_container()
        LoginFrame(self.container, self.data_manager, on_success=self.show_main_view).pack(fill="both", expand=True)

    def show_main_view(self):
        self.clean_container()
        MainView(self.container, self.data_manager, logout_callback=self.logout).pack(fill="both", expand=True)

    def logout(self):
        self.clean_container()
        self.show_login()

    def clean_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, data_manager, on_success):
        super().__init__(master, fg_color=COLORS["bg_main"])
        self.data_manager = data_manager
        self.on_success = on_success

        self.place_widgets()

    def place_widgets(self):
        center_frame = ctk.CTkFrame(self, width=400, height=500, fg_color=COLORS["bg_card"], corner_radius=20)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(center_frame, text="Gestor Alquileres", font=("Arial", 28, "bold"), text_color=COLORS["text_main"]).pack(pady=(40, 10))
        ctk.CTkLabel(center_frame, text="Bienvenido de nuevo", font=("Arial", 14), text_color=COLORS["text_sec"]).pack(pady=(0, 30))

        self.entry_name = ctk.CTkEntry(center_frame, placeholder_text="Usuario", width=300, height=40, font=("Arial", 14))
        self.entry_name.pack(pady=10)

        self.entry_code = ctk.CTkEntry(center_frame, placeholder_text="Código Cliente", width=300, height=40, font=("Arial", 14))
        self.entry_code.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(center_frame, placeholder_text="Contraseña", show="*", width=300, height=40, font=("Arial", 14))
        self.entry_pass.pack(pady=10)

        ctk.CTkButton(center_frame, text="Iniciar Sesión", command=self.login, width=300, height=40, font=("Arial", 14, "bold"), fg_color=COLORS["accent"], hover_color="#2563eb").pack(pady=30)
        ctk.CTkButton(center_frame, text="Crear Cuenta", command=self.register, fg_color="transparent", text_color=COLORS["text_sec"], hover_color=COLORS["bg_card_hover"]).pack(pady=5)

    def login(self):
        name = self.entry_name.get()
        code = self.entry_code.get()
        password = self.entry_pass.get()

        user = self.data_manager.user
        if user and user.name == name and user.password == password: # Simple check
            self.on_success()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def register(self):
        name = self.entry_name.get()
        code = self.entry_code.get()
        password = self.entry_pass.get()
        
        if name and password:
            self.data_manager.set_user(name, code, password)
            messagebox.showinfo("Hecho", "Usuario registrado.")
        else:
            messagebox.showwarning("Datos", "Rellena los campos.")

class MainView(ctk.CTkFrame):
    def __init__(self, master, data_manager, logout_callback):
        super().__init__(master, fg_color=COLORS["bg_main"])
        self.data_manager = data_manager
        self.logout_callback = logout_callback

        # Layout: Sidebar (Left) + Content (Right)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

        # Default View
        self.show_view("Dashboard")

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=COLORS["bg_sidebar"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Profile
        user = self.data_manager.user
        profile_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        profile_frame.pack(pady=40, padx=20, fill="x")
        
        # Avatar placeholder circle
        avatar = ctk.CTkFrame(profile_frame, width=60, height=60, corner_radius=30, fg_color=COLORS["accent"])
        avatar.pack(side="left")
        
        info = ctk.CTkFrame(profile_frame, fg_color="transparent")
        info.pack(side="left", padx=15)
        ctk.CTkLabel(info, text=user.name, font=("Arial", 16, "bold"), text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(info, text=f"ID: {user.client_code}", text_color=COLORS["text_sec"], font=("Arial", 12)).pack(anchor="w")

        # Nav Buttons
        self.nav_btn(sidebar, "📊  Dashboard", lambda: self.show_view("Dashboard"))
        self.nav_btn(sidebar, "🏠  Propiedades", lambda: self.show_view("Properties"))
        self.nav_btn(sidebar, "💸  Gastos", lambda: self.show_view("Expenses"))
        
        ctk.CTkButton(sidebar, text="Cerrar Sesión", fg_color=COLORS["bg_card"], hover_color=COLORS["danger"], 
                      command=self.logout_callback).pack(side="bottom", pady=40, padx=20, fill="x")

    def nav_btn(self, parent, text, cmd):
        btn = ctk.CTkButton(parent, text=text, command=cmd, fg_color="transparent", text_color=COLORS["text_sec"], 
                            anchor="w", font=("Arial", 16), height=50, hover_color=COLORS["bg_card_hover"])
        btn.pack(fill="x", padx=10, pady=2)

    def show_view(self, view_name):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        if view_name == "Dashboard":
            DashboardFrame(self.content_area, self.data_manager).pack(fill="both", expand=True)
        elif view_name == "Properties":
            PropertiesListFrame(self.content_area, self.data_manager).pack(fill="both", expand=True)
        elif view_name == "Expenses":
            ExpensesView(self.content_area, self.data_manager).pack(fill="both", expand=True)

class ExpensesView(ctk.CTkFrame):
    def __init__(self, master, data_manager):
        super().__init__(master, fg_color="transparent")
        self.data_manager = data_manager
        
        ctk.CTkLabel(self, text="Gestión de Gastos", font=("Arial", 28, "bold")).pack(pady=20, anchor="w", padx=20)
        
        # Actions
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20)
        ctk.CTkButton(actions, text="+ Añadir Gasto Manual", command=self.add_manual).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Importar XML Banco", fg_color="#F39C12", command=self.import_xml).pack(side="left", padx=5)
        
        # List
        self.scroll = ctk.CTkScrollableFrame(self, label_text="Historial de Gastos")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.refresh_list()

    def refresh_list(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        for exp in sorted(self.data_manager.expenses, key=lambda x: x.date, reverse=True):
            row = ctk.CTkFrame(self.scroll, fg_color=("gray85", "gray25"))
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=exp.date, width=100).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=exp.category, font=("Arial", 12, "bold"), width=100).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=exp.description, anchor="w").pack(side="left", padx=10, expand=True, fill="x")
            ctk.CTkLabel(row, text=f"-{exp.amount} €", text_color="red").pack(side="right", padx=20)

    def add_manual(self):
        # Quick Dialog for manual entry
        dialog = ctk.CTkInputDialog(text="Concepto del gasto:", title="Nuevo Gasto")
        desc = dialog.get_input()
        if desc:
            # Simplification: use generic Amount dialog next
            dialog2 = ctk.CTkInputDialog(text="Cuantía (€):", title="Nuevo Gasto")
            amt = dialog2.get_input()
            if amt:
                try:
                    from models import Expense
                    new_exp = Expense(float(amt), "OTHER", desc)
                    self.data_manager.expenses.append(new_exp)
                    self.data_manager.save_data()
                    self.refresh_list()
                except ValueError:
                    messagebox.showerror("Error", "El importe debe ser numérico")

    def import_xml(self):
        path = ctk.filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
        if path:
            try:
                import xml.etree.ElementTree as ET
                from models import Expense
                
                tree = ET.parse(path)
                root = tree.getroot()
                
                count = 0
                # Basic parsing logic assuming <transaction> structure
                # <transaction><date>2023-01-01</date><amount>100</amount><description>...</description></transaction>
                for item in root.findall(".//transaction"):
                    date = item.find("date").text if item.find("date") is not None else None
                    amount = item.find("amount").text if item.find("amount") is not None else "0"
                    desc = item.find("description").text if item.find("description") is not None else "Importado"
                    
                    if amount:
                        exp = Expense(float(amount), "BANK_IMPORT", desc, date=date)
                        self.data_manager.expenses.append(exp)
                        count += 1
                
                self.data_manager.save_data()
                self.refresh_list()
                messagebox.showinfo("Importación", f"Se han importado {count} movimientos.")
            except Exception as e:
                messagebox.showerror("Error Importación", f"No se pudo leer el XML: {e}")

# --- Placeholders for specific Views (to be implemented next) ---

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, data_manager):
        super().__init__(master, fg_color="transparent")
        self.data_manager = data_manager
        
        # Header
        ctk.CTkLabel(self, text="Dashboard", font=("Arial", 32, "bold"), text_color=COLORS["text_main"]).pack(anchor="w", pady=(0, 20))
        
        # Stats Grid
        self.stats_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_grid.pack(fill="x", pady=(0, 30))
        self.stats_grid.grid_columnconfigure((0,1,2), weight=1)
        
        self.calc_stats()

        # Recent Receipts Table
        ctk.CTkLabel(self, text="Últimos Recibos", font=("Arial", 20, "bold"), text_color=COLORS["text_main"]).pack(anchor="w", pady=(0, 15))
        
        self.table_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=15)
        self.table_frame.pack(fill="both", expand=True)
        
        self.populate_table()

    def calc_stats(self):
        total_income = 0
        total_expenses = 0
        for prop in self.data_manager.properties:
            # Sum rent from all tenants
            total_income += sum(t.rent for t in prop.tenants)
            total_expenses += prop.mortgage_monthly
            
        current_month = datetime.now().strftime("%Y-%m")
        for exp in self.data_manager.expenses:
            if exp.date and exp.date.startswith(current_month): total_expenses += exp.amount
                
        profit = total_income - total_expenses
        
        self.stat_card(0, "Ganancias Totales", f"{total_income:,.2f} €", COLORS["success"], "▲ +12%")
        self.stat_card(1, "Beneficios Netos", f"{profit:,.2f} €", COLORS["accent"], "▲ +8%")
        self.stat_card(2, "Gastos", f"-{total_expenses:,.2f} €", COLORS["danger"], "▼ -2%")

    def stat_card(self, col, title, value, color, trend):
        card = ctk.CTkFrame(self.stats_grid, fg_color=COLORS["bg_card"], corner_radius=15, height=150)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        
        ctk.CTkLabel(card, text=title, text_color=COLORS["text_sec"], font=("Arial", 14)).place(x=20, y=20)
        ctk.CTkLabel(card, text=value, text_color=color, font=("Arial", 32, "bold")).place(x=20, y=50)
        
        # Mock Graph Line
        canvas = ctk.CTkCanvas(card, width=150, height=40, bg=COLORS["bg_card"], highlightthickness=0)
        canvas.place(x=20, y=100)
        # Draw a simple jagged line
        coords = [0, 30, 30, 10, 60, 25, 90, 5, 120, 20, 150, 0]
        canvas.create_line(coords, fill=color, width=2, smooth=True)

    def populate_table(self):
        # Header Row
        headers = ["PROPIEDAD", "INQUILINO", "FECHA", "MONTO", "ESTADO"]
        h_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent", height=40)
        h_frame.pack(fill="x", padx=10, pady=5)
        
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, text_color=COLORS["text_sec"], font=("Arial", 12, "bold"), anchor="w").pack(side="left", expand=True, fill="x")

        # Data Rows
        scroll = ctk.CTkScrollableFrame(self.table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        current_month = datetime.now().strftime("%Y-%m")
        rows = 0
        for prop in self.data_manager.properties:
            for tenant in prop.tenants:
                rows += 1
                row = ctk.CTkFrame(scroll, fg_color="transparent", height=50)
                row.pack(fill="x", pady=5)
                
                status, color_code = tenant.get_current_status()
                # Map colors to theme
                bg_badge = COLORS["success"] if color_code == "green" else COLORS["warning"] if color_code == "orange" else COLORS["danger"]
                
                self.cell(row, prop.address)
                self.cell(row, tenant.name)
                self.cell(row, current_month)
                self.cell(row, f"{tenant.rent} €")
                
                # Badge
                b_frame = ctk.CTkFrame(row, fg_color="transparent")
                b_frame.pack(side="left", expand=True, fill="x")
                ctk.CTkLabel(b_frame, text=status, text_color="white", fg_color=bg_badge, corner_radius=8, width=80).pack(anchor="w")

        if rows == 0:
            ctk.CTkLabel(scroll, text="No hay datos recientes", text_color=COLORS["text_sec"]).pack(pady=20)

    def cell(self, parent, text):
        ctk.CTkLabel(parent, text=text, text_color=COLORS["text_main"], anchor="w").pack(side="left", expand=True, fill="x")

class PropertiesListFrame(ctk.CTkFrame):
    def __init__(self, master, data_manager):
        super().__init__(master, fg_color="transparent")
        self.data_manager = data_manager
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="Mis Propiedades", font=("Arial", 28, "bold"), text_color=COLORS["text_main"]).pack(side="left")
        
        btn_add = ctk.CTkButton(header, text="+ Nueva Propiedad", command=self.add_property, 
                                fg_color=COLORS["accent"], hover_color="#2563eb", font=("Arial", 14, "bold"))
        btn_add.pack(side="right")
        
        # Grid Scroll
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.refresh_list()

    def refresh_list(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        # Grid Layout Logic: 3 Columns
        for i, prop in enumerate(self.data_manager.properties):
            self.create_card(prop, i)

    def create_card(self, prop, index):
        # Calculate Row/Col
        row = index // 3
        col = index % 3
        
        card = ctk.CTkFrame(self.scroll, fg_color=COLORS["bg_card"], corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Image Placeholder (Gray box)
        img_placeholder = ctk.CTkFrame(card, height=120, fg_color=COLORS["bg_card_hover"], corner_radius=15)
        img_placeholder.pack(fill="x", padx=10, pady=10)
        
        # Address
        ctk.CTkLabel(card, text=prop.address, font=("Arial", 16, "bold"), text_color=COLORS["text_main"], anchor="w").pack(fill="x", padx=15)
        
        # Status
        status, color_code = prop.check_payment_status()
        bg_badge = COLORS["success"] if color_code == "green" else COLORS["warning"] if color_code == "orange" else COLORS["danger"]
        if color_code == "gray": bg_badge = COLORS["text_sec"]
        
        ctk.CTkLabel(card, text=f"Estado: {status}", text_color=bg_badge, font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=15, pady=(5, 10))

        # Action Btn
        ctk.CTkButton(card, text="Gestionar", fg_color="transparent", border_width=1, border_color=COLORS["text_sec"], 
                      text_color=COLORS["text_main"], hover_color=COLORS["bg_card_hover"],
                      command=lambda p=prop: self.open_detail(p)).pack(fill="x", padx=15, pady=(0, 15))

    def add_property(self):
        dialog = ctk.CTkInputDialog(text="Dirección:", title="Nueva Propiedad")
        addr = dialog.get_input()
        if addr:
            if self.data_manager.add_property(addr):
                self.refresh_list()
            else:
                messagebox.showwarning("Error", "Ya existe")

    def open_detail(self, prop):
        parent = self.master 
        for w in parent.winfo_children(): w.destroy()
        PropertyDetailViewV2(parent, prop, self.data_manager, back_callback=lambda: self.restore_list(parent)).pack(fill="both", expand=True)

    def restore_list(self, parent):
        for w in parent.winfo_children(): w.destroy()
        PropertiesListFrame(parent, self.data_manager).pack(fill="both", expand=True)

class PropertyDetailViewV2(ctk.CTkFrame):
    def __init__(self, master, prop, data_manager, back_callback):
        super().__init__(master, fg_color=COLORS["bg_main"])
        self.prop = prop
        self.data_manager = data_manager
        self.back_callback = back_callback
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)
        ctk.CTkButton(header, text="< Volver", width=80, command=back_callback, fg_color="transparent", 
                      border_width=1, text_color=COLORS["text_sec"], border_color=COLORS["text_sec"]).pack(side="left")
        ctk.CTkLabel(header, text=prop.address, font=("Arial", 28, "bold"), text_color=COLORS["text_main"]).pack(side="left", padx=20)
        
        # Tabs - Styled
        self.tabview = ctk.CTkTabview(self, fg_color="transparent", segmented_button_fg_color=COLORS["bg_card"],
                                      segmented_button_selected_color=COLORS["accent"],
                                      segmented_button_selected_hover_color=COLORS["bg_card_hover"],
                                      segmented_button_unselected_color=COLORS["bg_card"],
                                      segmented_button_unselected_hover_color=COLORS["bg_card_hover"],
                                      text_color=COLORS["text_sec"])
        self.tabview.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.tab_info = self.tabview.add("Información")
        self.tab_tenant = self.tabview.add("Inquilino")
        self.tab_financial = self.tabview.add("Financiero")
        self.tab_docs = self.tabview.add("Documentos")
        
        self.setup_info_tab()
        self.setup_tenant_tab()
        self.setup_financial_tab()
        self.setup_docs_tab()

    def setup_info_tab(self):
        f = ctk.CTkFrame(self.tab_info, fg_color=COLORS["bg_card"], corner_radius=15)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Grid layout for form
        f.grid_columnconfigure(0, weight=1)
        f.grid_columnconfigure(1, weight=1)
        
        self.entry_addr = self.ui_field(f, "Dirección", self.prop.address, 0, 0)
        self.entry_city = self.ui_field(f, "Ciudad", self.prop.city, 0, 1)
        self.entry_zip = self.ui_field(f, "Código Postal", self.prop.zip_code, 1, 0)
        self.entry_cntry = self.ui_field(f, "País", self.prop.country, 1, 1)
        self.entry_ref = self.ui_field(f, "Ref. Catastral", self.prop.cadastral_ref, 2, 0)
        
        ctk.CTkButton(f, text="Guardar Cambios", command=self.save_info, fg_color=COLORS["success"], 
                      hover_color="#059669", height=40).grid(row=3, column=0, columnspan=2, pady=40)

    def ui_field(self, parent, label, value, row, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(frame, text=label, text_color=COLORS["text_sec"], font=("Arial", 12)).pack(anchor="w")
        e = ctk.CTkEntry(frame, width=300, fg_color=COLORS["bg_main"], border_color=COLORS["bg_card_hover"],
                         text_color=COLORS["text_main"], font=("Arial", 14), height=35)
        e.insert(0, value)
        e.pack(anchor="w", pady=(5, 0), fill="x")
        return e

    def save_info(self):
        self.prop.address = self.entry_addr.get()
        self.prop.city = self.entry_city.get()
        self.prop.zip_code = self.entry_zip.get()
        self.prop.country = self.entry_cntry.get()
        self.prop.cadastral_ref = self.entry_ref.get()
        self.data_manager.save_data()
        messagebox.showinfo("Guardado", "Datos actualizados correctamente.")

    def setup_tenant_tab(self):
        self.frame_tenant = ctk.CTkFrame(self.tab_tenant, fg_color=COLORS["bg_card"], corner_radius=15)
        self.frame_tenant.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header actions
        actions = ctk.CTkFrame(self.frame_tenant, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(actions, text="Listado de Inquilinos", font=("Arial", 20, "bold"), text_color=COLORS["text_main"]).pack(side="left")
        ctk.CTkButton(actions, text="+ Añadir Inquilino", command=self.show_add_tenant_form, 
                      fg_color=COLORS["accent"], hover_color="#2563eb").pack(side="right")
        
        self.tenants_list_scroll = ctk.CTkScrollableFrame(self.frame_tenant, fg_color="transparent")
        self.tenants_list_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.refresh_tenants_list()

    def refresh_tenants_list(self):
        for w in self.tenants_list_scroll.winfo_children(): w.destroy()
        
        if not self.prop.tenants:
            ctk.CTkLabel(self.tenants_list_scroll, text="No hay inquilinos asignados.", text_color=COLORS["text_sec"]).pack(pady=40)
            return

        for index, t in enumerate(self.prop.tenants):
            self.render_tenant_card(t, index)

    def render_tenant_card(self, tenant, index):
        card = ctk.CTkFrame(self.tenants_list_scroll, fg_color=COLORS["bg_main"], corner_radius=10)
        card.pack(fill="x", pady=10)
        
        # Info
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(info, text=tenant.name, font=("Arial", 18, "bold"), text_color=COLORS["text_main"]).pack(side="left")
        ctk.CTkLabel(info, text=f"Renta: {tenant.rent} €", font=("Arial", 14), text_color=COLORS["accent"]).pack(side="left", padx=20)
        
        status, color = tenant.get_current_status()
        bg_badge = COLORS["success"] if color == "green" else COLORS["warning"] if color == "orange" else COLORS["danger"]
        ctk.CTkLabel(info, text=status, text_color="white", fg_color=bg_badge, corner_radius=6, width=80).pack(side="right")

        # Actions Row
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=15, pady=(0, 15))
        
        if status != "Pagado":
            ctk.CTkButton(actions, text="Marcar Pagado", height=30, fg_color=COLORS["success"], width=120,
                          command=lambda t=tenant: self.mark_paid(t)).pack(side="left", padx=(0, 10))
                          
        ctk.CTkButton(actions, text="Generar Recibo", height=30, fg_color=COLORS["accent"], width=120,
                      command=lambda t=tenant: self.generate_receipt_pdf(t)).pack(side="left", padx=(0, 10))
                          
        ctk.CTkButton(actions, text="Editar", height=30, fg_color="transparent", border_width=1, border_color=COLORS["text_sec"], width=80,
                      command=lambda t=tenant: self.edit_tenant(t)).pack(side="left", padx=5)
                      
        ctk.CTkButton(actions, text="Eliminar", height=30, fg_color=COLORS["danger"], width=80,
                      command=lambda t=tenant: self.remove_tenant(t)).pack(side="right")

    def generate_receipt_pdf(self, tenant):
        try:
            from receipt_generator import ReceiptGenerator
            generator = ReceiptGenerator()
            path = generator.generate_receipt(tenant, self.prop)
            if messagebox.askyesno("Recibo Generado", f"Se ha generado el recibo:\n{path}\n\n¿Quieres abrirlo?"):
                os.system(f"open '{path}'")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al generar PDF: {e}")

    def show_add_tenant_form(self, tenant_to_edit=None):
        # Using a Toplevel or overlay might be complex, let's replace the list view temporarily
        self.clean_tenant_frame()
        
        title_txt = "Editar Inquilino" if tenant_to_edit else "Nuevo Inquilino"
        ctk.CTkLabel(self.frame_tenant, text=title_txt, font=("Arial", 20, "bold"), text_color=COLORS["text_main"]).pack(pady=20)
        
        entry_name = ctk.CTkEntry(self.frame_tenant, placeholder_text="Nombre Completo", width=300, height=40)
        entry_name.pack(pady=10)
        
        entry_rent = ctk.CTkEntry(self.frame_tenant, placeholder_text="Renta Mensual (€)", width=300, height=40)
        entry_rent.pack(pady=10)
        
        if tenant_to_edit:
            entry_name.insert(0, tenant_to_edit.name)
            entry_rent.insert(0, str(tenant_to_edit.rent))

        btns = ctk.CTkFrame(self.frame_tenant, fg_color="transparent")
        btns.pack(pady=20)
        
        ctk.CTkButton(btns, text="Cancelar", fg_color="transparent", border_width=1, border_color=COLORS["text_sec"],
                      command=self.setup_tenant_tab).pack(side="left", padx=10)
                      
        ctk.CTkButton(btns, text="Guardar", fg_color=COLORS["accent"],
                      command=lambda: self.save_tenant(entry_name.get(), entry_rent.get(), tenant_to_edit)).pack(side="left", padx=10)

    def clean_tenant_frame(self):
        for w in self.frame_tenant.winfo_children(): w.destroy()

    def save_tenant(self, name, rent_str, existing_tenant=None):
        if name and rent_str:
            try:
                rent = float(rent_str)
                if existing_tenant:
                    existing_tenant.name = name
                    existing_tenant.rent = rent
                else:
                    from models import Tenant
                    new_t = Tenant(name, rent)
                    self.prop.tenants.append(new_t)
                
                self.data_manager.save_data()
                self.setup_tenant_tab() # Refresh list
            except ValueError:
                messagebox.showerror("Error", "Renta debe ser número")

    def edit_tenant(self, tenant):
        self.show_add_tenant_form(tenant)

    def mark_paid(self, tenant):
        current_month = datetime.now().strftime("%Y-%m")
        tenant.payments[current_month] = "PAID"
        self.data_manager.save_data()
        self.refresh_tenants_list()

    def remove_tenant(self, tenant):
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {tenant.name}?"):
            self.prop.tenants.remove(tenant)
            self.data_manager.save_data()
            self.refresh_tenants_list()

    def setup_financial_tab(self):
        f = ctk.CTkFrame(self.tab_financial, fg_color=COLORS["bg_card"], corner_radius=15)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(f, text="Hipoteca / Préstamo", font=("Arial", 18, "bold"), text_color=COLORS["text_main"]).pack(anchor="w", pady=20, padx=20)
        
        # Mortgage Field (Using pack instead of ui_field which forces grid)
        frame_mortgage = ctk.CTkFrame(f, fg_color="transparent")
        frame_mortgage.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(frame_mortgage, text="Cuota Mensual (€)", text_color=COLORS["text_sec"], font=("Arial", 12)).pack(anchor="w")
        self.entry_mortgage = ctk.CTkEntry(frame_mortgage, width=300, fg_color=COLORS["bg_main"], border_color=COLORS["bg_card_hover"],
                                           text_color=COLORS["text_main"], font=("Arial", 14), height=35)
        self.entry_mortgage.insert(0, str(self.prop.mortgage_monthly))
        self.entry_mortgage.pack(anchor="w", pady=(5, 0), fill="x")
        
        # Utilities
        ctk.CTkLabel(f, text="Suministros", font=("Arial", 18, "bold"), text_color=COLORS["text_main"]).pack(anchor="w", pady=(30, 10), padx=20)
        self.var_utils = ctk.BooleanVar(value=self.prop.utilities_included)
        ctk.CTkCheckBox(f, text="Gastos (Luz/Agua) incluidos en el alquiler (Restar del beneficio)", 
                        variable=self.var_utils, text_color=COLORS["text_main"]).pack(anchor="w", pady=5, padx=20)
                        
        ctk.CTkButton(f, text="Guardar Configuración Financiera", command=self.save_finance, 
                      fg_color=COLORS["accent"], height=40).pack(pady=40, padx=20, anchor="w")
        
        # Profit Preview
        profit = self.prop.calculate_profit(self.data_manager.expenses) 
        ctk.CTkLabel(f, text=f"Beneficio estimado este mes: {profit} €", font=("Arial", 20, "bold"), text_color=COLORS["success"]).pack(pady=10, padx=20, anchor="w")

    def save_finance(self):
        try:
            self.prop.mortgage_monthly = float(self.entry_mortgage.get())
            self.prop.utilities_included = self.var_utils.get()
            self.data_manager.save_data()
            messagebox.showinfo("Guardado", "Datos financieros actualizados.")
        except ValueError:
            messagebox.showerror("Error", "La cuota debe ser un número.")

    def setup_docs_tab(self):
        f = ctk.CTkFrame(self.tab_docs, fg_color=COLORS["bg_card"], corner_radius=15)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Property Docs
        ctk.CTkLabel(f, text="Documentación Propiedad", font=("Arial", 16, "bold"), text_color=COLORS["text_main"]).pack(anchor="w", pady=10, padx=20)
        self.doc_row(f, "Contrato Luz", self.prop.electricity_contract_path, "electricity_contract_path")
        self.doc_row(f, "Contrato Agua", self.prop.water_contract_path, "water_contract_path")
        self.doc_row(f, "Contrato Hipoteca", self.prop.mortgage_contract_path, "mortgage_contract_path")
        
        # Tenant Docs - Selector
        ctk.CTkLabel(f, text="Documentación Inquilinos", font=("Arial", 16, "bold"), text_color=COLORS["text_main"]).pack(anchor="w", pady=(20, 10), padx=20)
        
        if self.prop.tenants:
            # Selector
            sel_frame = ctk.CTkFrame(f, fg_color="transparent")
            sel_frame.pack(fill="x", padx=20)
            ctk.CTkLabel(sel_frame, text="Seleccionar Inquilino:", text_color=COLORS["text_sec"]).pack(side="left")
            
            tenant_names = [t.name for t in self.prop.tenants]
            self.selected_tenant_name = ctk.StringVar(value=tenant_names[0])
            combo = ctk.CTkComboBox(sel_frame, values=tenant_names, variable=self.selected_tenant_name, 
                                    command=self.refresh_tenant_docs_area)
            combo.pack(side="left", padx=10)
            
            self.tenant_docs_area = ctk.CTkFrame(f, fg_color="transparent")
            self.tenant_docs_area.pack(fill="x", pady=10)
            
            self.refresh_tenant_docs_area(None)
            
        else:
            ctk.CTkLabel(f, text="No hay inquilinos asignados.", text_color=COLORS["text_sec"]).pack(anchor="w", padx=20)

    def refresh_tenant_docs_area(self, _):
        for w in self.tenant_docs_area.winfo_children(): w.destroy()
        
        name = self.selected_tenant_name.get()
        tenant = next((t for t in self.prop.tenants if t.name == name), None)
        
        if tenant:
            self.doc_row(self.tenant_docs_area, "Contrato Alquiler", tenant.lease_contract_path, "lease_contract_path", target_obj=tenant)
            self.doc_row(self.tenant_docs_area, "Depósito Fianza", tenant.deposit_contract_path, "deposit_contract_path", target_obj=tenant)

    def doc_row(self, parent, label, current_path, attr_name, target_obj=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5, padx=20)
        
        ctk.CTkLabel(row, text=label, width=150, anchor="w", text_color=COLORS["text_main"]).pack(side="left")
        
        status = "✅ Subido" if current_path else "❌ No archivo"
        color = COLORS["success"] if current_path else COLORS["text_sec"]
        ctk.CTkLabel(row, text=status, text_color=color, width=100).pack(side="left")
        
        obj_to_update = target_obj if target_obj else self.prop
        
        ctk.CTkButton(row, text="Subir/Cambiar", width=100, fg_color=COLORS["bg_main"], hover_color=COLORS["bg_card_hover"],
                      command=lambda: self.upload_file(attr_name, obj_to_update)).pack(side="left", padx=10)
                      
        if current_path:
             ctk.CTkButton(row, text="Abrir", width=60, fg_color="transparent", border_width=1, border_color=COLORS["text_sec"],
                           command=lambda: os.system(f"open '{current_path}'")).pack(side="left")

    def upload_file(self, attr_name, target_obj):
        path = ctk.filedialog.askopenfilename()
        if path:
            setattr(target_obj, attr_name, path)
            self.data_manager.save_data()
            if target_obj == self.prop:
                self.setup_docs_tab()
            else:
                self.refresh_tenant_docs_area(None) 

class ExpensesView(ctk.CTkFrame):
    def __init__(self, master, data_manager):
        super().__init__(master, fg_color="transparent")
        self.data_manager = data_manager
        
        ctk.CTkLabel(self, text="Gestión de Gastos", font=("Arial", 28, "bold"), text_color=COLORS["text_main"]).pack(pady=20, anchor="w", padx=20)
        
        # Actions
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20)
        ctk.CTkButton(actions, text="+ Añadir Gasto Manual", command=self.add_manual, 
                      fg_color=COLORS["accent"], height=35).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Importar XML Banco", fg_color="transparent", border_width=1, border_color=COLORS["warning"], text_color=COLORS["warning"],
                      command=self.import_xml).pack(side="left", padx=5)
        
        # Header for List
        header = ctk.CTkFrame(self, fg_color="transparent", height=30)
        header.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkLabel(header, text="FECHA", width=100, anchor="w", text_color=COLORS["text_sec"], font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header, text="CATEGORÍA", width=100, anchor="w", text_color=COLORS["text_sec"], font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header, text="DESCRIPCIÓN", width=300, anchor="w", text_color=COLORS["text_sec"], font=("Arial", 12, "bold")).pack(side="left", padx=10, expand=True, fill="x")
        ctk.CTkLabel(header, text="IMPORTE", width=80, anchor="e", text_color=COLORS["text_sec"], font=("Arial", 12, "bold")).pack(side="right", padx=20)

        # List
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_card"], corner_radius=15)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.refresh_list()

    def refresh_list(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        for exp in sorted(self.data_manager.expenses, key=lambda x: x.date, reverse=True):
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=exp.date, width=100, text_color=COLORS["text_main"], anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=exp.category, font=("Arial", 11), text_color=COLORS["text_sec"], width=100, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=exp.description, anchor="w", text_color=COLORS["text_main"]).pack(side="left", padx=10, expand=True, fill="x")
            ctk.CTkLabel(row, text=f"-{exp.amount} €", text_color=COLORS["danger"], font=("Arial", 12, "bold")).pack(side="right", padx=20)

    def add_manual(self):
        dialog = ctk.CTkInputDialog(text="Concepto del gasto:", title="Nuevo Gasto")
        desc = dialog.get_input()
        if desc:
            dialog2 = ctk.CTkInputDialog(text="Cuantía (€):", title="Nuevo Gasto")
            amt = dialog2.get_input()
            if amt:
                try:
                    from models import Expense
                    new_exp = Expense(float(amt), "OTHER", desc)
                    self.data_manager.expenses.append(new_exp)
                    self.data_manager.save_data()
                    self.refresh_list()
                except ValueError:
                    messagebox.showerror("Error", "El importe debe ser numérico")

    def import_xml(self):
        path = ctk.filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
        if path:
            try:
                import xml.etree.ElementTree as ET
                from models import Expense
                
                tree = ET.parse(path)
                root = tree.getroot()
                
                count = 0
                for item in root.findall(".//transaction"):
                    date = item.find("date").text if item.find("date") is not None else None
                    amount = item.find("amount").text if item.find("amount") is not None else "0"
                    desc = item.find("description").text if item.find("description") is not None else "Importado"
                    
                    if amount:
                        exp = Expense(float(amount), "BANK_IMPORT", desc, date=date)
                        self.data_manager.expenses.append(exp)
                        count += 1
                
                self.data_manager.save_data()
                self.refresh_list()
                messagebox.showinfo("Importación", f"Se han importado {count} movimientos.")
            except Exception as e:
                messagebox.showerror("Error Importación", f"No se pudo leer el XML: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
