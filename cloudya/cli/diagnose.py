import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List
import os
import subprocess
import shutil
import datetime
from pathlib import Path

from cloudya.utils.system import collect_logs, check_service_status, check_cpu_usage, check_memory_usage, check_disk_usage

app = typer.Typer(help="Diagnostiquer les problèmes d'infrastructure")
console = Console()

@app.command()
def diagnose(
    service: Optional[str] = typer.Option(None, "--service", "-s", help="Service à diagnostiquer"),
    logs: bool = typer.Option(False, "--logs", "-l", help="Collecter les logs du service"),
    days: int = typer.Option(1, "--days", "-d", help="Nombre de jours de logs à collecter"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Afficher les informations détaillées"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Fichier de sortie pour les résultats")
):
    """
    Diagnostique les problèmes d'infrastructure et de services
    """
    if service:
        # Diagnostic d'un service spécifique
        console.print(f"[bold]Diagnostic du service: [cyan]{service}[/cyan][/bold]")
        
        # Vérifier l'état du service
        with console.status(f"Vérification de l'état du service {service}..."):
            status = check_service_status(service)
        
        # Afficher l'état
        if status["running"]:
            console.print(f"[green]✓ Service {service} en cours d'exécution[/green]")
        else:
            console.print(f"[red]✗ Service {service} arrêté ou non trouvé[/red]")
            if status.get("error"):
                console.print(f"  Erreur: {status['error']}")
        
        # Afficher les informations supplémentaires
        if "version" in status:
            console.print(f"Version: {status['version']}")
        if "uptime" in status:
            console.print(f"Uptime: {status['uptime']}")
        
        # Collecter et afficher les logs si demandé
        if logs:
            with console.status(f"Collecte des logs du service {service}..."):
                log_entries = collect_logs(service, days)
            
            if log_entries:
                console.print(f"\n[bold]Logs récents du service [cyan]{service}[/cyan] ({len(log_entries)} entrées):[/bold]")
                
                # Limiter le nombre de logs affichés par défaut
                display_logs = log_entries
                if not verbose and len(log_entries) > 10:
                    display_logs = log_entries[-10:]  # Afficher uniquement les 10 derniers logs
                    console.print(f"[yellow]Affichage des 10 derniers logs (sur {len(log_entries)}). Utilisez --verbose pour voir tous les logs.[/yellow]")
                
                for log in display_logs:
                    # Colorer les logs selon leur niveau
                    if "level" in log:
                        if log["level"].lower() in ["error", "critical", "fatal"]:
                            color = "red"
                        elif log["level"].lower() in ["warning", "warn"]:
                            color = "yellow"
                        else:
                            color = "white"
                    else:
                        color = "white"
                    
                    # Formater et afficher le log
                    timestamp = log.get("timestamp", "")
                    level = log.get("level", "").upper()
                    message = log.get("message", "")
                    
                    console.print(f"[dim]{timestamp}[/dim] [{color}]{level}[/{color}]: {message}")
                
                # Enregistrer les logs dans un fichier si demandé
                if output:
                    with open(output, "w") as f:
                        for log in log_entries:
                            timestamp = log.get("timestamp", "")
                            level = log.get("level", "").upper()
                            message = log.get("message", "")
                            f.write(f"{timestamp} {level}: {message}\n")
                    
                    console.print(f"\n[green]Logs enregistrés dans le fichier: {output}[/green]")
            else:
                console.print(f"[yellow]Aucun log trouvé pour le service {service}.[/yellow]")
        
        # Analyse basique (sans IA pour le moment)
        console.print("\n[bold]Analyse basique:[/bold]")
        if not status["running"]:
            console.print("[red]✗ Le service n'est pas en cours d'exécution.[/red]")
            console.print("  Suggestions:")
            console.print("  - Vérifiez que le service est installé correctement")
            console.print("  - Essayez de démarrer le service manuellement")
            console.print(f"  - Consultez les logs pour plus de détails: sudo journalctl -u {service}")
        else:
            # Recherche simple de mots clés d'erreur dans les logs
            if logs and log_entries:
                error_count = sum(1 for log in log_entries if log.get("level", "").lower() in ["error", "critical", "fatal"])
                warning_count = sum(1 for log in log_entries if log.get("level", "").lower() in ["warning", "warn"])
                
                if error_count > 0:
                    console.print(f"[red]✗ {error_count} erreurs trouvées dans les logs.[/red]")
                if warning_count > 0:
                    console.print(f"[yellow]! {warning_count} avertissements trouvés dans les logs.[/yellow]")
                
                if error_count == 0 and warning_count == 0:
                    console.print("[green]✓ Aucune erreur ou avertissement trouvé dans les logs.[/green]")
            else:
                console.print("[green]✓ Le service est en cours d'exécution.[/green]")
    else:
        # Diagnostic général du système
        console.print("[bold]Diagnostic général du système[/bold]")
        
        # Vérifier les ressources système
        with console.status("Vérification des ressources système..."):
            # Ces fonctions seraient implémentées dans utils/system.py
            cpu_info = check_cpu_usage()
            memory_info = check_memory_usage()
            disk_info = check_disk_usage()
            
        # Afficher les informations sur les ressources
        console.print("\n[bold]Ressources système:[/bold]")
        
        # CPU
        if cpu_info["usage"] < 70:
            console.print(f"[green]✓ CPU: {cpu_info['usage']}% utilisé[/green]")
        elif cpu_info["usage"] < 90:
            console.print(f"[yellow]! CPU: {cpu_info['usage']}% utilisé[/yellow]")
        else:
            console.print(f"[red]✗ CPU: {cpu_info['usage']}% utilisé[/red]")
        
        # Mémoire
        if memory_info["usage"] < 70:
            console.print(f"[green]✓ Mémoire: {memory_info['usage']}% utilisé ({memory_info['used']}/{memory_info['total']})[/green]")
        elif memory_info["usage"] < 90:
            console.print(f"[yellow]! Mémoire: {memory_info['usage']}% utilisé ({memory_info['used']}/{memory_info['total']})[/yellow]")
        else:
            console.print(f"[red]✗ Mémoire: {memory_info['usage']}% utilisé ({memory_info['used']}/{memory_info['total']})[/red]")
        
        # Disque
        if disk_info["usage"] < 70:
            console.print(f"[green]✓ Disque: {disk_info['usage']}% utilisé ({disk_info['used']}/{disk_info['total']})[/green]")
        elif disk_info["usage"] < 90:
            console.print(f"[yellow]! Disque: {disk_info['usage']}% utilisé ({disk_info['used']}/{disk_info['total']})[/yellow]")
        else:
            console.print(f"[red]✗ Disque: {disk_info['usage']}% utilisé ({disk_info['used']}/{disk_info['total']})[/red]")
        
        # Vérifier les services importants
        with console.status("Vérification des services importants..."):
            services = ["sshd", "nginx", "docker"]  # Exemple de services à vérifier
            service_statuses = {service: check_service_status(service) for service in services}
        
        console.print("\n[bold]Services importants:[/bold]")
        for service, status in service_statuses.items():
            if status["running"]:
                console.print(f"[green]✓ {service}: En cours d'exécution[/green]")
            else:
                console.print(f"[red]✗ {service}: Arrêté ou non trouvé[/red]")

