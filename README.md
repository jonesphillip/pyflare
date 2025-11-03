# Flare

An experiment in running Python functions at scale on Cloudflare with a single command. Write normal Python, execute across multiple containers in parallel.

![Flare Demo](assets/flare-screenshot.png)

## Quick Start

### 1. Install

```bash
git clone https://github.com/jonesphillip/pyflare
cd flare
./install.sh
```

This installs the `flare` CLI globally.

**Verify:**
```bash
flare --version
```

### 2. Deploy Worker

```bash
cd flare-worker
npm install
npx wrangler deploy
```

Note the Worker URL from the output. See [flare-worker/README.md](flare-worker/README.md) for details.

### 3. Configure

```bash
flare config init
# Enter Worker URL and generate API key
```

Set the API key in your Worker (this authenticates the Python client with your Worker):
```bash
cd flare-worker
echo 'sk_your_generated_key' | npx wrangler secret put API_KEY
```

### 4. Run

```bash
flare run examples/hello.py
```

## Usage

### Basic Function Execution

```python
import flare

app = flare.App("my-app")

@app.function()
def process(x):
    return x * 2

@app.local_entrypoint()
def main():
    result = process.remote(5)
    print(result)  # 10
```

```bash
flare run script.py
```

### Parallel Execution

```python
@app.function(max_containers=10)
def process_item(item):
    return item * 2

@app.local_entrypoint()
def main():
    items = [1, 2, 3, 4, 5]
    results = process_item.map(items)
    print(results)  # [2, 4, 6, 8, 10]
```

See execution details:
```bash
flare run script.py --execution
```

### Timeout Configuration

```python
@app.function(timeout=60)  # 60 second timeout
def slow_task(x):
    import time
    time.sleep(30)
    return x * 2
```

### Environment Variables

```python
import os

@app.function(env={"API_KEY": "secret_value"})
def authenticated_task(x):
    import os
    api_key = os.environ['API_KEY']
    return x * 2

# Load from local environment
@app.function(env={"TOKEN": os.getenv("MY_TOKEN")})
def process(x):
    import os
    token = os.environ['TOKEN']
    return x * 2
```

### CLI Arguments

```python
@app.local_entrypoint()
def main(name: str = "World", count: int = 3):
    for i in range(count):
        result = greet.remote(name)
        print(result)
```

```bash
flare run script.py --name "Alice" --count 5
```

### Direct Function Invocation

```python
@app.function()
def greet(name):
    return f"Hello, {name}!"
```

```bash
flare run examples/hello.py::greet --name "World"
```

## CLI Commands

```bash
# Run scripts
flare run script.py
flare run script.py::function_name --arg value
flare run script.py --execution  # Show execution details

# Configuration
flare config init
flare config show
flare config set-url <url>
flare config set-key <key>

# Help
flare --help
flare run --help
```

## Development

**Install Flare library in your project:**

Add to your `pyproject.toml`:
```toml
[project]
dependencies = [
    "flare @ file:///path/to/flare"
]
```

Then run:
```bash
uv sync
```

**Develop on Flare itself:**

```bash
# Install in development mode
uv sync --all-extras

# Run locally
# Terminal 1: Start worker
cd flare-worker
npm run dev

# Terminal 2: Run examples (in another terminal)
uv run flare run examples/hello.py
```

**Uninstall:**

```bash
uv tool uninstall flare
```
