from __future__ import annotations
from semantic_errors import SemanticDiagnostic, SemanticErrorKind
from symbols import FunctionSymbol, Scope, Symbol, SymbolKind
from ast_nodes import Program, Block, Stmt, VarDecl, CallExpr, IdentifierExpr, Expr


def resolve_names(program: Program) -> None:
    """Construa escopos, símbolos e vínculos entre usos e declarações."""

    # 1. Colete todas as assinaturas de função.
    # 2. Valide a existência e a assinatura de main.
    # 3. Percorra os corpos em ordem, criando um escopo para cada bloco.
    # 4. Anote declarações, usos e blocos na AST.
    # 5. Acumule os diagnósticos desta passagem antes de lançar SemanticError.
    raise NotImplementedError("implemente a resolução de nomes")

class NameResolver:
    def __init__(self, program: Program):
        self.program = program
        self.diagnostics: list[SemanticDiagnostic] = []
        self.functions_table: dict[str, FunctionSymbol] = {}
        self.current_scope: Scope | None = None

    def resolve(self):
        self._collect_functions()
        self._resolve_blocks()
    
    def _collect_functions(self):
        for function in self.program.functions:
            param_types = [parameter.type for parameter in function.parameters]
            func_symbol = FunctionSymbol(
                name= function.name, 
                kind= SymbolKind.FUNCTION,
                type= function.return_type, 
                declaration= function,
                parameter_types= param_types
            )
            
            function.metadata["symbol"] = func_symbol

            # Valida a existência de funções duplicadas
            if function.name in self.functions_table:
                self.diagnostics.append(SemanticDiagnostic(
                    SemanticErrorKind.DUPLICATE_FUNCTION,
                    f"Função '{function.name}' ja declarada",
                    function.span
                ))
            else:
                self.functions_table[function.name] = func_symbol

        # Valida a existência e assinatura da função main
        main = self.functions_table.get("main")
        if "main" in self.functions_table:
            if main.type != "int" and len(main.parameter_types) != 0:
                self.diagnostics.append(SemanticDiagnostic(
                    SemanticErrorKind.INVALID_MAIN,
                    f"Função 'main' deve retornar 'int'",
                    main.span
                ))
        else:
            self.diagnostics.append(SemanticDiagnostic(
                SemanticErrorKind.INVALID_MAIN,
                f"Função 'main' não declarada",
                main.span
            ))
        
    def _resolve_blocks(self):
        # for function_name, value in self.functions_table.items():
        for function in self.program.functions:
            function_scope = Scope(parent = None)

            # Valida os parâmetros duplicados
            for param in function.parameters:
                if param.name in function_scope.symbols:
                    self.diagnostics.append(SemanticDiagnostic(
                        SemanticErrorKind.DUPLICATE_DECLARATION,
                        f"Parâmetro '{param.name}' já declarado",
                        param.span
                    ))
                else:
                    param_symbol = Symbol(
                        name= param.name,
                        kind= SymbolKind.PARAMETER,
                        type= param.type,
                        declaration= param
                    )
                    function_scope.symbols[param.name] = param_symbol
                    param.metadata["symbol"] = param_symbol

            # Resolve os blocos da função
            self._resolve_block(function.body, function_scope)
                

    def _resolve_block(self, block: Block, parent_scope: Scope):
        new_scope = Scope(parent= parent_scope)
        block.metadata["scope"] = new_scope

        for stmt in block.statements:
            self._resolve_stmt(stmt, new_scope)
            

        print()
        print()
        
        pass

    def _resolve_stmt(self, stmt: Stmt, scope: Scope):
        # Valida se é um bloco e entra recursivo
        if isinstance(stmt, Block):
            new_scope = Scope(parent=scope)
            self._resolve_block(stmt, new_scope)
            return

        # Valida se ja foi declarada
        if isinstance(stmt, VarDecl):
            if stmt.name in scope.symbols:
                self.diagnostics.append(SemanticDiagnostic(
                    SemanticErrorKind.DUPLICATE_DECLARATION,
                    f"Variavel '{stmt.name}' ja foi declarada no mesmo escopo",
                    stmt.span
                ))
            else:
                var_symbol = Symbol(
                    name=stmt.name,
                    kind=SymbolKind.VARIABLE,
                    type=stmt.type,
                    declaration=stmt
                )
                scope.symbols[stmt.name] = var_symbol
                stmt.metadata["symbol"] = var_symbol

            if getattr(stmt, 'initializer', None):
                self._resolve_expr(stmt.initializer, scope)
            return

    def _resolve_expr(self, expr: Expr, scope: Scope):
        if isinstance(expr, CallExpr):
            function = self.functions_table.get(expr.name)
            if function:
                expr.metadata["symbol"] = function
            else:
                self.diagnostics.append(SemanticDiagnostic(
                    SemanticErrorKind.UNDECLARED_FUNCTION,
                    f"Funcao '{expr.name}' nao foi declarada",
                    expr.span
                ))
                                        
                for arg in expr.arguments:
                    self._resolve_expr(arg, scope)

        elif isinstance(expr, IdentifierExpr):
            found_expr = self._find_expr(expr, scope)
            print(found_expr)
                    
            print(f"Variavel '{expr}' inicializada com identificador '{expr.name}'")


    def _find_expr(self, expr: Expr, scope: Scope):
        symbol_in_scope = scope.symbols.get(expr.name, None)
        while scope is not None:
            if expr.name not in scope.symbols:
                scope = scope.parent
            else:
                symbol_in_scope = scope.symbols.get(expr.name)
                expr.metadata["symbol"] = symbol_in_scope
                break
        
        if not symbol_in_scope:
            self.diagnostics.append(SemanticDiagnostic(
                SemanticErrorKind.UNDECLARED_VARIABLE,
                f"Variavel '{expr.name}' nao foi declarada",
                expr.span
            ))
        return symbol_in_scope