@app.command("local")
def local_diagnose(
    service: str = typer.Option(..., "--service", "-s", help="Service local à diagnostiquer"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Tenter de résoudre les problèmes automatiquement")
):
    """
    Effectue un diagnostic local d'un service sans utiliser l'IA
    """
    console.print(f"[bold]Diagnostic local du service: [cyan]{service}[/cyan][/bold]")
    
    # Vérifier si le service existe
    with console.status(f"Vérification du service {service}..."):
        exists = os.path.exists(f"/etc/systemd/system/{service}.service") or os.path.exists(f"/lib/systemd/system/{service}.service")
    
    if not exists:
        console.print(f"[red]✗ Le service {service} n'existe pas.[/red]")
        return
    
    # Vérifier l'état du service
    with console.status(f"Vérification de l'état du service {service}..."):
        status = check_service_status(service)
    
    # Afficher les résultats
    if status["running"]:
        console.print(f"[green]✓ Service {service} en cours d'exécution[/green]")
    else:
        console.print(f"[red]✗ Service {service} arrêté[/red]")
        
        # Tenter de résoudre le problème si demandé
        if fix:
            console.print("Tentative de démarrage du service...")
            try:
                result = subprocess.run(["sudo", "systemctl", "start", service], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print(f"[green]✓ Service {service} démarré avec succès![/green]")
                else:
                    console.print(f"[red]✗ Échec du démarrage du service: {result.stderr}[/red]")
            except Exception as e:
                console.print(f"[red]✗ Erreur lors du démarrage du service: {str(e)}[/red]")

if __name__ == "__main__":
    app()
