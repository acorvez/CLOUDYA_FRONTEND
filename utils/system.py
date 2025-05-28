import os
import psutil
import subprocess
import re
import json
import datetime
import platform
import socket
from pathlib import Path
import logging

def check_cpu_usage():
    """
    Vérifie l'utilisation du CPU
    """
    try:
        usage = psutil.cpu_percent(interval=1)
        
        return {
            "usage": usage,
            "count": psutil.cpu_count(),
            "count_logical": psutil.cpu_count(logical=True)
        }
    except Exception as e:
        logging.error(f"Erreur lors de la vérification du CPU: {str(e)}")
        return {"usage": 0, "error": str(e)}

def check_memory_usage():
    """
    Vérifie l'utilisation de la mémoire
    """
    try:
        memory = psutil.virtual_memory()
        
        # Convertir les bytes en formats plus lisibles
        total_gb = memory.total / (1024 ** 3)
        used_gb = memory.used / (1024 ** 3)
        
        return {
            "usage": memory.percent,
            "total": f"{total_gb:.2f}GB",
            "used": f"{used_gb:.2f}GB",
            "available": f"{(memory.available / 1024 ** 3):.2f}GB"
        }
    except Exception as e:
        logging.error(f"Erreur lors de la vérification de la mémoire: {str(e)}")
        return {"usage": 0, "error": str(e)}

def check_disk_usage(path="/"):
    """
    Vérifie l'utilisation du disque
    """
    try:
        disk = psutil.disk_usage(path)
        
        # Convertir les bytes en formats plus lisibles
        total_gb = disk.total / (1024 ** 3)
        used_gb = disk.used / (1024 ** 3)
        
        return {
            "usage": disk.percent,
            "total": f"{total_gb:.2f}GB",
            "used": f"{used_gb:.2f}GB",
            "free": f"{(disk.free / 1024 ** 3):.2f}GB",
            "path": path
        }
    except Exception as e:
        logging.error(f"Erreur lors de la vérification du disque: {str(e)}")
        return {"usage": 0, "error": str(e)}

