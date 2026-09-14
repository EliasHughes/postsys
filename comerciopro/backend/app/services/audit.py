from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_action(
    db: Session,
    *,
    user_id: int | None,
    company_id: int | None,
    branch_id: int | None = None,
    ip: str | None = None,
    module: str,
    action: str,
    entity: str | None = None,
    entity_id: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    result: str = "OK",
    message: str | None = None,
) -> AuditLog:
    row = AuditLog(
        user_id=user_id,
        company_id=company_id,
        branch_id=branch_id,
        ip=ip,
        module=module,
        action=action,
        entity=entity,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        result=result,
        message=message,
    )
    db.add(row)
    return row
