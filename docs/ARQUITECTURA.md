# ComercioPro 2.0 — decisiones de diseño

## Qué se conservó del mockup
Identidad visual (brand #f9572a, Inter, cards, POS de 8+4 columnas), menú modular y el flujo Subtotal → Descuento → ITBIS → Total.

## Qué no se copió
Estado en memoria del navegador, `completeSale()` mutando stock, facturas aleatorias, usuario hardcodeado, export CSV ficticio.

## Transacción de venta
`POST /api/v1/sales` ejecuta en una sola sesión SQLAlchemy:

1. Sale + SaleDetails + SalePayments + SaleTaxes
2. InventoryMovement (kardex) y actualización de InventoryBalance
3. CashMovement si hay sesión abierta
4. AccountReceivable si hay CREDIT
5. JournalEntry (Caja/CxC, Ventas, ITBIS, Costo, Inventario)
6. AuditLog

Cualquier excepción hace rollback.

## Multiempresa
`company_id` / `branch_id` en tablas operativas. Una instancia sirve N empresas.

## Billing Engine
Tablas `fiscal_sequences` y `electronic_invoices`. El POS solo envía `ecf_type`. La firma XML / envío DGII se implementa en un servicio aparte para no contaminar el checkout.

## Auth
JWT access + refresh. RBAC con permisos `modulo.accion` (sales.create, cash.close, …).

## Persistencia
Desarrollo: SQLite (`DB_ENGINE=sqlite`).
Producción: SQL Server (`DB_ENGINE=mssql` + pyodbc). Los modelos no dependen del dialecto.
