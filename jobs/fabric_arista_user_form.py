#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Nautobot Job to trigger a GitHub Actions pipeline for fabric changes after user approval


import requests
import datetime
from nautobot.extras.jobs import Job, StringVar, ObjectVar, ChoiceVar
from nautobot.dcim.models import Site, Device

class FabricChangePipelineJob(Job):
    class Meta:
        name = "Fabric Change Pipeline Trigger"
        description = "Collects user input, requires approval, then triggers GitHub pipeline"
        approval_required = True
        commit_default = False

    site = ObjectVar(model=Site, description="Select the site where the device lives")
    device = ObjectVar(model=Device, query_params={"site": "$site"}, description="Select the device")
    core_zone = ChoiceVar(choices=(("core","Core"),("aggregation","Aggregation"),("edge","Edge")), description="Datacenter core/zone")
    fabric_action = ChoiceVar(choices=(("add_vlan","Add VLAN"),("remove_vlan","Remove VLAN"),("update_interface","Update Interface")), description="Fabric action")
    fabric_details = StringVar(description="Details (e.g. VLAN ID, interface name)")

    def run(self, site, device, core_zone, fabric_action, fabric_details):
        branch_name = f"fabric-change-{device.name}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        payload = {
            "branch_name": branch_name,
            "site": site.name,
            "device": device.name,
            "core_zone": core_zone,
            "action": fabric_action,
            "details": fabric_details,
        }

        webhook_url = "https://api.github.com/repos/<org>/<repo>/dispatches"
        
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer <GITHUB_TOKEN>",  # use Nautobot Secrets in prod
        }
        data = {"event_type": "nautobot-fabric-change", "client_payload": payload}

        self.log_info(f"Triggering GitHub pipeline for branch {branch_name}...")
        response = requests.post(webhook_url, headers=headers, json=data)

        if response.status_code in [200,201,204]:
            self.log_success(f"Pipeline triggered. Branch to be created: {branch_name}")
        else:
            self.log_failure(f"GitHub webhook failed: {response.status_code} {response.text}")