def check_service_status(service_name):
    """
    Vérifie l'état d'un service
    """
    result = {
        "name": service_name,
        "exists": False,
        "running": False
    }
    
    # Détecter le système d'exploitation
    os_type = platform.system()
    
    try:
        if os_type == "Linux":
            # Vérifier avec systemctl
            try:
                # Vérifier si le service existe
                proc = subprocess.run(
                    ["systemctl", "list-unit-files", f"{service_name}.service"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                result["exists"] = f"{service_name}.service" in proc.stdout
                
                if result["exists"]:
                    # Vérifier si le service est en cours d'exécution
                    proc = subprocess.run(
                        ["systemctl", "is-active", service_name],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    result["running"] = proc.stdout.strip() == "active"
                    
                    # Obtenir des informations supplémentaires
                    proc = subprocess.run(
                        ["systemctl", "status", service_name],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    status_output = proc.stdout
                    
                    # Extraire la version si disponible
                    version_match = re.search(r"version\s+(\S+)", status_output, re.IGNORECASE)
                    if version_match:
                        result["version"] = version_match.group(1)
                    
                    # Extraire le uptime si disponible
                    uptime_match = re.search(r"Active:\s+active\s+\(.*?\)\s+since\s+(.*?);", status_output)
                    if uptime_match:
                        result["uptime"] = uptime_match.group(1)
            
            except Exception as e:
                result["error"] = f"Erreur systemctl: {str(e)}"
        
        elif os_type == "Darwin":  # macOS
            # Vérifier avec launchctl
            try:
                proc = subprocess.run(
                    ["launchctl", "list"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                result["exists"] = service_name in proc.stdout
                result["running"] = service_name in proc.stdout and "-" not in proc.stdout.split(service_name)[1].split()[0]
            
            except Exception as e:
                result["error"] = f"Erreur launchctl: {str(e)}"
        
        elif os_type == "Windows":
            # Vérifier avec sc
            try:
                proc = subprocess.run(
                    ["sc", "query", service_name],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                result["exists"] = "SERVICE_NAME" in proc.stdout
                result["running"] = "RUNNING" in proc.stdout
            
            except Exception as e:
                result["error"] = f"Erreur sc: {str(e)}"
        
        # Si le service n'est pas un service système, vérifier les processus
        if not result["exists"]:
            for proc in psutil.process_iter(['pid', 'name']):
                if service_name.lower() in proc.info['name'].lower():
                    result["exists"] = True
                    result["running"] = True
                    result["process_name"] = proc.info['name']
                    result["pid"] = proc.info['pid']
                    break
        
        # Vérification spécifique pour Docker
        if service_name == "docker" or service_name == "docker.service":
            try:
                docker_proc = subprocess.run(
                    ["docker", "version"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if docker_proc.returncode == 0:
                    result["exists"] = True
                    result["running"] = True
                    
                    # Extraire la version
                    version_match = re.search(r"Version:\s+(\S+)", docker_proc.stdout)
                    if version_match:
                        result["version"] = version_match.group(1)
            except Exception:
                pass
        
        # Vérification spécifique pour Nginx
        elif service_name == "nginx" or service_name == "nginx.service":
            try:
                nginx_proc = subprocess.run(
                    ["nginx", "-v"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if nginx_proc.returncode == 0 or "nginx version" in nginx_proc.stderr:
                    result["exists"] = True
                    
                    # Vérifier si Nginx est en cours d'exécution
                    ps_proc = subprocess.run(
                        ["ps", "aux"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    result["running"] = "nginx" in ps_proc.stdout
                    
                    # Extraire la version
                    version_match = re.search(r"nginx version: nginx/(\S+)", nginx_proc.stderr)
                    if version_match:
                        result["version"] = version_match.group(1)
            except Exception:
                pass
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def collect_logs(service_name, days=1):
    """
    Collecte les logs d'un service
    """
    logs = []
    
    # Détecter le système d'exploitation
    os_type = platform.system()
    
    try:
        if os_type == "Linux":
            # Utiliser journalctl pour les services systemd
            since_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            
            try:
                proc = subprocess.run(
                    ["journalctl", "-u", service_name, "--since", since_date, "--no-pager"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                log_lines = proc.stdout.splitlines()
                
                for line in log_lines:
                    # Parse les logs journalctl (format: "Mai 14 12:34:56 hostname service[123]: message")
                    match = re.match(r"(\w+\s+\d+\s+\d+:\d+:\d+)\s+\S+\s+[^:]+:\s+(.*)", line)
                    if match:
                        timestamp, message = match.groups()
                        
                        # Déterminer le niveau de log
                        level = "INFO"
                        if re.search(r"\b(error|fail|failed|critical|emergency)\b", message, re.IGNORECASE):
                            level = "ERROR"
                        elif re.search(r"\b(warn|warning)\b", message, re.IGNORECASE):
                            level = "WARNING"
                        
                        logs.append({
                            "timestamp": timestamp,
                            "level": level,
                            "message": message
                        })
            
            except Exception as e:
                logging.error(f"Erreur lors de la collecte des logs journalctl: {str(e)}")
            
            # Si aucun log n'est trouvé avec journalctl, essayer les fichiers de log
            if not logs:
                log_paths = [
                    f"/var/log/{service_name}",
                    f"/var/log/{service_name}.log",
                    f"/var/log/syslog"
                ]
                
                for log_path in log_paths:
                    if os.path.exists(log_path):
                        try:
                            # Lire le fichier de log
                            with open(log_path, 'r') as f:
                                log_content = f.readlines()
                            
                            # Filtrer les logs par date et service
                            for line in log_content:
                                # Parse les logs (format variable)
                                if service_name in line:
                                    # Extraire la date si possible
                                    date_match = re.match(r"(\d{4}-\d{2}-\d{2}|\w+\s+\d+)\s+(\d+:\d+:\d+)\s+", line)
                                    if date_match:
                                        timestamp = f"{date_match.group(1)} {date_match.group(2)}"
                                        message = line[len(date_match.group(0)):].strip()
                                    else:
                                        timestamp = "Unknown"
                                        message = line.strip()
                                    
                                    # Déterminer le niveau de log
                                    level = "INFO"
                                    if re.search(r"\b(error|fail|failed|critical|emergency)\b", message, re.IGNORECASE):
                                        level = "ERROR"
                                    elif re.search(r"\b(warn|warning)\b", message, re.IGNORECASE):
                                        level = "WARNING"
                                    
                                    logs.append({
                                        "timestamp": timestamp,
                                        "level": level,
                                        "message": message
                                    })
                        
                        except Exception as e:
                            logging.error(f"Erreur lors de la lecture du fichier de log {log_path}: {str(e)}")
        
        elif os_type == "Darwin":  # macOS
            # macOS utilise des fichiers de log dans /var/log
            log_paths = [
                f"/var/log/{service_name}.log",
                "/var/log/system.log"
            ]
            
            for log_path in log_paths:
                if os.path.exists(log_path):
                    try:
                        # Lire le fichier de log
                        with open(log_path, 'r') as f:
                            log_content = f.readlines()
                        
                        # Filtrer les logs par service
                        for line in log_content:
                            if service_name in line:
                                # Parse les logs (format: "May 14 12:34:56 hostname service[123]: message")
                                date_match = re.match(r"(\w+\s+\d+\s+\d+:\d+:\d+)\s+", line)
                                if date_match:
                                    timestamp = date_match.group(1)
                                    message = line[len(date_match.group(0)):].strip()
                                else:
                                    timestamp = "Unknown"
                                    message = line.strip()
                                
                                # Déterminer le niveau de log
                                level = "INFO"
                                if re.search(r"\b(error|fail|failed|critical|emergency)\b", message, re.IGNORECASE):
                                    level = "ERROR"
                                elif re.search(r"\b(warn|warning)\b", message, re.IGNORECASE):
                                    level = "WARNING"
                                
                                logs.append({
                                    "timestamp": timestamp,
                                    "level": level,
                                    "message": message
                                })
                    
                    except Exception as e:
                        logging.error(f"Erreur lors de la lecture du fichier de log {log_path}: {str(e)}")
        
        elif os_type == "Windows":
            # Windows utilise l'Event Log
            try:
                # Utiliser PowerShell pour récupérer les logs
                cmd = f"powershell -Command \"Get-EventLog -LogName Application -Source '{service_name}' -After (Get-Date).AddDays(-{days}) | Select-Object TimeGenerated, EntryType, Message | ConvertTo-Json\""
                
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    shell=True,
                    check=False
                )
                
                if proc.returncode == 0 and proc.stdout.strip():
                    try:
                        events = json.loads(proc.stdout)
                        
                        # Si un seul événement est retourné, le convertir en liste
                        if not isinstance(events, list):
                            events = [events]
                        
                        for event in events:
                            level = event.get("EntryType", "Information").upper()
                            if level == "INFORMATION":
                                level = "INFO"
                            elif level == "WARNING":
                                level = "WARNING"
                            elif level in ["ERROR", "CRITICAL", "FAILURE"]:
                                level = "ERROR"
                            
                            logs.append({
                                "timestamp": event.get("TimeGenerated", "Unknown"),
                                "level": level,
                                "message": event.get("Message", "")
                            })
                    
                    except json.JSONDecodeError:
                        pass
            
            except Exception as e:
                logging.error(f"Erreur lors de la récupération des logs Windows: {str(e)}")
        
        # Si aucun log n'est trouvé, collecter les logs généraux du système
        if not logs:
            if os_type == "Linux":
                try:
                    # Essayer de collecter les logs de syslog
                    proc = subprocess.run(
                        ["grep", service_name, "/var/log/syslog"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if proc.returncode == 0:
                        for line in proc.stdout.splitlines():
                            # Parse les logs syslog
                            date_match = re.match(r"(\w+\s+\d+\s+\d+:\d+:\d+)\s+", line)
                            if date_match:
                                timestamp = date_match.group(1)
                                message = line[len(date_match.group(0)):].strip()
                            else:
                                timestamp = "Unknown"
                                message = line.strip()
                            
                            level = "INFO"
                            if re.search(r"\b(error|fail|failed|critical|emergency)\b", message, re.IGNORECASE):
                                level = "ERROR"
                            elif re.search(r"\b(warn|warning)\b", message, re.IGNORECASE):
                                level = "WARNING"
                            
                            logs.append({
                                "timestamp": timestamp,
                                "level": level,
                                "message": message
                            })
                
                except Exception as e:
                    logging.error(f"Erreur lors de la recherche dans syslog: {str(e)}")
    
    except Exception as e:
        logging.error(f"Erreur lors de la collecte des logs: {str(e)}")
    
    return logs

def collect_service_metrics(service_name):
    """
    Collecte des métriques spécifiques à un service
    """
    metrics = {}
    
    try:
        # Trouver les processus associés au service
        service_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if (service_name.lower() in proc.info['name'].lower() or 
                    (proc.info['cmdline'] and any(service_name.lower() in cmd.lower() for cmd in proc.info['cmdline']))):
                    service_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if service_processes:
            # Calculer l'utilisation totale du CPU
            cpu_percent = sum(p.cpu_percent(interval=0.1) for p in service_processes)
            metrics["cpu_usage"] = round(cpu_percent, 2)
            
            # Calculer l'utilisation totale de la mémoire
            memory_info = sum(p.memory_info().rss for p in service_processes)
            memory_mb = memory_info / (1024 * 1024)  # Convertir en MB
            metrics["memory_usage"] = round(memory_mb, 2)
            
            # Compter les connexions réseau
            try:
                connections = []
                for p in service_processes:
                    connections.extend(p.connections())
                
                metrics["connections"] = len(connections)
                
                # Compter les connexions par état
                conn_states = {}
                for conn in connections:
                    state = conn.status
                    conn_states[state] = conn_states.get(state, 0) + 1
                
                metrics["connection_states"] = conn_states
            except psutil.AccessDenied:
                pass
        
        # Service-specific metrics
        if service_name == "nginx" or service_name == "nginx.service":
            try:
                # Essayer de récupérer les métriques de Nginx (nécessite ngxtop ou similaire)
                # Ceci est simplifié, dans un cas réel il faudrait installer et utiliser ngxtop ou similaire
                metrics["requests_per_second"] = 0
            except Exception:
                pass
        
        elif service_name == "mysql" or service_name == "mysqld":
            try:
                # Essayer de récupérer les métriques de MySQL
                # Ceci est simplifié, dans un cas réel il faudrait interroger MySQL pour les métriques
                metrics["queries_per_second"] = 0
            except Exception:
                pass
    
    except Exception as e:
        logging.error(f"Erreur lors de la collecte des métriques du service: {str(e)}")
    
    return metrics
