import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au path pour pouvoir importer cloudya
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cloudya.utils import config


def test_create_default_config():
    """Test la création de la configuration par défaut"""
    with patch('cloudya.utils.config.save_config') as mock_save:
        with patch('os.makedirs') as mock_makedirs:
            cfg = config.create_default_config('/tmp/config.yaml')
            
            # Vérifier que le répertoire a été créé
            mock_makedirs.assert_called_once()
            
            # Vérifier que save_config a été appelé
            mock_save.assert_called_once()
            
            # Vérifier le contenu de la configuration
            assert 'auth' in cfg
            assert 'preferences' in cfg
            assert 'paths' in cfg


def test_load_config_existing():
    """Test le chargement d'une configuration existante"""
    mock_config = {
        'auth': {'token': 'test_token'},
        'preferences': {'default_provider': 'aws'},
        'paths': {'templates': '/tmp/templates'}
    }
    
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', MagicMock()):
            with patch('yaml.safe_load', return_value=mock_config):
                cfg = config.load_config('/tmp/config.yaml')
                
                assert cfg == mock_config
                assert cfg['auth']['token'] == 'test_token'


def test_load_config_non_existing():
    """Test le chargement d'une configuration non existante"""
    with patch('os.path.exists', return_value=False):
        with patch('cloudya.utils.config.create_default_config') as mock_create:
            mock_create.return_value = {'auth': {'token': None}}
            
            cfg = config.load_config('/tmp/config.yaml')
            
            # Vérifier que create_default_config a été appelé
            mock_create.assert_called_once_with('/tmp/config.yaml')
            
            assert cfg['auth']['token'] is None


def test_save_config():
    """Test la sauvegarde de la configuration"""
    mock_config = {
        'auth': {'token': 'test_token'},
        'preferences': {'default_provider': 'aws'},
        'paths': {'templates': '/tmp/templates'}
    }
    
    mock_open = MagicMock()
    with patch('builtins.open', mock_open):
        with patch('yaml.dump') as mock_dump:
            config.save_config('/tmp/config.yaml', mock_config)
            
            # Vérifier que le fichier a été ouvert en écriture
            mock_open.assert_called_once_with('/tmp/config.yaml', 'w')
            
            # Vérifier que yaml.dump a été appelé
            mock_dump.assert_called_once()


def test_get_config_value():
    """Test la récupération d'une valeur dans la configuration"""
    mock_config = {
        'auth': {'token': 'test_token'},
        'preferences': {'default_provider': 'aws'},
        'paths': {'templates': '/tmp/templates'}
    }
    
    # Test d'une valeur existante
    value = config.get_config_value(mock_config, 'auth.token')
    assert value == 'test_token'
    
    # Test d'une valeur inexistante
    value = config.get_config_value(mock_config, 'auth.email')
    assert value is None
    
    # Test d'une valeur inexistante avec une valeur par défaut
    value = config.get_config_value(mock_config, 'auth.email', default='default@example.com')
    assert value == 'default@example.com'


def test_set_config_value():
    """Test la définition d'une valeur dans la configuration"""
    mock_config = {
        'auth': {'token': 'test_token'},
        'preferences': {'default_provider': 'aws'},
        'paths': {'templates': '/tmp/templates'}
    }
    
    # Modifier une valeur existante
    updated_config = config.set_config_value(mock_config, 'auth.token', 'new_token')
    assert updated_config['auth']['token'] == 'new_token'
    
    # Ajouter une nouvelle valeur
    updated_config = config.set_config_value(mock_config, 'auth.email', 'test@example.com')
    assert updated_config['auth']['email'] == 'test@example.com'
    
    # Ajouter une nouvelle section et valeur
    updated_config = config.set_config_value(mock_config, 'newSection.key', 'value')
    assert updated_config['newSection']['key'] == 'value'
