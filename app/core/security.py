
"""Segurança: proteção de senha e tokens de acesso."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.exceptions import TokenInvalido

# O bcrypt só considera os primeiros 72 BYTES da senha (e a versão 5 recusa
# senhas maiores). Em UTF-8 um caractere acentuado ocupa 2 bytes, então o limite
# é conferido em bytes, não em caracteres - ver schemas.UsuarioCreate.
LIMITE_BYTES_SENHA = 72


class HashDeSenha(ABC):
    """Contrato de quem sabe transformar e conferir senhas."""

    @abstractmethod
    def gerar(self, senha: str) -> str:
        """Devolve o hash da senha informada."""

    @abstractmethod
    def verificar(self, senha: str, hash_armazenado: str) -> bool:
        """Confere se a senha corresponde ao hash gravado."""


class HashBcrypt(HashDeSenha):
    """Implementação de produção, baseada no algoritmo bcrypt."""

    def gerar(self, senha: str) -> str:
        senha_bytes = senha.encode("utf-8")
        if len(senha_bytes) > LIMITE_BYTES_SENHA:
            raise ValueError("A senha não pode ultrapassar 72 bytes em UTF-8.")
        return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("ascii")

    def verificar(self, senha: str, hash_armazenado: str) -> bool:
        senha_bytes = senha.encode("utf-8")
        if len(senha_bytes) > LIMITE_BYTES_SENHA:
            # Nenhuma senha cadastrada passa desse tamanho; responder "não confere"
            # é mais seguro do que deixar o bcrypt lançar um erro inesperado.
            return False
        try:
            return bcrypt.checkpw(senha_bytes, hash_armazenado.encode("ascii"))
        except (ValueError, TypeError):
            return False


@dataclass(frozen=True)
class TokenEmitido:
    """Um token de acesso recém-criado e o momento em que deixa de valer."""

    valor: str
    expira_em: datetime


class TokenJWT:
    """Emite e confere tokens JWT assinados com HS256."""

    ALGORITMO = "HS256"

    def __init__(self, segredo: str, expira_minutos: int) -> None:
        if not isinstance(segredo, str) or len(segredo) < 32:
            raise ValueError("O segredo JWT deve ser uma string com pelo menos 32 caracteres.")
        if expira_minutos <= 0:
            raise ValueError("O tempo de expiração do token deve ser maior que zero.")
        self._segredo = segredo
        self._validade = timedelta(minutes=expira_minutos)

    def emitir(self, usuario_id: int, agora: datetime | None = None) -> TokenEmitido:
        """Cria um token válido pelo tempo configurado."""
        expira_em = (agora or datetime.now(timezone.utc)) + self._validade
        conteudo = {"sub": str(usuario_id), "exp": expira_em}
        valor = jwt.encode(conteudo, self._segredo, algorithm=self.ALGORITMO)
        return TokenEmitido(valor=valor, expira_em=expira_em)

    def ler(self, token: str) -> int:
        """Confere assinatura e validade e devolve o id do usuário.

        Raises:
            TokenInvalido: token expirado, adulterado ou malformado.
        """
        try:
            conteudo = jwt.decode(
                token,
                self._segredo,
                algorithms=[self.ALGORITMO],
                options={"require": ["sub", "exp"]},
            )
            return int(conteudo["sub"])
        except jwt.ExpiredSignatureError as erro:
            raise TokenInvalido("Sessão expirada. Entre novamente.") from erro
        except (jwt.InvalidTokenError, ValueError, TypeError) as erro:
            raise TokenInvalido() from erro
