import subprocess
import os

path_to_analisador = os.path.join('..', 'Analisador_Lexico', 'AnalisadorLexico.py')
dir_files = os.path.join('..', 'Analisador_Lexico', 'files')

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []
        self.fechaparetense = '}'
        self.recovered = True


    def current_token(self):
        return self.tokens[self.current_token_index] if self.current_token_index < len(self.tokens) else ('EOF', 'EOF', 'EOF')

    def advance(self):
        self.current_token_index += 1


    def match(self, expected_type, expected_value=None, first=True):
        token = self.current_token()
        if token[1] == expected_type and (expected_value is None or token[2] in expected_value):
            self.advance()
        else:
            if token[0] == 'EOF':
                return
            if first:
                self.errors.append(f"Erro: Na linha {token[0]} esperava-se {expected_value} e foi encontrado {token[2]}")
                self.advance()
                self.match(expected_type, expected_value, False)
            else:
                self.advance()
                self.match( expected_type, expected_value, False)

    def algoritmo(self):
        self.match('PRE', 'algoritmo')
        self.match('DEL', '{')
        self.corpo()
        self.match('DEL', '}')

    def corpo(self):
        block_order = ['constantes', 'variaveis', 'registro', 'funcao', 'principal']
        block_count = {'constantes': 0, 'variaveis': 0, 'registro': 0, 'funcao': 0, 'principal': 0}
        found_principal = False

        while self.current_token()[1] != 'EOF' and not found_principal:
            token = self.current_token()
            block_type = token[2]
            if block_type in block_order:
                if block_type == 'constantes':
                    if block_count['constantes'] == 0 and block_count['variaveis'] == 0 and block_count['registro'] == 0 and block_count['funcao'] == 0:
                        self.bloco_constantes()
                        block_count['constantes'] += 1
                        self.recovered = True
                    else:
                       block_order.remove(block_type)
                elif block_type == 'variaveis':
                    if block_count['variaveis'] == 0 and block_count['registro'] == 0 and block_count['funcao'] == 0:
                        self.bloco_variaveis()
                        block_count['variaveis'] += 1
                        self.recovered = True
                    else:
                        block_order.remove(block_type)
                elif block_type == 'registro':
                    if block_count['registro'] == 0 and block_count['funcao'] == 0:
                        self.bloco_registro()
                        block_count['registro'] += 1
                        self.recovered = True
                    else:
                        block_order.remove(block_type)
                elif block_type == 'funcao':
                    if block_count['principal'] == 0:
                        self.funcao()
                        block_count['funcao'] += 1
                        self.recovered = True
                    else:
                       block_order.remove(block_type)
                elif block_type == 'principal':
                    if block_count['principal'] == 0:
                        self.funcao_principal()
                        block_count['principal'] += 1
                        found_principal = True
                    else:
                       block_order.remove(block_type)
            else:
                if self.recovered:
                    self.errors.append(f"Erro: Na linha {token[0]} esperava-se {' ou '.join(block_order)} e foi encontrado {token[2]}")
                    self.advance()
                    self.recovered = False
                else:
                    self.advance()

        # Verifica se há tokens após o bloco 'principal'
        if found_principal and self.current_token()[2] != '}':
            token = self.current_token()
            if token[0] == 'EOF':
                self.errors.append(f"Erro: Na linha {token[0]} esperava-se '{self.fechaparetense}' e foi encontrado EOF")
                return
            self.errors.append(f"Erro: Na linha {token[0]} não se esperava nenhum bloco após 'principal', mas foi encontrado {token[2]}")
            while self.current_token()[0] != 'EOF' and self.current_token()[2] != '}':
                self.advance()

        # Verifica se o bloco 'principal' foi encontrado
        elif not found_principal:
            self.errors.append("Erro: Bloco 'principal' não encontrado, mas é obrigatório.")

