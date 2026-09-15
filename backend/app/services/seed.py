from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.accounting import Account
from app.models.cash import CashRegister
from app.models.catalog import Brand, Category, TaxRate, UnitOfMeasure
from app.models.company import Branch, Company, Terminal
from app.models.inventory import InventoryBalance
from app.models.party import Customer, Supplier
from app.models.product import Product
from app.models.user import Permission, Role, RolePermission, User, UserRole


PERMISSIONS = [
    ("*", "system", "Todos los permisos"),
    ("sales.create", "sales", "Crear venta"),
    ("sales.cancel", "sales", "Anular venta"),
    ("sales.refund", "sales", "Devolución / NC"),
    ("inventory.create", "inventory", "Crear movimiento"),
    ("inventory.adjust", "inventory", "Ajustar stock"),
    ("inventory.transfer", "inventory", "Transferir"),
    ("cash.open", "cash", "Abrir caja"),
    ("cash.close", "cash", "Cerrar caja"),
    ("cash.withdraw", "cash", "Retiro de caja"),
    ("products.create", "products", "Crear producto"),
    ("products.edit", "products", "Editar producto"),
    ("products.delete", "products", "Eliminar producto"),
    ("accounting.create", "accounting", "Asiento"),
    ("accounting.edit", "accounting", "Editar asiento"),
    ("reports.view", "reports", "Ver reportes"),
    ("reports.export", "reports", "Exportar reportes"),
    ("users.create", "users", "Crear usuario"),
    ("users.edit", "users", "Editar usuario"),
    ("users.disable", "users", "Desactivar usuario"),
    ("purchases.create", "purchases", "Crear compra"),
    ("purchases.approve", "purchases", "Aprobar compra"),
    ("purchases.receive", "purchases", "Recibir mercancía"),
]

ROLES = {
    "super_admin": ("Super Administrador", ["*"]),
    "admin": ("Administrador", [p[0] for p in PERMISSIONS if p[0] != "*"]),
    "manager": ("Gerente", ["reports.view", "reports.export", "sales.create", "inventory.adjust"]),
    "accountant": ("Contador", ["accounting.create", "accounting.edit", "reports.view", "reports.export"]),
    "supervisor": ("Supervisor", ["sales.create", "sales.cancel", "inventory.adjust", "cash.open", "cash.close"]),
    "cashier": ("Cajero", ["sales.create", "cash.open", "cash.close"]),
    "warehouse": ("Almacén", ["inventory.create", "inventory.adjust", "inventory.transfer", "purchases.receive"]),
}

ACCOUNTS = [
    ("1101", "Caja General", "ASSET", "DEBIT"),
    ("1102", "Cuentas por Cobrar", "ASSET", "DEBIT"),
    ("1104", "Inventario de Mercancía", "ASSET", "DEBIT"),
    ("1105", "ITBIS Pagado (Adelantado)", "ASSET", "DEBIT"),
    ("2101", "Cuentas por Pagar (Proveedores)", "LIABILITY", "CREDIT"),
    ("2102", "ITBIS por Pagar", "LIABILITY", "CREDIT"),
    ("3101", "Capital", "EQUITY", "CREDIT"),
    ("4101", "Ingresos por Ventas", "INCOME", "CREDIT"),
    ("5101", "Costo de Ventas", "COST", "DEBIT"),
    ("6101", "Gastos Operativos", "EXPENSE", "DEBIT"),
]

