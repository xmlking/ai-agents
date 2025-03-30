import typer
from sumo.utils import another_function

app = typer.Typer()


def return_one():
    return 1


@app.command()
def hello(name: str):
    print(another_function())
    print(f"Hello {name} from script!")


if __name__ == "__main__":
    app()