# ------------------------------------------------------------------

    def bloco_constantes(self):
        self.match('PRE', 'constantes')
        self.match('DEL', '{')
        while self.current_token()[2] != '}':
            self.declaracao_de_constante()
        self.match('DEL', '}')

    def declaracao_de_constante(self):
        token = self.current_token()
        if token[2] == 'booleano':
            self.declaracao_booleana()
        elif token[2] in ['inteiro', 'real']:
            self.declaracao_numerica()
        elif token[2] == 'cadeia':
            self.declaracao_de_cadeia()
        elif token[2] == 'char':
            self.declaracao_de_caractere()
        else:
            self.errors.append(f"Erro: Tipo de constante inválido na linha {token[0]} encontrado {token[2]}")
            self.advance()

    def declaracao_booleana(self):
        self.match('PRE', 'booleano')
        self.match('IDE')
        self.match('REL', '=')
        self.expressao_booleana()
        self.listagem_constante_booleana()
        self.match('DEL', ';')

    def listagem_constante_booleana(self):
        while self.current_token()[2] == ',':
            self.advance()
            self.match('IDE')
            self.match('REL', '=')
            self.expressao_booleana()

    def declaracao_numerica(self):
        if self.current_token()[2] == 'inteiro':
            self.match('PRE', 'inteiro')
        else:
            self.match('PRE', 'real')
        self.match('IDE')
        self.match('REL', '=')
        self.expressao_numerica()
        self.listagem_constante_numerica()
        self.match('DEL', ';')

    def listagem_constante_numerica(self):
        while self.current_token()[2] == ',':
            self.advance()
            self.match('IDE')
            self.match('REL', '=')
            self.expressao_numerica()

    def declaracao_de_cadeia(self):
        self.match('PRE', 'cadeia')
        self.match('IDE')
        self.match('REL', '=')
        self.match('CAC')
        self.listagem_constante_de_cadeia()
        self.match('DEL', ';')

    def listagem_constante_de_cadeia(self):
        while self.current_token()[2] == ',':
            self.advance()
            self.match('IDE')
            self.match('REL', '=')
            self.match('CAC')

    def declaracao_de_caractere(self):
        self.match('PRE', 'char')
        self.match('IDE')
        self.match('REL', '=')
        self.match('CAC')
        self.listagem_constante_de_caractere()
        self.match('DEL', ';')

    def listagem_constante_de_caractere(self):
        while self.current_token()[2] == ',':
            self.advance()
            self.match('IDE')
            self.match('REL', '=')
            self.match('CAC')

    def expressao_booleana(self):
        self.expressao_AND()
        self.operacao_OR()

    def operacao_OR(self):
        if self.current_token()[2] == '||':
            self.advance()
            self.expressao_booleana()

    def expressao_AND(self):
        self.expressao_NOT()
        self.operacao_AND()

    def operacao_AND(self):
        if self.current_token()[2] == '&&':
            self.advance()
            self.expressao_AND()

    def expressao_NOT(self):
        if self.current_token()[2] == '!':
            self.advance()
            self.parcela_booleana()
        else:
            self.parcela_booleana()

    def parcela_booleana(self):
        if self.current_token()[2] in ['verdadeiro', 'falso']:
            self.advance()
        elif self.current_token()[1] == 'IDE':
            self.advance()
        elif self.current_token()[2] == '(':
            self.advance()
            self.expressao_booleana()
            self.match('DEL', ')')

    def expressao_numerica(self):
        token = self.current_token()
        self.expressao_MD()
        self.operacao_AS()

    def operacao_AS(self):
        token = self.current_token()
        if self.current_token()[2] in ['+', '-']:
            token = self.current_token()
            self.advance()
            self.expressao_numerica()

    def expressao_MD(self):
        token = self.current_token()
        self.parcela_numerica()
        self.operacao_MD()

    def operacao_MD(self):
        token = self.current_token()
        if self.current_token()[2] in ['*', '/']:
            token = self.current_token()
            self.advance()
            self.expressao_MD()

    def parcela_numerica(self):
        token = self.current_token()
        if self.current_token()[1] in ['NRO', 'IDE']:
            self.advance()
        elif self.current_token()[2] == '(':
            token = self.current_token()
            self.advance()
            self.expressao_numerica()
            self.match('DEL', ')')

# ------------------------------------------------------------------

    def bloco_variaveis(self):
        self.match('PRE', 'variaveis')
        self.match('DEL', '{')
        while self.current_token()[2] != '}':
            self.declaracao_de_variavel()
        self.match('DEL', '}')

    def declaracao_de_variavel(self):
        token = self.current_token()
        tipos = ['booleano', 'inteiro', 'real', 'char', 'cadeia']
        if token[2] in tipos or token[1] == 'IDE':
            self.tipo_variavel()
            self.IDE_vetor()
            self.listagem_de_identificador()
            self.match('DEL', ';')
        else:
            self.errors.append(f"Erro: Tipo de variável inválido na linha {token[0]} encontrado {token[2]}")
            self.advance()

    def tipo_variavel(self):  
        tipos = ['booleano', 'inteiro', 'real', 'char', 'cadeia']
        if self.current_token()[2] in tipos or self.current_token()[1] == 'IDE':
            self.advance()

    def IDE_vetor(self):
        token = self.current_token()
        self.match('IDE')
        token = self.current_token()
        self.vetor()

    def vetor(self):
        token = self.current_token()
        while self.current_token()[2] == '[':
            token = self.current_token()
            self.advance()
            token = self.current_token()
            self.expressao_numerica()
            token = self.current_token()
            self.match('DEL', ']')

    def listagem_de_identificador(self):
        while self.current_token()[2] == ',':
            self.advance()
            self.IDE_vetor()
            
