import ast
from typing import Any


class FlowDecorator(ast.NodeTransformer):
    def __init__(self, target_name: str):
        self.modified = False
        self.target_name = target_name

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        if not self.modified and node.name == self.target_name:
            self.modified = True
            # Create @flow(log_prints=True) decorator
            flow_decorator = ast.Call(
                func=ast.Name(id="flow", ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg="log_prints", value=ast.Constant(value=True))
                ],
            )
            node.decorator_list.append(flow_decorator)
        return node


def add_flow_decorator(content: str, function_name: str) -> str:
    """Adds @flow decorator to specified function and returns modified content."""
    tree = ast.parse(content)

    # Add import if it doesn't exist
    has_flow_import = any(
        isinstance(node, ast.ImportFrom)
        and node.module == "prefect"
        and any(name.name == "flow" for name in node.names)
        for node in tree.body
    )

    if not has_flow_import:
        import_flow = ast.ImportFrom(
            module="prefect", names=[ast.alias(name="flow", asname=None)], level=0
        )
        tree.body.insert(0, import_flow)

    transformer = FlowDecorator(function_name)
    modified_tree = transformer.visit(tree)

    return ast.unparse(modified_tree)
