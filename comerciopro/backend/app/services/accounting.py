from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.accounting import Account, JournalEntry, JournalEntryLine
from app.services.sequences import next_journal_number


ACCOUNT_CODES = {
    "CASH": "1101",
    "AR": "1102",
    "INVENTORY": "1104",
    "ITBIS_PAID": "1105",
    "AP": "2101",
    "ITBIS_PAYABLE": "2102",
    "SALES": "4101",
    "COGS": "5101",
    "EXPENSE": "6101",
}


def get_account(db: Session, company_id: int, code: str) -> Account:
    acc = db.scalar(select(Account).where(Account.company_id == company_id, Account.code == code))
    if not acc:
        raise RuntimeError(f"Cuenta {code} no existe en el catálogo")
    return acc


def post_entry(
    db: Session,
    *,
    company_id: int,
    branch_id: int | None,
    user_id: int | None,
    source: str,
    source_id: str,
    concept: str,
    lines: list[tuple[str, float, float, str | None]],
) -> JournalEntry:
    entry = JournalEntry(
        company_id=company_id,
        branch_id=branch_id,
        number=next_journal_number(db, company_id),
        source=source,
        source_id=source_id,
        concept=concept,
        user_id=user_id,
        status="POSTED",
    )
    db.add(entry)
    db.flush()
    debit_sum = credit_sum = 0.0
    for code, debit, credit, memo in lines:
        if debit == 0 and credit == 0:
            continue
        acc = get_account(db, company_id, code)
        db.add(
            JournalEntryLine(
                entry_id=entry.id,
                account_id=acc.id,
                debit=round(debit, 2),
                credit=round(credit, 2),
                memo=memo,
            )
        )
        debit_sum += debit
        credit_sum += credit
    if round(debit_sum, 2) != round(credit_sum, 2):
        raise RuntimeError(f"Asiento desbalanceado D={debit_sum} C={credit_sum}")
    return entry


def post_sale_entry(db, sale, cogs: float) -> JournalEntry:
    cash_amount = sum(float(p.amount) for p in sale.payments if p.method != "CREDIT")
    credit_amount = sum(float(p.amount) for p in sale.payments if p.method == "CREDIT")
    lines = []
    if cash_amount:
        lines.append((ACCOUNT_CODES["CASH"], cash_amount, 0, "Cobro"))
    if credit_amount:
        lines.append((ACCOUNT_CODES["AR"], credit_amount, 0, "Crédito cliente"))
    lines.append((ACCOUNT_CODES["SALES"], 0, float(sale.subtotal) - float(sale.discount_global), "Ingresos"))
    if float(sale.tax_total):
        lines.append((ACCOUNT_CODES["ITBIS_PAYABLE"], 0, float(sale.tax_total), "ITBIS"))
    if cogs:
        lines.append((ACCOUNT_CODES["COGS"], cogs, 0, "Costo de ventas"))
        lines.append((ACCOUNT_CODES["INVENTORY"], 0, cogs, "Salida inventario"))
    return post_entry(
        db,
        company_id=sale.company_id,
        branch_id=sale.branch_id,
        user_id=sale.user_id,
        source="SALE",
        source_id=sale.number,
        concept=f"Venta {sale.number}",
        lines=lines,
    )
