

"""The main entry point for the webapp."""


from flask import Flask


app = Flask(__name__)


@app.route('/')
def main():
    """The root page."""
    return "It's alive!"


if __name__ == '__main__':
    main()
