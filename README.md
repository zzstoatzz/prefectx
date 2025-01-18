# prefectx

:zap: Deploy your code to Prefect Cloud in seconds! :zap:

## Installation
All you need is `uv`! See [installation docs here](https://docs.astral.sh/uv/getting-started/installation/)
```bash
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Usage
### Login to Prefect Cloud
```bash
$ uvx prefect cloud login
```

### Grab your workflow
Pick a Python file with the function(s) you want to deploy (or use the example below). The function you specify will be automatically converted into a Prefect flow.

```python
$ cat << 'EOF' > example_workflow.py
def get_message():
    return "Hello, World!"

def hello_world():
    print(get_message())

def greet_user(name: str, exclaim: bool = False):
    message = f"Hello, {name}"
    if exclaim:
        message += "!"
    print(message)
EOF
```

### Deploy your code on Prefect Cloud

Specify the file and the function you want to run:
```bash
$ uvx --from git+https://github.com/jakekaplan/prefectx@main prefectx example_workflow.py hello_world
```

Run with parameters:
```bash
$ uvx --from git+https://github.com/jakekaplan/prefectx@main prefectx example_workflow.py greet_user --parameters '{"name": "Alice", "exclaim": true}'
```
