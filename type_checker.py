from __future__ import annotations

from ast_nodes import Program, Block, FunctionDecl, Stmt, Expr, IntLiteral, BoolLiteral, TypeName
from semantic_errors import SemanticDiagnostic, SemanticError


class TypeChecker:
    """Determine tipos de expressões e valide seus contextos."""
    
    # 1. Use os símbolos anexados pela resolução de nomes.
    # 2. Determine cada expressão de baixo para cima.
    # 3. Valide operadores, chamadas, comandos e declarações.
    # 4. Anote expressões válidas e acumule os diagnósticos da passagem.

    def __init__(self, program: Program):
        self.program = program
        self.diagnostics: list[SemanticDiagnostic] = []

    def check(self):
        for function in self.program.functions:
            self._check_block(function.body, function)

        if self.diagnostics:
            raise SemanticError(self.diagnostics)

    def _check_block(self, block: Block, function: FunctionDecl):
        pass

    def _check_expr(self, expr: Expr):
        if isinstance(expr, IntLiteral):
            expr.metadata["type"] = TypeName.INT
            return TypeName.INT

        if isinstance(expr, BoolLiteral):
            expr.metadata["type"] = TypeName.BOOL
            return TypeName.BOOL
        
        pass

    def _check_stmt(self, stmt: Stmt):
        pass