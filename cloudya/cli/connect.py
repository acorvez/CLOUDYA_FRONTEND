#!/usr/bin/env python3
import typer
import os
import sys
from rich.console import Console
from pathlib import Path
from typing import Optional

# Import des modules de connexion pour chaque fournisseur
from cloudya.utils.providers import (
    aws,
    gcp,
    azure,
    openstack,
    proxmox,
    vmware,
    nutanix
)

app = typer.Typer(help="Se connecter aux infrastructures cloud et hyperviseurs")
console = Console()

@app.command("aws")
def connect_aws(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profil AWS à utiliser"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="Région AWS")
):
    """Se connecte à AWS Cloud"""
    aws.connect(profile, region)

@app.command("gcp")
def connect_gcp(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Projet GCP à utiliser"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Chemin vers le fichier de configuration GCP")
):
    """Se connecte à Google Cloud Platform"""
    gcp.connect(project, config_file)

@app.command("azure")
def connect_azure(
    subscription: Optional[str] = typer.Option(None, "--subscription", "-s", help="Abonnement Azure à utiliser")
):
    """Se connecte à Microsoft Azure"""
    azure.connect(subscription)

@app.command("openstack")
def connect_openstack(
    auth_url: Optional[str] = typer.Option(None, "--auth-url", help="URL d'authentification OpenStack"),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Nom d'utilisateur OpenStack"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Mot de passe OpenStack"),
    project_name: Optional[str] = typer.Option(None, "--project", help="Nom du projet OpenStack"),
    cloud_name: Optional[str] = typer.Option(None, "--cloud", "-c", help="Nom du cloud dans clouds.yaml")
):
    """Se connecte à OpenStack"""
    openstack.connect(auth_url, username, password, project_name, cloud_name)

@app.command("proxmox")
def connect_proxmox(
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Hôte Proxmox (ex: proxmox.example.com)"),
    port: Optional[int] = typer.Option(8006, "--port", "-p", help="Port de l'API Proxmox"),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Nom d'utilisateur Proxmox (ex: root@pam)"),
    token_name: Optional[str] = typer.Option(None, "--token-name", help="Nom du token d'API Proxmox"),
    token_value: Optional[str] = typer.Option(None, "--token-value", help="Valeur du token d'API Proxmox")
):
    """Se connecte à Proxmox VE"""
    proxmox.connect(host, port, username, token_name, token_value)

@app.command("vmware")
def connect_vmware(
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Hôte vCenter ou ESXi (ex: vcenter.example.com)"),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Nom d'utilisateur VMware"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Mot de passe VMware"),
    port: Optional[int] = typer.Option(443, "--port", help="Port du serveur vCenter ou ESXi")
):
    """Se connecte à VMware vSphere (vCenter ou ESXi)"""
    vmware.connect(host, username, password, port)

@app.command("nutanix")
def connect_nutanix(
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Hôte Nutanix Prism Central (ex: prism.example.com)"),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Nom d'utilisateur Nutanix"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Mot de passe Nutanix"),
    port: Optional[int] = typer.Option(9440, "--port", help="Port du serveur Nutanix Prism Central")
):
    """Se connecte à Nutanix Prism Central"""
    nutanix.connect(host, username, password, port)

if __name__ == "__main__":
    app()
