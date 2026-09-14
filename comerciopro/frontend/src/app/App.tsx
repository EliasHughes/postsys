import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import AppLayout from "../layouts/AppLayout";
import LoginPage from "../modules/auth/LoginPage";
import DashboardPage from "../modules/dashboard/DashboardPage";
import PosPage from "../modules/pos/PosPage";
import SalesPage from "../modules/sales/SalesPage";
import ProductsPage from "../modules/products/ProductsPage";
import InventoryPage from "../modules/inventory/InventoryPage";
import PurchasesPage from "../modules/purchases/PurchasesPage";
import SuppliersPage from "../modules/suppliers/SuppliersPage";
import CustomersPage from "../modules/customers/CustomersPage";
import CashPage from "../modules/cash/CashPage";
import AccountingPage from "../modules/accounting/AccountingPage";
import ReportsPage from "../modules/reports/ReportsPage";
import UsersPage from "../modules/users/UsersPage";
import SettingsPage from "../modules/settings/SettingsPage";

function Private({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="h-full grid place-items-center text-slate-400">Cargando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <Private>
            <AppLayout />
          </Private>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="pos" element={<PosPage />} />
        <Route path="ventas" element={<SalesPage />} />
        <Route path="productos" element={<ProductsPage />} />
        <Route path="inventario" element={<InventoryPage />} />
        <Route path="compras" element={<PurchasesPage />} />
        <Route path="proveedores" element={<SuppliersPage />} />
        <Route path="clientes" element={<CustomersPage />} />
        <Route path="caja" element={<CashPage />} />
        <Route path="contabilidad" element={<AccountingPage />} />
        <Route path="reportes" element={<ReportsPage />} />
        <Route path="usuarios" element={<UsersPage />} />
        <Route path="configuracion" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
