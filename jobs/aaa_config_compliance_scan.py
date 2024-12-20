import datetime as dt


from nautobot.apps.jobs import Job, register_jobs
# from nautobot.core.celery import register_jobs
# from nautobot.apps.jobs import Job, register_jobs
from nautobot.users.models import Token
from nautobot.extras.models.secrets import Secret
from nautobot.extras.secrets.exceptions import SecretError
from nautobot.apps.jobs import StringVar, IntegerVar, ObjectVar, MultiObjectVar, BooleanVar  
from nautobot.dcim.models import Device

from nautobot.tenancy.models import Tenant, TenantGroup


name = "AAA Config Policy Job"



class ConfigScan(Job):

    """
        AAA Config Policy Job
    """

    class Meta:
        " Metadata needed to implement the backbone site design. "

        name = "AAA Config Policy"
        commit_default = False
        has_sensitive_variables = False
    
    device = MultiObjectVar(model=Device, required=True)
   
    
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

    def run(self, device):
        self.logger.info(device)
        
        resp = self.get_tokens()
        if len(resp) > 0:
            return (f"deleted objects: {resp}")
        else:
            return ("no objects found to delete")

register_jobs(ConfigScan)