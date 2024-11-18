import datetime as dt

from nautobot.apps.jobs import Job, register_jobs
# from nautobot.core.celery import register_jobs
# from nautobot.apps.jobs import Job, register_jobs
from nautobot.users.models import Token
from nautobot.extras.models.secrets import Secret
from nautobot.extras.secrets.exceptions import SecretError
from nautobot.app.jobs import StringVar, IntegerVar, ObjectVar, MultiObjectVar, BooleanVar  
from nautobot.dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Manufacturer,
    Platform,
    Region,
    Site,
)

from nautobot.tenancy.models import Tenant, TenantGroup


name = "AAA Config Policy Job"




class FormEntry:
    """Form entries."""

    tenant_group = MultiObjectVar(model=TenantGroup, required=False)
    tenant = MultiObjectVar(model=Tenant, required=False)
    region = MultiObjectVar(model=Region, required=False)
    site = MultiObjectVar(model=Site, required=False)
    role = MultiObjectVar(model=DeviceRole, required=False)
    manufacturer = MultiObjectVar(model=Manufacturer, required=False)
    platform = MultiObjectVar(model=Platform, required=False)
    device_type = MultiObjectVar(model=DeviceType, required=False)
    device = MultiObjectVar(model=Device, required=False)
    dry_run = BooleanVar(
        label="Dry run",
        default=True,
        required=False,
    )


class ConfigScan(FormEntry, Job):

    """
        AAA Config Policy Job
    """

    class Meta:
        " Metadata needed to implement the backbone site design. "

        name = "AAA Config Policy"
        commit_default = False
        has_sensitive_variables = False
    
    tenant_group = FormEntry.tenant_group
    tenant = FormEntry.tenant
    region = FormEntry.region
    site = FormEntry.site
    role = FormEntry.role
    manufacturer = FormEntry.manufacturer
    platform = FormEntry.platform
    device_type = FormEntry.device_type
    device = FormEntry.device
    dry_run = FormEntry.dry_run

    
    def token_exception_list(self, t):
        try:
            secret = Secret.objects.get(name="TOKEN_BYPASS")   # env variable for token exception
            token_exception_list = secret.get_value()
            if t.key in token_exception_list:
                return True
        except SecretError as exc:
            self.logger.warning(exc)
            self.logger.info("checking user tokens for admin user")
            if t.user.username in ["admin"]:
                return True
    
        

    def get_tokens(self):
        tokens = Token.objects.all()
        token_list = []
        is_valid = True
        ct = dt.datetime.now(dt.timezone.utc)
        for t in tokens:
            
            if t.is_expired:
                is_valid = False
                
            if t.expires is not None:
                if t.created.day < dt.datetime.now(dt.timezone.utc).day:
                    is_valid = False
                    
            if t.expires:
                if (t.expires - ct).total_seconds() > 86400:
                    is_valid = False
                    
            if not is_valid and not self.token_exception_list(t):
                token_list.append({"t_user": t.user.username, "t_created": t.created.strftime("%Y-%m-%d %H:%M:%S UTC"), "t_id": t.id, "t_is_expired": t.is_expired, "t_key": t.key })
                t.delete()
                
        return token_list

    def run(self, **data):
        resp = self.get_tokens()
        if len(resp) > 0:
            return (f"deleted objects: {resp}")
        else:
            return ("no objects found to delete")

register_jobs(ConfigScan)