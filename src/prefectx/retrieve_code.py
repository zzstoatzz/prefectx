import sys
import zlib
import base64
from pathlib import Path
from prefect.variables import Variable

def main():
    if len(sys.argv) != 3:
        print("Usage: retrieve_variable.py <variable_name> <output_file>")
        sys.exit(1)

    variable_name = sys.argv[1]
    output_file = sys.argv[2]

    encoded = Variable.get(variable_name)
    if not encoded:
        print(f"No code found in variable {variable_name}")
        sys.exit(1)

    compressed = base64.b64decode(encoded)
    code = zlib.decompress(compressed).decode()

    Path(output_file).write_text(code)
    Variable.unset(variable_name)
    print(f"Successfully wrote code from variable {variable_name} to {output_file}")

if __name__ == "__main__":
    main()