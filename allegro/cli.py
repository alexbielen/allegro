import click


@click.group()
def cli():
    pass


@click.command()
def hello():
    click.echo("Hello! Welcome to Allegro!")


if __name__ == "__main__":
    cli()
