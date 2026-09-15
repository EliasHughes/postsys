export default function SettingsPage() {
  return (
    <div className="max-w-xl bg-white dark:bg-slate-900 p-6 rounded-2xl border space-y-3 text-sm">
      <h3 className="font-bold text-lg">Configuración</h3>
      <p className="text-slate-500 text-xs">
        Empresa, sucursales, impuestos, secuencias fiscales y backups se administran aquí.
        El motor de facturación electrónica (e-CF / DGII) queda desacoplado del POS.
      </p>
      <ul className="text-xs space-y-1 text-slate-600">
        <li>• Moneda: DOP / RD$</li>
        <li>• ITBIS por defecto: 18%</li>
        <li>• Tipos e-CF preparados: 31, 32, 33, 34, 41, 43, 44, 45</li>
        <li>• Backup: programar dump diario de SQL Server desde esta pantalla (fase ops)</li>
      </ul>
    </div>
  );
}
