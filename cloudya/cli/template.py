#!/usr/bin/env python3
"""
Commande template pour Cloudya CLI
Gestion des templates avec l'architecture hybride
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

# Import du gestionnaire de templates
try:
    from cloudya.template_manager import template_manager, TemplateNotFoundError
except ImportError:
    # Fallback si le gestionnaire n'est pas disponible
    print("❌ Gestionnaire de templates non disponible")
    sys.exit(1)

console = Console()

def show_help():
    """Affiche l'aide de la commande template"""
    help_text = """
🔧 Cloudya Template Manager

Usage: cloudya template COMMAND [OPTIONS]

Commandes:
  list                     Liste tous les templates disponibles
  list CATEGORY           Liste les templates d'une catégorie
  show NAME               Affiche un template
  show NAME --category=CAT Affiche un template dans une catégorie
  install NAME URL        Installe un template depuis une URL
  remove NAME             Supprime un template utilisateur
  info NAME               Affiche les informations d'un template
  paths                   Affiche les chemins de recherche

Exemples:
  cloudya template list
  cloudya template list terraform/aws
  cloudya template show vpc --category=terraform/aws
  cloudya template install my-vpc https://raw.githubusercontent.com/.../vpc.tf
  cloudya template remove my-vpc
  cloudya template info wordpress --category=apps

Hiérarchie des templates:
  1. ~/.config/cloudya/templates/     (personnalisés utilisateur)
  2. ~/.local/share/cloudya/templates/ (partagés utilisateur)  
  3. /usr/local/share/cloudya/templates/ (système)
  4. Package cloudya (par défaut)
"""
    console.print(Panel(help_text, title="🔧 Template Manager", border_style="blue"))

def list_templates(category=None):
    """Liste les templates disponibles"""
    try:
        templates = template_manager.list_templates(category)
        
        if category:
            console.print(f"📁 Templates dans la catégorie: [cyan]{category}[/cyan]\n")
        else:
            console.print("📁 Tous les templates disponibles\n")
        
        # Créer une table pour chaque source
        sources = {
            'user_config': '👤 Templates personnalisés (~/.config/cloudya/templates)',
            'user_data': '📚 Templates partagés (~/.local/share/cloudya/templates)',
            'system': '🏢 Templates système (/usr/local/share/cloudya/templates)',
            'package': '📦 Templates par défaut (package)'
        }
        
        total_templates = 0
        
        for source_key, source_title in sources.items():
            if templates[source_key]:
                table = Table(title=source_title, show_header=False)
                table.add_column("Template", style="cyan")
                
                for template in templates[source_key]:
                    table.add_row(f"  {template}")
                    total_templates += 1
                
                console.print(table)
                console.print()
        
        if total_templates == 0:
            if category:
                console.print(f"[yellow]Aucun template trouvé dans la catégorie '{category}'[/yellow]")
            else:
                console.print("[yellow]Aucun template disponible[/yellow]")
        else:
            console.print(f"[green]Total: {total_templates} template(s) trouvé(s)[/green]")
            
    except Exception as e:
        console.print(f"[red]Erreur lors de la liste des templates: {e}[/red]")

def show_template(name, category=None):
    """Affiche le contenu d'un template"""
    try:
        content = template_manager.resolve_template(name, category)
        
        # Déterminer le langage pour la coloration syntaxique
        if name.endswith('.tf') or category and 'terraform' in category:
            language = "hcl"
        elif name.endswith('.yml') or name.endswith('.yaml'):
            language = "yaml"
        elif name.endswith('.py'):
            language = "python"
        elif name.endswith('.sh'):
            language = "bash"
        else:
            language = "text"
        
        # Afficher avec coloration syntaxique
        syntax = Syntax(content, language, theme="monokai", line_numbers=True)
        
        title = f"📄 Template: {name}"
        if category:
            title += f" (catégorie: {category})"
            
        console.print(Panel(syntax, title=title, border_style="green"))
        
    except TemplateNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        console.print("\n[yellow]Templates disponibles:[/yellow]")
        list_templates(category)
    except Exception as e:
        console.print(f"[red]Erreur lors de l'affichage du template: {e}[/red]")

def install_template(name, url, category=None):
    """Installe un template depuis une URL"""
    console.print(f"📥 Installation du template '[cyan]{name}[/cyan]' depuis [blue]{url}[/blue]")
    
    try:
        if template_manager.install_template(name, url, category):
            console.print(f"[green]✅ Template '{name}' installé avec succès![/green]")
            if category:
                console.print(f"   Catégorie: {category}")
            console.print(f"   Emplacement: ~/.local/share/cloudya/templates/")
        else:
            console.print(f"[red]❌ Échec de l'installation du template '{name}'[/red]")
    except Exception as e:
        console.print(f"[red]❌ Erreur lors de l'installation: {e}[/red]")

