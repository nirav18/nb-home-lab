from nautobot.apps.jobs import JobHookReceiver, register_jobs
from nautobot.extras.choices import ObjectChangeActionChoices
from nautobot.ipam.models import IPAddress
from nautobot.dcim.models import Device
import logging
import socket

name="Primary IPv4 Address Change Receiver"


class PrimaryIPv4AddressChangeReceiver(JobHookReceiver):
    model = Device
    related_models = [IPAddress]
    

    class Meta:
        name = "Update DNS On Device IPv4 Change"
        description = "Update DNS records when a device's primary IPv4 address is changed."
        commit_default = False
        approval_required = False
        has_sensitive_variables = False
        worker_timeout = 300  # 5 minutes
        run_asynchronous = True
        
        
    def receive_job_hook(self, change, action, changed_object):
        # Skip deletes — we only care about IP address value updates
        # if action != ObjectChangeActionChoices.ACTION_CREATE and action != ObjectChangeActionChoices.ACTION_UPDATE:
        #     return
        
        if action == ObjectChangeActionChoices.ACTION_UPDATE:
            # log diff output
            snapshots = change.get_snapshots()
            # self.logger.info("DIFF: %s", snapshots['differences'])
            self.logger.info("Changed Object: %s", changed_object)
            
            if "primary_ip4" in snapshots["differences"]["added"] and isinstance(changed_object, Device):
                old_ip = snapshots["differences"]["removed"]["primary_ip4"]["address"] if "address" in snapshots["differences"]["removed"]["primary_ip4"] else None
                new_ip = snapshots["differences"]["added"]["primary_ip4"]["address"]
                old_dns_name = snapshots["differences"]["removed"]["primary_ip4"]["dns_name"] if "dns_name" in snapshots["differences"]["removed"]["primary_ip4"] else None
                new_dns_name = snapshots["differences"]["added"]["primary_ip4"]["dns_name"] if "dns_name" in snapshots["differences"]["added"]["primary_ip4"] else None
                if new_dns_name is None:
                    new_dns_name = self.validate_dns_record(new_ip.split("/")[0])
                    if new_dns_name:
                        ip_address_obj = IPAddress.objects.get(address=new_ip)
                        ip_address_obj.dns_name = new_dns_name
                        ip_address_obj.save()
                        self.logger.info("Updated DNS name for IP %s to %s", new_ip, new_dns_name)
                    else:
                        self.logger.info("No DNS record found for IP %s", new_ip)
                 # Log the change
                device = changed_object
                self.logger.info(
                    "Device %s primary_ip4 changed from %s → %s",
                    device.name, old_ip, new_ip
                )
                self.logger.info(
                    "Device %s dns_name changed from %s → %s",
                    device.name, old_dns_name, new_dns_name
                )

    
    def validate_dns_record(self, ip_address):
        """Return A records for a given IP using Python's socket module."""
    
        self.logger.info("getting A record for %s", ip_address)
        hostname = None
        try:
            # Step 1: Reverse lookup (PTR)
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            # logger.info("new dns_name is %s", hostname)
        except socket.herror:
            self.logger.error("DNS lookup failed for IP %s", ip_address) 
        except socket.gaierror:
            self.logger.error("DNS lookup failed for IP %s", ip_address)
        except Exception as e:
            self.logger.error("Error occurred while looking up DNS record for %s: %s", ip_address, e)
            
        return hostname
           
register_jobs(PrimaryIPv4AddressChangeReceiver)