# ------------------------------------------------------------------

    def bloco_registro(self):
        self.match('PRE', 'registro')
        self.match('IDE')
        self.match('DEL', '{')
        self.listagem_bloco_variaveis()
        self.match('DEL', '}')

    def listagem_bloco_variaveis(self):
        while self.current_token()[2] != '}':
            self.declaracao_de_variavel()

# ------------------------------------------------------------------
    def funcao(self):
        self.match('PRE', 'funcao')
        self.tipo_retorno()
        self.match('IDE')
        self.match('DEL', '(')
        self.listagem_declaracao_parametros()
        self.match('DEL', ')')
        self.match('DEL', '{')
        self.escopo()
        self.match('DEL', '}')

    def funcao_principal(self):
        self.match('PRE', 'principal')
        self.match('DEL', '(')
        self.listagem_declaracao_parametros()
        self.match('DEL', ')')
        self.match('DEL', '{')
        self.escopo()
        self.match('DEL', '}')

    def tipo_retorno(self):
        tipos = ['booleano', 'inteiro', 'real', 'char', 'cadeia', 'vazio']
        if self.current_token()[2] in tipos or self.current_token()[1] == 'IDE':
            self.advance()
        else:
            self.errors.append(f"Erro: Tipo de retorno inválido na linha {self.current_token()[0]} encontrado {self.current_token()[2]}")
            self.advance()

    def listagem_declaracao_parametros(self):
        if self.current_token()[2] != ')':
            self.tipo_variavel()
            self.IDE_vetor()
            self.mais_declaracao_parametros()

    def mais_declaracao_parametros(self):
        while self.current_token()[2] == ',':
            self.advance()
            self.tipo_variavel()
            self.IDE_vetor()

    def escopo(self):
        if self.current_token()[2] == 'constantes':
            self.bloco_constantes()
        if self.current_token()[2] == 'variaveis':
            self.bloco_variaveis()
        self.bloco()
        self.retorno()

    def bloco(self):
        while self.current_token()[2] not in ['}', 'retorno']:
            if self.current_token()[2] == 'se':
                self.se()
            elif self.current_token()[2] == 'enquanto':
                self.enquanto()
            elif self.current_token()[2] == 'leia':
                self.leia()
            elif self.current_token()[2] == 'escreva':
                self.escreva()
            elif self.current_token()[1] == 'IDE':
                self.reatribuicao()
            else:
                self.errors.append(f"Erro: Comando inválido na linha {self.current_token()[0]} encontrado {self.current_token()[2]}")
                self.advance()

    def retorno(self):
        if self.current_token()[2] == 'retorno':
            self.match('PRE', 'retorno')
            if self.current_token()[2] != ';':
                self.expressao_geral()
            self.match('DEL', ';')

    def se(self):
        self.match('PRE', 'se')
        self.match('DEL', '(')
        self.expressao_geral()
        self.match('DEL', ')')
        self.match('DEL', '{')
        self.bloco()
        self.match('DEL', '}')
        if self.current_token()[2] == 'senao':
            self.senao()

    def senao(self):
        self.match('PRE', 'senao')
        self.match('DEL', '{')
        self.bloco()
        self.match('DEL', '}')

    def enquanto(self):
        self.match('PRE', 'enquanto')
        self.match('DEL', '(')
        self.expressao_geral()
        self.match('DEL', ')')
        self.match('DEL', '{')
        self.bloco()
        self.match('DEL', '}')

    def leia(self):
        self.match('PRE', 'leia')
        self.match('DEL', '(')
        self.listagem_leia()
        self.match('DEL', ')')
        self.match('DEL', ';')

    def listagem_leia(self):
        self.IDE_vetor()
        self.mais_parametros_leia()

    def mais_parametros_leia(self):
        while self.current_token()[2] == ',':
            self.advance()
            self.IDE_vetor()

    def escreva(self):
        self.match('PRE', 'escreva')
        self.match('DEL', '(')
        self.listagem_parametros()
        self.match('DEL', ')')
        self.match('DEL', ';')

    def listagem_parametros(self):
        if self.current_token()[2] != ')':
            self.expressao_geral()
            self.mais_parametros()

    def mais_parametros(self):
        while self.current_token()[2] == ',':
            self.advance()
            self.expressao_geral()

    def reatribuicao(self):
        self.match('IDE')
        self.reatribuicao_simples_ou_vetor_ou_composto()
        self.match('DEL', ';')

    def reatribuicao_simples_ou_vetor_ou_composto(self):
        while self.current_token()[2] in ['[', '.', '=']:
            if self.current_token()[2] == '[':
                self.advance()
                self.expressao_numerica()
                self.match('DEL', ']')
            elif self.current_token()[2] == '.':
                self.advance()
                self.match('IDE')
            elif self.current_token()[2] == '=':
                self.advance()
                self.expressao_geral()

    def expressao_geral(self):
        self.expressao_AND_geral()
        self.operacao_OR_geral()

    def operacao_OR_geral(self):
        if self.current_token()[2] == '||':
            self.advance()
            self.expressao_geral()

    def expressao_AND_geral(self):
        self.expressao_REL_geral()
        self.operacao_AND_geral()

    def operacao_AND_geral(self):
        if self.current_token()[2] == '&&':
            self.advance()
            self.expressao_AND_geral()

    def expressao_REL_geral(self):
        self.expressao_NOT_geral()
        self.operacao_REL_geral()

    def operacao_REL_geral(self):
        if self.current_token()[2] in ['==', '!=', '>', '<', '>=', '<=']:
            self.advance()
            self.expressao_NOT_geral()

    def expressao_NOT_geral(self):
        if self.current_token()[2] == '!':
            self.advance()
            self.parcela_booleana()
        else:
            self.expressao_AS_geral()

    def expressao_AS_geral(self):
        self.expressao_MD_geral()
        self.operacao_AS_geral()

    def operacao_AS_geral(self):
        if self.current_token()[2] in ['+', '-']:
            self.advance()
            self.expressao_numerica()

    def expressao_MD_geral(self):
        self.parcela_geral()
        self.operacao_MD_geral()

    def operacao_MD_geral(self):
        if self.current_token()[2] in ['*', '/']:
            self.advance()
            self.expressao_MD()

    def parcela_geral(self):
        if self.current_token()[1] in ['IDE', 'NRO', 'CAC']:
            self.advance()
        elif self.current_token()[2] == 'verdadeiro':
            self.advance()
        elif self.current_token()[2] == 'falso':
            self.advance()
        elif self.current_token()[2] == '(':
            self.advance()
            self.expressao_geral()
            self.match('DEL', ')')

