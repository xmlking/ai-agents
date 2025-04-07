import typer
from sumo.utils import another_function

app = typer.Typer()


def return_one():
    return 1


@app.command()
def hello(name: str):
    print(another_function())
    print(f"Hello {name} from script!")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
