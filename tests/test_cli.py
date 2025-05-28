import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

# Ajouter le répertoire parent au path pour pouvoir importer cloudya
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cloudya.cli import app


@pytest.fixture
def runner():
    return CliRunner()


def test_version(runner):
    """Test la commande version"""
    with patch('cloudya.cli.rprint') as mock_rprint:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        mock_rprint.assert_called()


def test_login(runner):
    """Test la commande login"""
    with patch('cloudya.utils.config.load_config', return_value={'auth': {}}):
        with patch('cloudya.utils.config.save_config') as mock_save:
            with patch('cloudya.cli.rprint') as mock_rprint:
                result = runner.invoke(app, ["login", "--token", "test_token"])
                assert result.exit_code == 0
                mock_save.assert_called_once()
                mock_rprint.assert_called()


def test_register(runner):
    """Test la commande register"""
    with patch('cloudya.utils.config.load_config', return_value={'auth': {}}):
        with patch('cloudya.utils.config.save_config') as mock_save:
            with patch('cloudya.cli.rprint') as mock_rprint:
                result = runner.invoke(app, ["register", "--email", "test@example.com"])
                assert result.exit_code == 0
                mock_save.assert_called_once()
                mock_rprint.assert_called()


def test_callback():
    """Test le callback de l'application"""
    with patch('os.path.exists', return_value=False):
        with patch('os.makedirs') as mock_makedirs:
            with patch('cloudya.utils.config.create_default_config') as mock_create_config:
                from cloudya.cli import callback
                callback()
                
                # Vérifier que le répertoire a été créé si nécessaire
                mock_makedirs.assert_called_once()
                
                # Vérifier que la configuration par défaut a été créée
                mock_create_config.assert_called_once()
