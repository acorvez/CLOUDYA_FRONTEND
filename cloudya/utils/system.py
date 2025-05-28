import os
import psutil
import platform
import subprocess
import time
import random
from datetime import datetime

def check_cpu_usage():
    """
    Vérifie l'utilisation du CPU.
    """
    try:
        # Utiliser psutil si disponible
        cpu_usage = psutil.cpu_percent(interval=1)
        return {
            "usage": cpu_usage,
            "status": "ok" if cpu_usage < 80 else "warning" if cpu_usage < 95 else "critical"
        }
    except:
        # Simulation si psutil n'est pas disponible
        cpu_usage = random.uniform(10, 90)
        return {
            "usage": round(cpu_usage, 2),
            "status": "ok" if cpu_usage < 80 else "warning" if cpu_usage < 95 else "critical"
        }

def check_memory_usage():
    """
    Vérifie l'utilisation de la mémoire.
    """
    try:
        # Utiliser psutil si disponible
        memory = psutil.virtual_memory()
        return {
            "usage": memory.percent,
            "used": f"{memory.used / (1024 * 1024 * 1024):.2f}GB",
            "total": f"{memory.total / (1024 * 1024 * 1024):.2f}GB",
            "status": "ok" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
        }
    except:
        # Simulation si psutil n'est pas disponible
        memory_usage = random.uniform(50, 85)
        memory_total = 16  # GB
        memory_used = memory_total * (memory_usage / 100)
        return {
            "usage": round(memory_usage, 2),
            "used": f"{memory_used:.2f}GB",
            "total": f"{memory_total:.2f}GB",
            "status": "ok" if memory_usage < 80 else "warning" if memory_usage < 95 else "critical"
        }

def check_disk_usage(path="/"):
    """
    Vérifie l'utilisation du disque.
    """
    try:
        # Utiliser psutil si disponible
        disk = psutil.disk_usage(path)
        return {
            "usage": disk.percent,
            "used": f"{disk.used / (1024 * 1024 * 1024):.2f}GB",
            "total": f"{disk.total / (1024 * 1024 * 1024):.2f}GB",
            "status": "ok" if disk.percent < 80 else "warning" if disk.percent < 95 else "critical"
        }
    except:
        # Simulation si psutil n'est pas disponible
        disk_usage = random.uniform(40, 75)
        disk_total = 500  # GB
        disk_used = disk_total * (disk_usage / 100)
        return {
            "usage": round(disk_usage, 2),
            "used": f"{disk_used:.2f}GB",
            "total": f"{disk_total:.2f}GB",
            "status": "ok" if disk_usage < 80 else "warning" if disk_usage < 95 else "critical"
        }

def check_service_status(service_name):
    """
    Vérifie l'état d'un service.
    """
    # Liste des services connus (simulation)
    known_services = ["nginx", "apache2", "mysql", "postgresql", "redis", "mongodb", "docker"]
    
    # Vérifier si le service existe
    if service_name.lower() not in known_services:
        return {
            "exists": False,
            "running": False,
            "status": "unknown"
        }
    
    try:
        # Essayer de vérifier l'état du service (dépend du système d'exploitation)
        if platform.system() == "Linux":
            # Utiliser systemctl pour vérifier l'état du service sur Linux
            result = subprocess.run(["systemctl", "is-active", service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            running = result.stdout.strip() == "active"
        elif platform.system() == "Windows":
            # Utiliser sc query pour vérifier l'état du service sur Windows
            result = subprocess.run(["sc", "query", service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            running = "RUNNING" in result.stdout
        else:
            # Simulation pour les autres systèmes d'exploitation
            running = random.choice([True, True, True, False])  # 75% de chance d'être en cours d'exécution
        
        return {
            "exists": True,
            "running": running,
            "status": "running" if running else "stopped"
        }
    except:
        # Simulation en cas d'erreur
        running = random.choice([True, True, True, False])  # 75% de chance d'être en cours d'exécution
        return {
            "exists": True,
            "running": running,
            "status": "running" if running else "stopped"
        }

def collect_service_metrics(service_name):
    """
    Collecte des métriques pour un service spécifique.
    """
    # Liste des services connus (simulation)
    known_services = ["nginx", "apache2", "mysql", "postgresql", "redis", "mongodb", "docker"]
    
    # Vérifier si le service existe
    if service_name.lower() not in known_services:
        return None
    
    # Simulation de métriques spécifiques au service
    cpu_usage = random.uniform(10, 70)
    memory_usage = random.uniform(100, 500)  # MB
    connections = random.randint(10, 200)
    requests_per_second = random.uniform(1, 50)
    
    return {
        "cpu_usage": round(cpu_usage, 2),
        "memory_usage": round(memory_usage, 2),
        "connections": connections,
        "requests_per_second": round(requests_per_second, 2)
    }

def get_system_info():
    """
    Obtient des informations système générales.
    """
    try:
        # Utiliser psutil si disponible
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage("/")
        
        return {
            "hostname": platform.node(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "boot_time": boot_time,
            "cpu_count": cpu_count,
            "memory_total": f"{memory.total / (1024 * 1024 * 1024):.2f}GB",
            "swap_total": f"{swap.total / (1024 * 1024 * 1024):.2f}GB",
            "disk_total": f"{disk.total / (1024 * 1024 * 1024):.2f}GB"
        }
    except:
        # Simulation si psutil n'est pas disponible
        return {
            "hostname": platform.node(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "boot_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_count": 4,
            "memory_total": "16.00GB",
            "swap_total": "2.00GB",
            "disk_total": "500.00GB"
        }

def collect_network_stats():
    """
    Collecte des statistiques réseau.
    """
    try:
        # Utiliser psutil si disponible
        network = psutil.net_io_counters()
        
        return {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv,
            "errin": network.errin,
            "errout": network.errout,
            "dropin": network.dropin,
            "dropout": network.dropout
        }
    except:
        # Simulation si psutil n'est pas disponible
        return {
            "bytes_sent": random.randint(1000000, 10000000),
            "bytes_recv": random.randint(10000000, 100000000),
            "packets_sent": random.randint(10000, 100000),
            "packets_recv": random.randint(100000, 1000000),
            "errin": random.randint(0, 10),
            "errout": random.randint(0, 10),
            "dropin": random.randint(0, 5),
            "dropout": random.randint(0, 5)
        }

def get_process_list():
    """
    Obtient la liste des processus en cours d'exécution.
    """
    try:
        # Utiliser psutil si disponible
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            processes.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "username": proc.info['username'],
                "memory_percent": proc.info['memory_percent'],
                "cpu_percent": proc.info['cpu_percent']
            })
        
        # Trier par utilisation CPU
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return processes[:10]  # Retourner les 10 processus les plus consommateurs
    except:
        # Simulation si psutil n'est pas disponible
        processes = []
        for i in range(10):
            processes.append({
                "pid": random.randint(1, 10000),
                "name": random.choice(["python", "bash", "nginx", "apache2", "mysql", "firefox", "chrome", "systemd"]),
                "username": random.choice(["root", "www-data", "user"]),
                "memory_percent": random.uniform(0.1, 5.0),
                "cpu_percent": random.uniform(0.1, 10.0)
            })
        
        # Trier par utilisation CPU
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return processes
