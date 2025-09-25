#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Nautobot Job to trigger a GitHub Actions pipeline for fabric changes after user approval


import requests
import datetime
from nautobot.extras.jobs import Job, StringVar, ObjectVar, ChoiceVar
from nautobot.apps.jobs import register_jobs
# from nautobot.extras.choices import ObjectChangeActionChoices
from nautobot.ipam.models import IPAddress
from nautobot.dcim.models import Device, Location

class FabricChangePipelineJob(Job):
    class Meta:
        name = "Fabric Change Job"
        description = "Submit a fabric-related change request with approval"
        approval_required = True   # <-- this makes Nautobot require approval
        commit_default = False     # runs in "dry-run" until approval
        has_sensitive_variables = False

    # User Inputs
    # site = ObjectVar(
    #     model=Site,
    #     description="Select the site where the device lives",
    # )

    device = ObjectVar(
        model=Device,
        query_params={"site": "$site"},   # filters devices by selected site
        description="Select the device for the change",
    )

    core_zone = ChoiceVar(
        choices=(
            ("core", "Core"),
            ("aggregation", "Aggregation"),
            ("edge", "Edge"),
        ),
        description="Select the datacenter core/zone",
    )

    fabric_action = ChoiceVar(
        choices=(
            ("add_vlan", "Add VLAN"),
            ("remove_vlan", "Remove VLAN"),
            ("update_interface", "Update Interface"),
        ),
        description="Type of fabric-related change to perform",
    )

    fabric_details = StringVar(
        description="Details of the fabric change (e.g. VLAN ID, interface name, etc)."
    )

    def run(self, device, core_zone, fabric_action, fabric_details):
        """
        Executes after approval. Here you can add your real logic
        (API calls, config pushes, etc.)
        """
        self.log_info(f"Approved fabric change for device: {device.name}")
        # self.log_info(f"Site: {site.name}")
        self.log_info(f"Core/Zone: {core_zone}")
        self.log_info(f"Action: {fabric_action}")
        self.log_success(f"Details: {fabric_details}")

        # Example: Pretend to apply change
        if fabric_action == "add_vlan":
            self.log_success(f"Would add VLAN {fabric_details} to {device.name}")
        elif fabric_action == "remove_vlan":
            self.log_success(f"Would remove VLAN {fabric_details} from {device.name}")
        elif fabric_action == "update_interface":
            self.log_success(f"Would update interface {fabric_details} on {device.name}")

        return "Fabric change completed (simulated)."

register_jobs(FabricChangePipelineJob)