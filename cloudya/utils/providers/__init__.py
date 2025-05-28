"""
Package d'initialisation pour les modules de fournisseurs cloud
"""
from . import aws
from . import gcp
from . import azure
from . import openstack
from . import proxmox
from . import vmware
from . import nutanix

__all__ = [
    'aws',
    'gcp',
    'azure',
    'openstack',
    'proxmox',
    'vmware',
    'nutanix'
]
