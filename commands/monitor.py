import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List
import os
import time
import datetime
from pathlib import Path

from cloudya.utils.system import check_cpu_usage, check_memory_usage, check_disk_usage, check_service_status, collect_service_metrics

app = typer.Typer(help="Surveiller les ressources et services")
console = Console()

@app.command()
def monitor(
    service: Optional[str] = typer.Option(None, "--service", "-s", help="Service à surveiller"),
    interval: int = typer.Option(5, "--interval", "-i", help="Intervalle de rafraîchissement en secondes"),
    count: Optional[int] = typer.Option(None, "--count", "-c", help="Nombre de mesures à effectuer"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Fichier de sortie pour les résultats")
):
    """
    Surveille les ressources système ou un service spécifique
    """
    if service:
        # Surveillance d'un service spécifique
        monitor_service(service, interval, count, output)
    else:
        # Surveillance générale du système
        monitor_system(interval, count, output)

def monitor_system(interval: int, count: Optional[int], output: Optional[str]):
    """
    Surveille les ressources générales du système
    """
    console.print("[bold]Surveillance des ressources système[/bold]")
    console.print(f"Intervalle: {interval} secondes")
    if count:
        console.print(f"Nombre de mesures: {count}")
    
    # Préparer le fichier de sortie si demandé
    output_file = None
    if output:
        output_file = open(output, "w")
        output_file.write("timestamp,cpu_usage,memory_usage,memory_used,memory_total,disk_usage,disk_used,disk_total\n")
    
    try:
        iterations = 0
        while True:
            # Collecter les métriques
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cpu_info = check_cpu_usage()
            memory_info = check_memory_usage()
            disk_info = check_disk_usage()
            
            # Afficher les résultats
            console.clear()
            console.print(f"[bold]Surveillance des ressources système[/bold] - {timestamp}")
            
            # CPU
            if cpu_info["usage"] < 70:
                console.print(f"[green]CPU: {cpu_info['usage']}%[/green]")
            elif cpu_info["usage"] < 90:
                console.print(f"[yellow]CPU: {cpu_info['usage']}%[/yellow]")
            else:
                console.print(f"[red]CPU: {cpu_info['usage']}%[/red]")
            
            # Mémoire
            if memory_info["usage"] < 70:
                console.print(f"[green]Mémoire: {memory_info['usage']}% ({memory_info['used']}/{memory_info['total']})[/green]")
            elif memory_info["usage"] < 90:
                console.print(f"[yellow]Mémoire: {memory_info['usage']}% ({memory_info['used']}/{memory_info['total']})[/yellow]")
            else:
                console.print(f"[red]Mémoire: {memory_info['usage']}% ({memory_info['used']}/{memory_info['total']})[/red]")
            
            # Disque
            if disk_info["usage"] < 70:
                console.print(f"[green]Disque: {disk_info['usage']}% ({disk_info['used']}/{disk_info['total']})[/green]")
            elif disk_info["usage"] < 90:
                console.print(f"[yellow]Disque: {disk_info['usage']}% ({disk_info['used']}/{disk_info['total']})[/yellow]")
            else:
                console.print(f"[red]Disque: {disk_info['usage']}% ({disk_info['used']}/{disk_info['total']})[/red]")
            
            # Enregistrer dans le fichier de sortie si demandé
            if output_file:
                output_file.write(f"{timestamp},{cpu_info['usage']},{memory_info['usage']},{memory_info['used']},{memory_info['total']},{disk_info['usage']},{disk_info['used']},{disk_info['total']}\n")
                output_file.flush()
            
            # Incrémenter le compteur
            iterations += 1
            
            # Afficher le compteur si limité
            if count:
                console.print(f"Mesure {iterations}/{count}")
                # Vérifier si on a atteint le nombre de mesures demandé
                if iterations >= count:
                    break
            else:
                console.print("Appuyez sur Ctrl+C pour arrêter...")
            
            # Attendre l'intervalle
            time.sleep(interval)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Surveillance interrompue par l'utilisateur.[/yellow]")
    finally:
        if output_file:
            output_file.close()
            console.print(f"[green]Résultats enregistrés dans le fichier: {output}[/green]")

def monitor_service(service: str, interval: int, count: Optional[int], output: Optional[str]):
    """
    Surveille un service spécifique
    """
    console.print(f"[bold]Surveillance du service: [cyan]{service}[/cyan][/bold]")
    console.print(f"Intervalle: {interval} secondes")
    if count:
        console.print(f"Nombre de mesures: {count}")
    
    # Vérifier si le service existe
    initial_status = check_service_status(service)
    if not initial_status["exists"]:
        console.print(f"[red]Le service {service} n'existe pas.[/red]")
        return
    
    # Préparer le fichier de sortie si demandé
    output_file = None
    if output:
        output_file = open(output, "w")
        output_file.write("timestamp,status,cpu_usage,memory_usage,connections,requests_per_second\n")
    
    try:
        iterations = 0
        while True:
            # Collecter les métriques
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = check_service_status(service)
            metrics = collect_service_metrics(service)
            
            # Afficher les résultats
            console.clear()
            console.print(f"[bold]Surveillance du service: [cyan]{service}[/cyan] - {timestamp}[/bold]")
            
            # État du service
            if status["running"]:
                console.print(f"[green]État: En cours d'exécution[/green]")
            else:
                console.print(f"[red]État: Arrêté[/red]")
            
            # Métriques spécifiques au service
            if metrics:
                if "cpu_usage" in metrics:
                    if metrics["cpu_usage"] < 50:
                        console.print(f"[green]CPU: {metrics['cpu_usage']}%[/green]")
                    elif metrics["cpu_usage"] < 80:
                        console.print(f"[yellow]CPU: {metrics['cpu_usage']}%[/yellow]")
                    else:
                        console.print(f"[red]CPU: {metrics['cpu_usage']}%[/red]")
                
                if "memory_usage" in metrics:
                    if metrics["memory_usage"] < 50:
                        console.print(f"[green]Mémoire: {metrics['memory_usage']}MB[/green]")
                    elif metrics["memory_usage"] < 80:
                        console.print(f"[yellow]Mémoire: {metrics['memory_usage']}MB[/yellow]")
                    else:
                        console.print(f"[red]Mémoire: {metrics['memory_usage']}MB[/red]")
                
                if "connections" in metrics:
                    console.print(f"Connexions: {metrics['connections']}")
                
                if "requests_per_second" in metrics:
                    console.print(f"Requêtes/sec: {metrics['requests_per_second']}")
            
            # Enregistrer dans le fichier de sortie si demandé
            if output_file:
                status_value = "running" if status["running"] else "stopped"
                cpu = metrics.get("cpu_usage", "N/A")
                mem = metrics.get("memory_usage", "N/A")
                conn = metrics.get("connections", "N/A")
                rps = metrics.get("requests_per_second", "N/A")
                output_file.write(f"{timestamp},{status_value},{cpu},{mem},{conn},{rps}\n")
                output_file.flush()
            
            # Incrémenter le compteur
            iterations += 1
            
            # Afficher le compteur si limité
            if count:
                console.print(f"Mesure {iterations}/{count}")
                # Vérifier si on a atteint le nombre de mesures demandé
                if iterations >= count:
                    break
            else:
                console.print("Appuyez sur Ctrl+C pour arrêter...")
            
            # Attendre l'intervalle
            time.sleep(interval)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Surveillance interrompue par l'utilisateur.[/yellow]")
    finally:
        if output_file:
            output_file.close()
            console.print(f"[green]Résultats enregistrés dans le fichier: {output}[/green]")

@app.command("report")
def generate_report(
    days: int = typer.Option(7, "--days", "-d", help="Nombre de jours à inclure dans le rapport"),
    service: Optional[str] = typer.Option(None, "--service", "-s", help="Service à inclure dans le rapport"),
    output: str = typer.Option("cloudya_report.html", "--output", "-o", help="Fichier de sortie pour le rapport")
):
    """
    Génère un rapport de performance du système ou d'un service
    """
    console.print(f"[bold]Génération d'un rapport pour les {days} derniers jours...[/bold]")
    
    # Collecter les données
    with console.status("Collecte des données de performance..."):
        # Ici, nous simulons la collecte de données
        # Dans une implémentation réelle, vous collecteriez les données à partir de fichiers de logs, etc.
        
        # Données système
        system_data = {
            "cpu": [{"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), "value": 50 + (i % 20)} for i in range(days)],
            "memory": [{"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), "value": 60 + (i % 15)} for i in range(days)],
            "disk": [{"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), "value": 70 + (i % 5)} for i in range(days)]
        }
        
        # Données du service (si demandé)
        service_data = None
        if service:
            service_data = {
                "cpu": [{"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), "value": 30 + (i % 25)} for i in range(days)],
                "memory": [{"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), "value": 40 + (i % 20)} for i in range(days)],
                "connections": [{"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), "value": 100 + (i % 50)} for i in range(days)]
            }
    
    # Générer le rapport HTML
    with console.status("Génération du rapport HTML..."):
        # Créer un rapport HTML simple
        html_content = generate_html_report(system_data, service_data, service, days)
        
        # Enregistrer le rapport
        with open(output, "w") as f:
            f.write(html_content)
    
    console.print(f"[green]Rapport généré avec succès: {output}[/green]")
    console.print("Vous pouvez ouvrir ce fichier dans votre navigateur pour visualiser le rapport.")

def generate_html_report(system_data, service_data, service_name, days):
    """
    Génère un rapport HTML basique
    """
    # Cette fonction est simplifiée, dans une implémentation réelle,
    # vous utiliseriez probablement une bibliothèque de templates comme Jinja2
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cloudya - Rapport de performance</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            .section {{ margin-top: 20px; }}
            .metric {{ margin-bottom: 15px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>Cloudya - Rapport de performance</h1>
        <p>Rapport généré le {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Période: {days} jours</p>
        
        <div class="section">
            <h2>Performance système</h2>
            
            <div class="metric">
                <h3>Utilisation CPU</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Utilisation (%)</th>
                    </tr>
    """
    
    # Ajouter les données CPU
    for entry in reversed(system_data["cpu"]):
        html += f"""
                    <tr>
                        <td>{entry['date']}</td>
                        <td>{entry['value']}%</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
            
            <div class="metric">
                <h3>Utilisation mémoire</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Utilisation (%)</th>
                    </tr>
    """
    
    # Ajouter les données mémoire
    for entry in reversed(system_data["memory"]):
        html += f"""
                    <tr>
                        <td>{entry['date']}</td>
                        <td>{entry['value']}%</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
            
            <div class="metric">
                <h3>Utilisation disque</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Utilisation (%)</th>
                    </tr>
    """
    
    # Ajouter les données disque
    for entry in reversed(system_data["disk"]):
        html += f"""
                    <tr>
                        <td>{entry['date']}</td>
                        <td>{entry['value']}%</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
        </div>
    """
    
    # Ajouter les données du service si demandé
    if service_data and service_name:
        html += f"""
        <div class="section">
            <h2>Performance du service: {service_name}</h2>
            
            <div class="metric">
                <h3>Utilisation CPU</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Utilisation (%)</th>
                    </tr>
        """
        
        # Ajouter les données CPU du service
        for entry in reversed(service_data["cpu"]):
            html += f"""
                        <tr>
                            <td>{entry['date']}</td>
                            <td>{entry['value']}%</td>
                        </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="metric">
                <h3>Utilisation mémoire</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Utilisation (%)</th>
                    </tr>
        """
        
        # Ajouter les données mémoire du service
        for entry in reversed(service_data["memory"]):
            html += f"""
                        <tr>
                            <td>{entry['date']}</td>
                            <td>{entry['value']}%</td>
                        </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="metric">
                <h3>Connexions</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Nombre</th>
                    </tr>
        """
        
        # Ajouter les données de connexions du service
        for entry in reversed(service_data["connections"]):
            html += f"""
                        <tr>
                            <td>{entry['date']}</td>
                            <td>{entry['value']}</td>
                        </tr>
            """
        
        html += """
                </table>
            </div>
        </div>
        """
    
    # Finaliser le HTML
    html += """
    </body>
    </html>
    """
    
    return html

if __name__ == "__main__":
    app()