def remove_template(name, category=None):
    """Supprime un template utilisateur"""
    console.print(f"🗑️  Suppression du template '[cyan]{name}[/cyan]'")
    
    try:
        if template_manager.remove_template(name, category):
            console.print(f"[green]✅ Template '{name}' supprimé avec succès![/green]")
        else:
            console.print(f"[yellow]⚠️ Template '{name}' non trouvé dans les répertoires utilisateur[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Erreur lors de la suppression: {e}[/red]")

def show_template_info(name, category=None):
    """Affiche les informations détaillées d'un template"""
    try:
        info = template_manager.show_template_info(name, category)
        
        if not info['found']:
            console.print(f"[red]❌ Template '{name}' non trouvé[/red]")
            return
        
        # Créer un tableau d'informations
        table = Table(title=f"📋 Informations: {name}", show_header=False)
        table.add_column("Propriété", style="cyan", width=15)
        table.add_column("Valeur", style="white")
        
        table.add_row("Nom", info['name'])
        if info['category']:
            table.add_row("Catégorie", info['category'])
        table.add_row("Source", info['source'])
        table.add_row("Chemin", info['path'])
        if info['size']:
            table.add_row("Taille", f"{info['size']} octets")
        
        console.print(table)
        
        # Afficher un aperçu du contenu
        if info['content_preview']:
            console.print("\n📄 Aperçu du contenu:")
            preview = Syntax(info['content_preview'], "text", theme="monokai")
            console.print(Panel(preview, border_style="dim"))
            
    except Exception as e:
        console.print(f"[red]❌ Erreur lors de la récupération des informations: {e}[/red]")

def show_paths():
    """Affiche les chemins de recherche des templates"""
    console.print("📂 Chemins de recherche des templates (par ordre de priorité):\n")
    
    table = Table()
    table.add_column("Priorité", style="cyan", width=8)
    table.add_column("Type", style="green", width=20)
    table.add_column("Chemin", style="white")
    table.add_column("Existe", style="yellow", width=8)
    
    # Chemins de recherche
    paths_info = [
        (1, "Config utilisateur", template_manager.search_paths[0]),
        (2, "Data utilisateur", template_manager.search_paths[1]),
        (3, "Système", template_manager.search_paths[2]),
        (4, "Package", "cloudya.templates (importlib.resources)")
    ]
    
    for priority, path_type, path in paths_info:
        if isinstance(path, Path):
            exists = "✅" if path.exists() else "❌"
            path_str = str(path)
        else:
            exists = "📦"
            path_str = path
            
        table.add_row(str(priority), path_type, path_str, exists)
    
    console.print(table)
    
    # Afficher les variables d'environnement XDG
    console.print("\n🔧 Variables d'environnement XDG:")
    xdg_vars = [
        ("XDG_CONFIG_HOME", "~/.config"),
        ("XDG_DATA_HOME", "~/.local/share"),
        ("XDG_CACHE_HOME", "~/.cache")
    ]
    
    for var_name, default_value in xdg_vars:
        import os
        current_value = os.environ.get(var_name, default_value)
        console.print(f"  {var_name}: [cyan]{current_value}[/cyan]")

def main():
    """Point d'entrée principal de la commande template"""
    parser = argparse.ArgumentParser(
        description="Gestionnaire de templates Cloudya",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("command", nargs="?", help="Commande à exécuter")
    parser.add_argument("name", nargs="?", help="Nom du template")
    parser.add_argument("url", nargs="?", help="URL source (pour install)")
    parser.add_argument("--category", "-c", help="Catégorie du template")
    parser.add_argument("--force", "-f", action="store_true", help="Forcer l'opération")
    
    args = parser.parse_args()
    
    # Si aucune commande, afficher l'aide
    if not args.command:
        show_help()
        return 0
    
    command = args.command.lower()
    
    try:
        if command == "list":
            list_templates(args.name)  # args.name sert de catégorie pour list
            
        elif command == "show":
            if not args.name:
                console.print("[red]❌ Nom du template requis pour 'show'[/red]")
                return 1
            show_template(args.name, args.category)
            
        elif command == "install":
            if not args.name or not args.url:
                console.print("[red]❌ Nom et URL requis pour 'install'[/red]")
                console.print("Usage: cloudya template install NAME URL [--category=CATEGORY]")
                return 1
            install_template(args.name, args.url, args.category)
            
        elif command == "remove":
            if not args.name:
                console.print("[red]❌ Nom du template requis pour 'remove'[/red]")
                return 1
            remove_template(args.name, args.category)
            
        elif command == "info":
            if not args.name:
                console.print("[red]❌ Nom du template requis pour 'info'[/red]")
                return 1
            show_template_info(args.name, args.category)
            
        elif command == "paths":
            show_paths()
            
        elif command in ["help", "--help", "-h"]:
            show_help()
            
        else:
            console.print(f"[red]❌ Commande inconnue: '{command}'[/red]")
            console.print("Utilisez 'cloudya template help' pour voir les commandes disponibles")
            return 1
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Opération interrompue par l'utilisateur[/yellow]")
        return 1
    except Exception as e:
        console.print(f"[red]❌ Erreur inattendue: {e}[/red]")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
