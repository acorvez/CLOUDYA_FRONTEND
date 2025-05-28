import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au path pour pouvoir importer cloudya
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cloudya.utils import system


@patch('psutil.cpu_percent', return_value=50)
@patch('psutil.cpu_count', return_value=4)
def test_check_cpu_usage(mock_cpu_count, mock_cpu_percent):
    """Test la vérification de l'utilisation du CPU"""
    result = system.check_cpu_usage()
    
    assert result['usage'] == 50
    assert result['count'] == 4
    
    mock_cpu_percent.assert_called_once()
    mock_cpu_count.assert_called_once()


@patch('psutil.virtual_memory')
def test_check_memory_usage(mock_virtual_memory):
    """Test la vérification de l'utilisation de la mémoire"""
    # Mock de l'objet retourné par virtual_memory
    mock_memory = MagicMock()
    mock_memory.percent = 75
    mock_memory.total = 16 * 1024 * 1024 * 1024  # 16 GB
    mock_memory.used = 12 * 1024 * 1024 * 1024   # 12 GB
    mock_memory.available = 4 * 1024 * 1024 * 1024  # 4 GB
    
    mock_virtual_memory.return_value = mock_memory
    
    result = system.check_memory_usage()
    
    assert result['usage'] == 75
    assert result['total'] == '16.00GB'
    assert result['used'] == '12.00GB'
    assert result['available'] == '4.00GB'
    
    mock_virtual_memory.assert_called_once()


@patch('psutil.disk_usage')
def test_check_disk_usage(mock_disk_usage):
    """Test la vérification de l'utilisation du disque"""
    # Mock de l'objet retourné par disk_usage
    mock_disk = MagicMock()
    mock_disk.percent = 60
    mock_disk.total = 500 * 1024 * 1024 * 1024  # 500 GB
    mock_disk.used = 300 * 1024 * 1024 * 1024   # 300 GB
    mock_disk.free = 200 * 1024 * 1024 * 1024   # 200 GB
    
    mock_disk_usage.return_value = mock_disk
    
    result = system.check_disk_usage()
    
    assert result['usage'] == 60
    assert result['total'] == '500.00GB'
    assert result['used'] == '300.00GB'
    assert result['free'] == '200.00GB'
    assert result['path'] == '/'
    
    mock_disk_usage.assert_called_once()


@patch('platform.system', return_value='Linux')
@patch('subprocess.run')
def test_check_service_status_linux(mock_run, mock_platform):
    """Test la vérification de l'état d'un service sous Linux"""
    # Mocks pour les appels à subprocess.run
    mock_list_unit = MagicMock()
    mock_list_unit.stdout = "nginx.service               enabled"
    
    mock_is_active = MagicMock()
    mock_is_active.stdout = "active"
    
    mock_status = MagicMock()
    mock_status.stdout = """
    ● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2021-05-17 12:34:56 UTC; 2h ago
       Docs: man:nginx(8)
    Process: 1234 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
    Process: 1235 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
    Main PID: 1236 (nginx)
       Tasks: 2 (limit: 4915)
      Memory: 5.0M
     CGroup: /system.slice/nginx.service
             ├─1236 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
             └─1237 nginx: worker process
    """
    
    # Configurer les retours des appels à subprocess.run
    mock_run.side_effect = [mock_list_unit, mock_is_active, mock_status]
    
    result = system.check_service_status('nginx')
    
    assert result['name'] == 'nginx'
    assert result['exists'] == True
    assert result['running'] == True
    
    # Vérifier les appels à subprocess.run
    assert mock_run.call_count == 3


@patch('platform.system', return_value='Linux')
@patch('subprocess.run')
def test_check_service_status_not_found(mock_run, mock_platform):
    """Test la vérification d'un service inexistant"""
    # Mock pour l'appel à subprocess.run
    mock_list_unit = MagicMock()
    mock_list_unit.stdout = "No unit files found."
    
    mock_run.return_value = mock_list_unit
    
    # Mock de psutil.process_iter
    with patch('psutil.process_iter', return_value=[]) as mock_process_iter:
        result = system.check_service_status('nonexistent')
        
        assert result['name'] == 'nonexistent'
        assert result['exists'] == False
        assert result['running'] == False
        
        mock_process_iter.assert_called_once()


@patch('platform.system', return_value='Linux')
@patch('subprocess.run')
def test_collect_logs(mock_run, mock_platform):
    """Test la collecte des logs d'un service"""
    # Mock pour l'appel à subprocess.run
    mock_journalctl = MagicMock()
    mock_journalctl.stdout = """
    May 17 12:34:56 hostname nginx[1234]: 172.17.0.1 - - [17/May/2021:12:34:56 +0000] "GET / HTTP/1.1" 200 612 "-" "Mozilla/5.0"
    May 17 12:35:00 hostname nginx[1234]: 172.17.0.1 - - [17/May/2021:12:35:00 +0000] "GET /favicon.ico HTTP/1.1" 404 153 "-" "Mozilla/5.0"
    May 17 12:35:05 hostname nginx[1234]: 2021/05/17 12:35:05 [error] 1234#1234: *1 open() "/var/www/html/favicon.ico" failed (2: No such file or directory)
    """
    
    mock_run.return_value = mock_journalctl
    
    logs = system.collect_logs('nginx', days=1)
    
    assert len(logs) == 3
    assert logs[0]['timestamp'] == 'May 17 12:34:56'
    assert logs[0]['level'] == 'INFO'
    assert logs[2]['level'] == 'ERROR'  # Détection d'une erreur dans le log
    
    # Vérifier l'appel à subprocess.run
    mock_run.assert_called_once()


@patch('psutil.process_iter')
def test_collect_service_metrics(mock_process_iter):
    """Test la collecte des métriques d'un service"""
    # Mock pour un processus
    mock_process = MagicMock()
    mock_process.info = {'name': 'nginx', 'pid': 1234}
    mock_process.cpu_percent.return_value = 2.5
    mock_process.memory_info.return_value.rss = 50 * 1024 * 1024  # 50 MB
    mock_process.connections.return_value = [MagicMock(status='ESTABLISHED'), MagicMock(status='LISTEN')]
    
    mock_process_iter.return_value = [mock_process]
    
    metrics = system.collect_service_metrics('nginx')
    
    assert metrics['cpu_usage'] == 2.5
    assert metrics['memory_usage'] == 50.0  # En MB
    assert metrics['connections'] == 2
    assert metrics['connection_states']['ESTABLISHED'] == 1
    assert metrics['connection_states']['LISTEN'] == 1
    
    mock_process_iter.assert_called_once()
    mock_process.cpu_percent.assert_called_once()
    mock_process.memory_info.assert_called_once()
    mock_process.connections.assert_called_once()