PRODUCTS = [
    ("74600123", "Aceite Vegetal 1L", "Abarrotes", 140, 185, 34),
    ("74600124", "Agua Cristal 600ml", "Bebidas", 12, 25, 115),
    ("74600125", "Arroz Selecto 5lb", "Abarrotes", 200, 265, 34),
    ("74600126", "Cerveza Presidente 650ml", "Bebidas", 95, 150, 48),
    ("74600127", "Cloro Clorox 1gl", "Limpieza", 110, 155, 20),
    ("74600128", "Coca-Cola 2L", "Bebidas", 80, 120, 50),
    ("74600129", "Desodorante Rexona", "Higiene", 110, 165, 22),
    ("74600130", "Detergente Ace 1kg", "Limpieza", 120, 175, 25),
    ("74600131", "Doritos Nacho", "Snacks", 50, 85, 60),
    ("74600133", "Galletas Oreo", "Snacks", 40, 65, 70),
    ("74600134", "Habichuelas Rojas 1lb", "Abarrotes", 40, 65, 60),
    ("74600135", "Jabón de Cuaba", "Higiene", 18, 30, 80),
    ("74600136", "Jugo Rica 1L", "Bebidas", 60, 90, 35),
    ("74600137", "Leche Rica 1L", "Lácteos", 75, 105, 30),
    ("74600138", "Papas Sabritas", "Snacks", 32, 55, 55),
    ("74600139", "Papel Higiénico Scott 4u", "Higiene", 95, 135, 40),
    ("74600140", "Pasta Dental Colgate", "Higiene", 68, 98, 38),
    ("74600141", "Queso Geo 1lb", "Lácteos", 150, 210, 15),
    ("74600142", "Shampoo Head&Shoulders", "Higiene", 170, 240, 18),
    ("74600143", "Yogurt Yoplait", "Lácteos", 42, 68, 68),
]


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(Company.id).limit(1)):
        return

    company = Company(
        name=settings.DEFAULT_COMPANY_NAME,
        legal_name=settings.DEFAULT_COMPANY_NAME,
        rnc="131000000",
        currency=settings.CURRENCY,
        tax_rate=settings.DEFAULT_TAX_RATE,
    )
    db.add(company)
    db.flush()

    branch = Branch(company_id=company.id, name=settings.DEFAULT_BRANCH_NAME, code="SDQ-01")
    db.add(branch)
    db.flush()

    db.add(Terminal(company_id=company.id, branch_id=branch.id, name="Caja 1", code="T01"))
    db.add(CashRegister(company_id=company.id, branch_id=branch.id, name="Caja Principal", code="CAJA-1"))

    perm_map: dict[str, Permission] = {}
    for code, module, desc in PERMISSIONS:
        p = Permission(code=code, module=module, description=desc)
        db.add(p)
        db.flush()
        perm_map[code] = p

    role_map: dict[str, Role] = {}
    for slug, (name, codes) in ROLES.items():
        role = Role(company_id=company.id, name=name, slug=slug, is_system=True)
        db.add(role)
        db.flush()
        role_map[slug] = role
        for code in codes:
            db.add(RolePermission(role_id=role.id, permission_id=perm_map[code].id))

    admin = User(
        company_id=company.id,
        branch_id=branch.id,
        username=settings.DEFAULT_ADMIN_USER,
        full_name="Elias Hughes",
        email="admin@comerciopro.local",
        hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
        is_active=True,
    )
    db.add(admin)
    db.flush()
    db.add(UserRole(user_id=admin.id, role_id=role_map["super_admin"].id))

    tax = TaxRate(company_id=company.id, name="ITBIS 18%", rate=0.18, is_default=True)
    tax_ex = TaxRate(company_id=company.id, name="Exento", rate=0, is_exempt=True)
    db.add_all([tax, tax_ex])
    unit = UnitOfMeasure(company_id=company.id, code="UND", name="Unidad")
    db.add(unit)
    db.flush()

    cats: dict[str, Category] = {}
    for name in ["Abarrotes", "Bebidas", "Limpieza", "Lácteos", "Snacks", "Higiene"]:
        c = Category(company_id=company.id, name=name)
        db.add(c)
        db.flush()
        cats[name] = c

    db.add(Brand(company_id=company.id, name="Genérica"))

    for code, name, cat, cost, price, stock in PRODUCTS:
        p = Product(
            company_id=company.id,
            sku=code,
            barcode=code,
            name=name,
            category_id=cats[cat].id,
            unit_id=unit.id,
            tax_id=tax.id,
            cost=cost,
            price=price,
            wholesale_price=round(price * 0.92, 2),
            min_stock=10,
            reorder_point=15,
            is_active=True,
        )
        db.add(p)
        db.flush()
        db.add(
            InventoryBalance(
                company_id=company.id,
                branch_id=branch.id,
                product_id=p.id,
                qty_on_hand=stock,
                avg_cost=cost,
            )
        )

    db.add_all(
        [
            Customer(company_id=company.id, name="Consumidor Final", is_final_consumer=True, document="00000000000"),
            Customer(company_id=company.id, name="María Pérez", document="00112345678", phone="809-555-1001", credit_limit=5000),
            Customer(company_id=company.id, name="José Ramírez", document="00187654321", phone="809-555-1002"),
            Customer(company_id=company.id, name="Colmado El Sol SRL", document_type="RNC", document="130123456", credit_limit=25000),
            Supplier(company_id=company.id, name="Distribuidora del Cibao", rnc="101000111"),
            Supplier(company_id=company.id, name="Bebidas del Caribe", rnc="101000222"),
            Supplier(company_id=company.id, name="Lácteos del Este", rnc="101000333"),
            Supplier(company_id=company.id, name="Limpieza Pro", rnc="101000444"),
            Supplier(company_id=company.id, name="Abarrotes Nacionales", rnc="101000555"),
        ]
    )

    for code, name, typ, nature in ACCOUNTS:
        db.add(Account(company_id=company.id, code=code, name=name, type=typ, nature=nature))

    db.commit()
