import typer

app = typer.Typer(help="Commande de test pour dire bonjour")

@app.command()
def world():
    """
    Dit bonjour au monde
    """
    print("Bonjour, monde !")

@app.command()
def user(name: str = typer.Argument(..., help="Votre nom")):
    """
    Dit bonjour à un utilisateur spécifique
    """
    print(f"Bonjour, {name} !")

if __name__ == "__main__":
    app()
