from datetime import datetime


class ExternalWorkerJobResponse(object):
    def __init__(
            self,
            id,
            url,
            correlation_id,
            process_instance_id,
            execution_id,
            scope_id,
            sub_scope_id,
            scope_definition_id,
            scope_type,
            element_id,
            element_name,
            retries,
            exception_message,
            due_date,
            create_time,
            tenant_id,
            lock_owner,
            lock_expiration_time
    ):
        self.id: str = id
        self.url: str = url
        self.correlation_id: str = correlation_id
        self.process_instance_id: str = process_instance_id
        self.execution_id: str = execution_id
        self.scope_id: str = scope_id
        self.sub_scope_id: str = sub_scope_id
        self.scope_definition_id: str = scope_definition_id
        self.scope_type: str = scope_type
        self.element_id: str = element_id
        self.element_name: str = element_name
        self.retries: int = retries
        self.exception_message: str = exception_message
        self.due_date: datetime = due_date
        self.create_time: datetime = create_time
        self.tenant_id: str = tenant_id
        self.lock_owner: str = lock_owner
        self.lock_expiration_time: datetime = lock_expiration_time
