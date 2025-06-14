#!/usr/bin/env python3
"""
Gestionnaire de templates pour Cloudya
Suit l'architecture hybride recommandée avec hiérarchie XDG
"""

import os
import yaml
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from importlib.resources import files
import shutil
import requests

class TemplateNotFoundError(Exception):
    """Exception levée quand un template n'est pas trouvé"""
    pass

class CloudyaTemplateManager:
    """Gestionnaire de templates avec résolution hiérarchique"""
    
    def __init__(self):
        self.setup_paths()
        self.load_config()
    
    def setup_paths(self):
        """Configure les chemins de recherche selon les standards XDG"""
        # Variables d'environnement XDG
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')
        xdg_data_home = os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')
        xdg_cache_home = os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')
        
        # Chemins de recherche par ordre de priorité
        self.search_paths = [
            Path(xdg_config_home) / 'cloudya' / 'templates',  # 1. Templates utilisateur personnalisés
            Path(xdg_data_home) / 'cloudya' / 'templates',    # 2. Templates utilisateur partagés
            Path('/usr/local/share/cloudya/templates'),        # 3. Templates système locaux
            # 4. Templates du package (via importlib.resources) - géré séparément
        ]
        
        # Répertoires de travail
        self.config_dir = Path(xdg_config_home) / 'cloudya'
        self.data_dir = Path(xdg_data_home) / 'cloudya'
        self.cache_dir = Path(xdg_cache_home) / 'cloudya'
        
        # Créer les répertoires nécessaires
        for path in self.search_paths[:2]:  # Seulement les répertoires utilisateur
            path.mkdir(parents=True, exist_ok=True)
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self):
        """Charge la configuration des templates"""
        config_file = self.config_dir / 'config.yaml'
        
        # Configuration par défaut
        self.config = {
            'templates': {
                'default_engine': 'jinja2',
                'extensions': ['.j2', '.yaml', '.yml', '.tf', '.py'],
            },
            'repositories': [
                {
                    'name': 'official',
                    'url': 'https://github.com/acorvez/cloudya-templates',
                    'branch': 'main'
                }
            ]
        }
        
        # Charger la config utilisateur si elle existe
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self.config.update(user_config)
            except Exception as e:
                print(f"Erreur lors du chargement de la config: {e}")
    
    def resolve_template(self, template_name: str, category: str = None) -> str:
        """
        Résout un template en suivant la hiérarchie de priorité
        
        Args:
            template_name: Nom du template (ex: 'vpc', 'wordpress')
            category: Catégorie optionnelle (ex: 'terraform/aws', 'apps')
        
        Returns:
            Contenu du template
        """
        # Construire les chemins possibles
        if category:
            template_paths = [f"{category}/{template_name}", template_name]
        else:
            template_paths = [template_name]
        
        # Extensions possibles
        extensions = self.config['templates']['extensions']
        
        # Recherche dans les chemins utilisateur/système
        for search_path in self.search_paths:
            for template_path in template_paths:
                for ext in extensions:
                    full_path = search_path / f"{template_path}{ext}"
                    if full_path.exists():
                        return full_path.read_text(encoding='utf-8')
        
        # Fallback sur les templates du package
        try:
            package_templates = files("cloudya.templates")
            for template_path in template_paths:
                for ext in extensions:
                    try:
                        template_file = package_templates / f"{template_path}{ext}"
                        return template_file.read_text(encoding='utf-8')
                    except FileNotFoundError:
                        continue
        except Exception:
            pass
        
        raise TemplateNotFoundError(f"Template '{template_name}' not found in category '{category}'")
    
    def list_templates(self, category: str = None) -> Dict[str, List[str]]:
        """
        Liste tous les templates disponibles par source
        
        Args:
            category: Filtrer par catégorie (optionnel)
        
        Returns:
            Dictionnaire {source: [templates]}
        """
        templates = {
            'user_config': [],
            'user_data': [],
            'system': [],
            'package': []
        }
        
        source_names = ['user_config', 'user_data', 'system']
        
        # Scanner les répertoires
        for i, search_path in enumerate(self.search_paths):
            if search_path.exists():
                templates[source_names[i]] = self._scan_directory(search_path, category)
        
        # Scanner les templates du package
        try:
            package_templates = files("cloudya.templates")
            templates['package'] = self._scan_package_templates(package_templates, category)
        except Exception:
            pass
        
        return templates
    
    def _scan_directory(self, directory: Path, category: str = None) -> List[str]:
        """Scanne un répertoire pour trouver les templates"""
        templates = []
        
        if category:
            scan_dir = directory / category
            if not scan_dir.exists():
                return templates
        else:
            scan_dir = directory
        
        extensions = self.config['templates']['extensions']
        
        for template_file in scan_dir.rglob('*'):
            if template_file.is_file() and any(template_file.name.endswith(ext) for ext in extensions):
                # Calculer le nom relatif
                rel_path = template_file.relative_to(directory)
                template_name = str(rel_path)
                
                # Supprimer l'extension
                for ext in extensions:
                    if template_name.endswith(ext):
                        template_name = template_name[:-len(ext)]
                        break
                
                templates.append(template_name)
        
        return sorted(templates)
    
    def _scan_package_templates(self, package_templates, category: str = None) -> List[str]:
        """Scanne les templates du package"""
        templates = []
        
        # Cette implémentation dépend de la structure du package
        # Pour l'instant, retourner une liste simulée
        return [
            'terraform/aws/vpc',
            'terraform/aws/eks',
            'terraform/gcp/vpc',
            'apps/wordpress',
            'apps/nextcloud',
            'config/cloudya'
        ]
    
    def install_template(self, template_name: str, source_url: str, category: str = None) -> bool:
        """
        Installe un template depuis une URL
        
        Args:
            template_name: Nom du template
            source_url: URL source
            category: Catégorie de destination
        
        Returns:
            True si réussi
        """
        try:
            # Télécharger le template
            response = requests.get(source_url, timeout=30)
            response.raise_for_status()
            
            # Déterminer le chemin de destination (templates utilisateur)
            dest_dir = self.search_paths[1]  # ~/.local/share/cloudya/templates
            if category:
                dest_dir = dest_dir / category
            
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder le template
            template_file = dest_dir / f"{template_name}.j2"
            template_file.write_text(response.text, encoding='utf-8')
            
            print(f"Template '{template_name}' installé dans {template_file}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'installation du template: {e}")
            return False
    
    def remove_template(self, template_name: str, category: str = None) -> bool:
        """
        Supprime un template utilisateur
        
        Args:
            template_name: Nom du template
            category: Catégorie
        
        Returns:
            True si réussi
        """
        # Chercher dans les répertoires utilisateur seulement
        for search_path in self.search_paths[:2]:
            template_path = search_path
            if category:
                template_path = template_path / category
            
            extensions = self.config['templates']['extensions']
            for ext in extensions:
                template_file = template_path / f"{template_name}{ext}"
                if template_file.exists():
                    template_file.unlink()
                    print(f"Template '{template_name}' supprimé")
                    return True
        
        print(f"Template '{template_name}' non trouvé dans les répertoires utilisateur")
        return False
    
    def show_template_info(self, template_name: str, category: str = None) -> Dict:
        """
        Affiche les informations d'un template
        
        Args:
            template_name: Nom du template
            category: Catégorie
        
        Returns:
            Dictionnaire avec les infos du template
        """
        info = {
            'name': template_name,
            'category': category,
            'found': False,
            'source': None,
            'path': None,
            'size': None,
            'content_preview': None
        }
        
        # Chercher le template
        try:
            content = self.resolve_template(template_name, category)
            info['found'] = True
            info['content_preview'] = content[:200] + "..." if len(content) > 200 else content
            
            # Trouver le chemin source
            for i, search_path in enumerate(self.search_paths):
                template_paths = [f"{category}/{template_name}" if category else template_name]
                for template_path in template_paths:
                    for ext in self.config['templates']['extensions']:
                        full_path = search_path / f"{template_path}{ext}"
                        if full_path.exists():
                            info['source'] = ['user_config', 'user_data', 'system'][i]
                            info['path'] = str(full_path)
                            info['size'] = full_path.stat().st_size
                            break
            
            if not info['source']:
                info['source'] = 'package'
                info['path'] = 'cloudya.templates'
                
        except TemplateNotFoundError:
            pass
        
        return info
    
    def create_default_templates(self):
        """Crée les templates par défaut dans le package"""
        # Cette méthode sera utilisée lors de l'installation
        default_templates = {
            'config/cloudya.yaml': '''# Configuration Cloudya
api:
  url: {{ api_url | default('https://api.cloudya.ai') }}

preferences:
  default_provider: {{ default_provider | default('aws') }}
  default_region: {{ default_region | default('us-east-1') }}

paths:
  templates: ~/.cloudya/templates
  logs: ~/.cloudya/logs
''',
            'terraform/aws/vpc.tf': '''# VPC AWS généré par Cloudya
resource "aws_vpc" "main" {
  cidr_block           = "{{ vpc_cidr | default('10.0.0.0/16') }}"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "{{ vpc_name | default('cloudya-vpc') }}"
    Environment = "{{ environment | default('dev') }}"
  }
}
''',
            'apps/wordpress.yml': '''# WordPress deployment via Ansible
- name: Install WordPress
  hosts: all
  become: yes
  vars:
    domain: "{{ domain | default('localhost') }}"
    admin_user: "{{ admin_user | default('admin') }}"
    
  tasks:
    - name: Install packages
      package:
        name:
          - nginx
          - php-fpm
          - mysql-server
        state: present
'''
        }
        
        return default_templates

# Instance globale
template_manager = CloudyaTemplateManager()

# Fonctions utilitaires
def resolve_template(template_name: str, category: str = None) -> str:
    """Fonction utilitaire pour résoudre un template"""
    return template_manager.resolve_template(template_name, category)

def list_templates(category: str = None) -> Dict[str, List[str]]:
    """Fonction utilitaire pour lister les templates"""
    return template_manager.list_templates(category)
