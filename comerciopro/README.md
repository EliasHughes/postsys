# ComercioPro 2.0

POS + ERP para República Dominicana.

**Stack:** React + TypeScript · FastAPI · SQLAlchemy · SQL Server (MSSQL) / SQLite en desarrollo.

Una venta no es un `UPDATE` suelto en el navegador. Es una transacción SQL atómica:

`Sale + SaleDetails + Payments + InventoryMovement + CashMovement + AccountingEntry + AuditLog`

Si algo falla → `ROLLBACK`. Si todo funciona → `COMMIT`.

## Arranque rápido (desarrollo)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8016

# Frontend
cd frontend
npm install
npm run dev
# http://localhost:3016  →  API http://localhost:8016
```

Login inicial (se crea al arrancar si la BD está vacía):

- Usuario: `admin`
- Contraseña: `Admin123!`
- Rol: Super Administrador

## Arquitectura

```
React + TS  →  FastAPI REST  →  Services  →  Repositories  →  SQL Server
```

Multiempresa / multisucursal desde el día uno: casi todas las tablas llevan `company_id` y, cuando aplica, `branch_id`.

## Módulos

| Área | Contenido |
|---|---|
| POS | Venta rápida, barcode, cliente, crédito, pago mixto, descuentos, cotización, anulación, NC |
| Inventario | Kardex, lotes, vencimientos, ajustes, transferencias, reorden |
| Compras | OC con estados, recepción, CxP, pagos |
| Caja | Apertura, movimientos, cierre, cuadre, sobrante/faltante |
| Contabilidad | Diario automático, catálogo, mayor, comprobación, P&L, BG |
| Clientes / Proveedores | Crédito, estado de cuenta, fidelización (puntos) |
| Seguridad | JWT + refresh, RBAC granular, auditoría |
| Facturación RD | Capa Billing Engine lista para e-CF / DGII (31–45) |

Documentación de diseño: `docs/`.
