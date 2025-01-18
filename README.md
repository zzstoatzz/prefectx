# prefectx

### Make sure `uv` is [installed](https://docs.astral.sh/uv/getting-started/installation/)
```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Login to Prefect Cloud
```
$ uvx prefect cloud login
```

### Create an example workflow
```
$ cat << 'EOF' > hello_workflow.py
def get_message():
    return "Hello, World!"

def hello_world():
    print(get_message())
EOF
```
### Run your workflow on Prefect Cloud
```
$ uvx --from git+https://github.com/jakekaplan/prefectx@main prefectx hello_workflow.py hello
```
