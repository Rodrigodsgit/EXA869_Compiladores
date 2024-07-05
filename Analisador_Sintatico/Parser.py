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
        expected_blocks = ['constantes', 'variaveis', 'registro', 'funcao', 'principal']
        found_principal = False

        while self.current_token() != 'EOF' and not found_principal:
            token = self.current_token()
            if token[2] == 'principal':
                self.funcao_principal()
                expected_blocks.remove('principal')
                found_principal = True
            elif token[2] in expected_blocks:
                if token[2] == 'constantes':
                    self.bloco_constantes()
                elif token[2] == 'variaveis':
                    self.bloco_variaveis()
                elif token[2] == 'registro':
                    self.bloco_registro()
                elif token[2] == 'funcao':
                    self.funcao()
                expected_blocks.remove(token[2])
            else:
                self.errors.append(f"Erro: Na linha {token[0]} esperava-se {' ou '.join(expected_blocks)} e foi encontrado {token[2]}")
                self.advance()  # 

        # Verifica se há tokens após o bloco 'principal'
        if found_principal and self.current_token()[2] != '}':
            token = self.current_token()
            if token[0] == 'EOF':
                self.errors.append(f"Erro: Na linha {token[0]} esperava-se '{self.fechaparetense}'e foi encontrado EOF")
                return
            self.errors.append(f"Erro: Na linha {token[0]} não se esperava nenhum bloco após 'principal', mas encontrado {token[2]}")
            while (self.current_token()[0] != 'EOF') and (self.current_token()[2] != '}'):  
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
        self.expressao_MD()
        self.operacao_AS()

    def operacao_AS(self):
        if self.current_token()[2] in ['+', '-']:
            op = self.current_token()[2]
            self.advance()
            self.expressao_numerica()

    def expressao_MD(self):
        self.parcela_numerica()
        self.operacao_MD()

    def operacao_MD(self):
        if self.current_token()[2] in ['*', '/']:
            op = self.current_token()[2]
            self.advance()
            self.expressao_MD()

    def parcela_numerica(self):
        if self.current_token()[1] in ['NRO', 'IDE']:
            self.advance()
        elif self.current_token()[2] == '(':
            self.advance()
            self.expressao_numerica()
            self.match('DEL', ')')

# ------------------------------------------------------------------

    def bloco_variaveis(self):
        self.match('PRE', 'variaveis')
        self.match('DEL', '{')
        while self.current_token()[2] != '}':
            # Implementar a análise das declarações de variáveis aqui
            pass
        self.match('DEL', '}')

    def bloco_registro(self):
        self.match('PRE', 'registro')
        self.match('DEL', '{')
        while self.current_token()[2] != '}':
            # Implementar a analise do corpo do bloco de registro aqui
            pass
        self.match('DEL', '}')

    def funcao(self):
        self.match('PRE', 'funcao')
        self.match('DEL', '{')
        # Implementar a analise do corpo da função aqui
        self.match('DEL', '}')

    def funcao_principal(self):
        self.match('PRE', 'principal')
        self.match('DEL', '{')
        # Implementar a análise do corpo da função principal aqui
        self.match('DEL', '}')

    def parse(self):
        self.algoritmo()
        if self.errors:
            print("Erros encontrados durante a análise:")
            for error in self.errors:
                print(error)
        else:
            print("Análise concluída com sucesso, sem erros.")


def executar_analisador_lexico():
    try:
        result = subprocess.run(['python', path_to_analisador], check=True, capture_output=True, text=True)
        print("Saída do Analisador Lexico:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erro ao executar o Analisador Lexico:", e.stderr)

executar_analisador_lexico()

def ler_arquivos_saida(dir_files):
    lista_tuplas = []
    for arquivo in os.listdir(dir_files):
        if arquivo.endswith('-saida.txt'):
            caminho_arquivo = os.path.join(dir_files, arquivo)
            with open(caminho_arquivo, 'r') as file:
                linhas = file.readlines()
                for linha in linhas:
                    linha = linha.strip()  
                    if linha and linha != "Sucesso": 
                        tupla = tuple(linha.split())
                        lista_tuplas.append(tupla)
            parser = Parser(lista_tuplas)
            parser.parse()


ler_arquivos_saida(dir_files)