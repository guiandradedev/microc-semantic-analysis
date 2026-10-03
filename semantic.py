from __future__ import annotations

from ast_nodes import Program
from name_resolver import NameResolver
from type_checker import TypeChecker


class SemanticAnalyzer:
    """Coordena as duas passagens da Análise Semântica 1."""

    def analyze(self, program: Program) -> Program:
        NameResolver(program).resolve()
        TypeChecker(program).check()
        return program