# ------------------------------------------------------------------
    def parse(self):
        self.algoritmo()
        if self.errors:
            print("Erros encontrados durante a análise:")
            for error in self.errors:
                print(error)
        else:
            print("Análise concluída com sucesso, sem erros.")


# Exemplo de uso:
tokens = [
    (1, "PRE", "algoritmo"),
    (1, "DEL", "{"),
    (3, "PRE", "funcao"),
    (3, "IDE", "keyregister"),
    (3, "IDE", "nada"),
    (3, "DEL", "("),
    (3, "DEL", ")"),
    (3, "DEL", "{"),
    (4, "PRE", "retorno"),
    (4, "DEL", "("),
    (4, "IDE", "a"),
    (4, "ART", "/"),
    (4, "IDE", "bdadb"),
    (4, "DEL", "["),
    (4, "NRO", "0"),
    (4, "DEL", "]"),
    (4, "DEL", ")"),
    (4, "ART", "-"),
    (4, "IDE", "bdadb"),
    (4, "DEL", "["),
    (4, "NRO", "11"),
    (4, "DEL", "]"),
    (4, "DEL", ";"),
    (5, "DEL", "}"),
    (7, "PRE", "principal"),
    (7, "DEL", "("),
    (7, "DEL", ")"),
    (7, "DEL", "{"),
    (9, "DEL", "}"),
    (10, "DEL", "}"),
    ("Sucesso",)
]

parser = Parser(tokens)
parser.parse()



