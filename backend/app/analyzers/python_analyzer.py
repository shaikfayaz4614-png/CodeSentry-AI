
import ast


def analyze_python_code(code: str):
    findings = []

    # Parse Python source code
    try:
        tree = ast.parse(code)

    except SyntaxError as error:
        return [{
            "type": "error",
            "severity": "high",
            "message": error.msg,
            "line": error.lineno,
            "suggestion": "Check the syntax near this line and correct the error."
        }]

    def add_finding(issue_type, severity, message, line, suggestion):
        findings.append({
            "type": issue_type,
            "severity": severity,
            "message": message,
            "line": line,
            "suggestion": suggestion
        })

    # Check whether a function validates a collection
    # before dividing by its length.
    def has_empty_collection_guard(function_node, collection_name):

        for node in ast.walk(function_node):

            # Avoid treating nested functions as part of this function.
            if node is not function_node and isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
            ):
                continue

            if not isinstance(node, ast.If):
                continue

            test = node.test

            # Example: if not numbers: return None
            is_empty_check = (
                isinstance(test, ast.UnaryOp)
                and isinstance(test.op, ast.Not)
                and isinstance(test.operand, ast.Name)
                and test.operand.id == collection_name
            )

            if is_empty_check:
                if any(
                    isinstance(statement, (ast.Return, ast.Raise))
                    for statement in node.body
                ):
                    return True

        return False

    # Build parent relationships for AST nodes.
    parents = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    # Analyze syntax tree
    for node in ast.walk(tree):

        # 1. Unsafe eval() and exec()
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec"):
                    add_finding(
                        "security",
                        "high",
                        f"Use of {node.func.id}() can execute untrusted code.",
                        node.lineno,
                        "Avoid eval() or exec(). Use safer alternatives such as "
                        "ast.literal_eval() when parsing Python literals."
                    )

        # 2. Bare except blocks
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                add_finding(
                    "warning",
                    "medium",
                    "Bare except catches all exceptions.",
                    node.lineno,
                    "Catch a specific exception, such as ValueError or TypeError."
                )

        # 3. Division by len()
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Div):
                if isinstance(node.right, ast.Call):
                    if (
                        isinstance(node.right.func, ast.Name)
                        and node.right.func.id == "len"
                        and len(node.right.args) == 1
                        and isinstance(node.right.args[0], ast.Name)
                    ):
                        collection_name = node.right.args[0].id

                        # Find the containing function.
                        parent = parents.get(node)
                        containing_function = None

                        while parent is not None:
                            if isinstance(
                                parent,
                                (ast.FunctionDef, ast.AsyncFunctionDef)
                            ):
                                containing_function = parent
                                break
                            parent = parents.get(parent)

                        # Skip warning if an empty-list guard exists.
                        if not (
                            containing_function
                            and has_empty_collection_guard(
                                containing_function,
                                collection_name
                            )
                        ):
                            add_finding(
                                "bug",
                                "medium",
                                "Potential division by zero when the collection is empty.",
                                node.lineno,
                                "Check that the collection is not empty before "
                                "dividing by its length."
                            )

        # 4. Mutable default arguments
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defaults = node.args.defaults
            positional_args = (
                node.args.posonlyargs + node.args.args
            )

            default_arguments = (
                positional_args[-len(defaults):]
                if defaults else []
            )

            for argument, default in zip(default_arguments, defaults):
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    add_finding(
                        "bug",
                        "medium",
                        f"Mutable default argument '{argument.arg}' "
                        "may be shared between function calls.",
                        default.lineno,
                        "Use None as the default value and create a new "
                        "list, dictionary, or set inside the function."
                    )

    return findings
