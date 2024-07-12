import subprocess
import os

path_to_analisador = os.path.join('..', 'Analisador_Lexico', 'AnalisadorLexico.py')
dir_files = os.path.join('..', 'Analisador_Lexico', 'files')
dir_files_sintatico = os.path.join(os.path.dirname(__file__), 'files')

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []
        self.fechaparetense = '}'
        self.recovered = True


    def current_token(self):
       token = self.tokens[self.current_token_index] if self.current_token_index < len(self.tokens) else ('EOF', 'EOF', 'EOF')
       return token

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
                if expected_value is None and expected_type == 'IDE':
                    self.errors.append(f"Erro: Na linha {token[0]} esperava-se um 'identificador' e foi encontrado '{token[2]}'")
                elif expected_value is None and expected_type == 'CAC':
                    self.errors.append(f"Erro: Na linha {token[0]} esperava-se uma 'cadeia de carecteres' e foi encontrado '{token[2]}'")
                else:
                    self.errors.append(f"Erro: Na linha {token[0]} esperava-se '{expected_value}' e foi encontrado '{token[2]}'")
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
                        block_order.remove(block_type)
                    else:
                       block_order.remove(block_type)
                elif block_type == 'variaveis':
                    if block_count['variaveis'] == 0 and block_count['registro'] == 0 and block_count['funcao'] == 0:
                        self.bloco_variaveis()
                        block_count['variaveis'] += 1
                        self.recovered = True
                        block_order.remove(block_type)
                    else:
                        block_order.remove(block_type)
                elif block_type == 'registro':
                    if  block_count['funcao'] == 0:
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
                        if block_count['funcao'] == 1:
                            block_order.remove('registro')
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
                    self.errors.append(f"Erro: Na linha {token[0]} esperava-se {' ou '.join(block_order)} e foi encontrado '{token[2]}'")
                    self.recovered = False
                self.advance()

        # Verifica se há tokens após o bloco 'principal'
        if found_principal and self.current_token()[2] != '}':
            token = self.current_token()
            if token[0] == 'EOF':
                self.errors.append(f"Erro: Na linha {token[0]} esperava-se '{self.fechaparetense}' e foi encontrado 'nada'")
                return
            self.errors.append(f"Erro: Na linha {token[0]} esperava-se '{self.fechaparetense}', e foi encontrado '{token[2]}'")
            while self.current_token()[0] != 'EOF' and self.current_token()[2] != '}':
                self.advance()

        # Verifica se o bloco 'principal' foi encontrado
        elif not found_principal:
            self.errors.append(f"Erro: Na linha {self.current_token()[0]} esperava-se 'principal', mas não foi encontrado")

# ------------------------------------------------------------------

    def bloco_constantes(self):
        self.match('PRE', 'constantes')
        self.match('DEL', '{')
        while self.current_token()[2] != '}' and self.current_token()[0] != 'EOF':
            self.declaracao_de_constante()
        self.match('DEL', '}')

    def declaracao_de_constante(self):
        token = self.current_token()
        if token[2] == 'booleano':
            self.declaracao_booleana()
            self.recovered = True
        elif token[2] in ['inteiro', 'real']:
            self.declaracao_numerica()
            self.recovered = True
        elif token[2] == 'cadeia':
            self.declaracao_de_cadeia()
            self.recovered = True
        elif token[2] == 'char':
            self.declaracao_de_caractere()
            self.recovered = True
        else:
            if self.recovered:
                self.errors.append(f"Erro: Na linha {token[0]} esperava-se 'booleano', 'inteiro', 'real', 'cadeia' ou 'char' e foi encontrado '{token[2]}'")
                self.recovered = False
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
        else:
            self.errors.append(f"Erro: Na linha {self.current_token()[0]} esperava-se 'verdadeiro', 'falso', 'identificador' ou '(' e foi encontrado 'nada'")

    def expressao_numerica(self):
        self.current_token()
        self.expressao_MD()
        self.operacao_AS()

    def operacao_AS(self):
        self.current_token()
        if self.current_token()[2] in ['+', '-']:
            op = self.current_token()[2]
            self.advance()
            self.expressao_numerica()

    def expressao_MD(self):
        self.current_token()
        self.parcela_numerica()
        self.operacao_MD()

    def operacao_MD(self):
        self.current_token()
        if self.current_token()[2] in ['*', '/']:
            op = self.current_token()[2]
            self.advance()
            self.expressao_MD()

    def parcela_numerica(self):
        self.current_token()
        if self.current_token()[1] in ['NRO', 'IDE']:
            self.advance()
        elif self.current_token()[2] == '(':
            self.advance()
            self.expressao_numerica()
            self.match('DEL', ')')
        else:
            self.errors.append(f"Erro: Na linha {self.current_token()[0]} esperava-se um 'identificador', 'numero' ou '(' e foi encontrado 'nada'")

# ------------------------------------------------------------------

    def bloco_variaveis(self):
        self.match('PRE', 'variaveis')
        self.match('DEL', '{')
        while self.current_token()[2] != '}' and self.current_token()[0] != 'EOF':
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
            self.recovered = True
        else:
            if self.recovered:
                self.errors.append(f"Erro: Na linha {token[0]} esperado 'booleano', 'inteiro', 'real', 'char' ou 'cadeia' encontrado '{token[2]}'")
                self.recovered = False
            self.advance()

    def tipo_variavel(self):
        tipos = ['booleano', 'inteiro', 'real', 'char', 'cadeia']
        if self.current_token()[2] in tipos or self.current_token()[1] == 'IDE':
            self.advance()

    def IDE_vetor(self):
        self.match('IDE')
        self.vetor()

    def vetor(self):
        while self.current_token()[2] == '[':
            self.advance()
            self.expressao_numerica()
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
        while self.current_token()[2] != '}' and self.current_token()[0] != 'EOF':
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
            self.recovered = True
        else:
            if self.recovered:
                self.errors.append(f"Erro: Na linha {self.current_token()[0]} esperado 'booleano', 'inteiro', 'real', 'char' ou 'cadeia' encontrado {self.current_token()[2]}")
                self.recovered = False
            if self.current_token()[0] != 'EOF':
                self.advance()
                self.tipo_retorno()

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
        while self.current_token()[2] not in ['}', 'retorno'] and self.current_token()[0] != 'EOF':
            if self.current_token()[2] == 'se':
                self.se()
                self.recovered = True
            elif self.current_token()[2] == 'enquanto':
                self.enquanto()
                self.recovered = True
            elif self.current_token()[2] == 'leia':
                self.leia()
                self.recovered = True
            elif self.current_token()[2] == 'escreva':
                self.escreva()
                self.recovered = True
            elif self.current_token()[1] == 'IDE':
                self.reatribuicao()
                self.recovered = True
            else:
                if self.recovered:
                    self.errors.append(f"Erro: Na linha {self.current_token()[0]} esperado 'se', 'enquanto', 'leia', 'escreva' ou 'identificadores' encontrado '{self.current_token()[2]}'")
                    self.recovered = False
                self.advance()

    def retorno(self):
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
        self.IDE_vetor_ou_composto_ou_chamada()
        self.mais_parametros_leia()

    def mais_parametros_leia(self):
        while self.current_token()[2] == ',':
            self.advance()
            self.IDE_vetor_ou_composto_ou_chamada()

    def IDE_vetor_ou_composto_ou_chamada(self):
        self.match('IDE')
        self.vetor_ou_composto_ou_chamada()

    def vetor_ou_composto_ou_chamada(self):
        while self.current_token()[2] in ['[', '.', '(']:
            if self.current_token()[2] == '[':
                self.advance()
                self.expressao_numerica()
                self.match('DEL', ']')
            elif self.current_token()[2] == '.':
                self.advance()
                self.match('IDE')
            elif self.current_token()[2] == '(':
                self.advance()
                self.listagem_parametros()
                self.match('DEL', ')')

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
        else: 
            if self.current_token()[1] != 'LOG':
                self.errors.append(f"Erro: Na linha {self.current_token()[0]} esperava-se identificados, numero, cadeia de carecteres, verdadeiro, falso, ou ( e foi encontrado nada " )

# ------------------------------------------------------------------
    def parse(self, caminho_saida):
        self.algoritmo()
        with open(caminho_saida, 'w') as file:
            if self.errors:                    
                    for error in self.errors:
                        file.write(error + '\n')
            else:
               file.write("Sucesso")

def executar_analisador_lexico():
    try:
        result = subprocess.run(['python', path_to_analisador], check=True, capture_output=True, text=True)
        print("Saída do Analisador Lexico:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erro ao executar o Analisador Lexico:", e.stderr)

executar_analisador_lexico()

def ler_arquivos_saida(dir_files):
    for arquivo in os.listdir(dir_files):
        lista_tuplas = []
        if arquivo.endswith('-saida.txt'):
            caminho_arquivo = os.path.join(dir_files, arquivo)
            with open(caminho_arquivo, 'r') as file:
                linhas = file.readlines()
                for linha in linhas:
                    linha = linha.strip()  
                    if linha and linha != "Sucesso": 
                        tupla = tuple(linha.split())
                        lista_tuplas.append(tupla)

            caminho_saida = os.path.join(dir_files_sintatico, f"{arquivo[:-4]}-sintatico.txt")
            parser = Parser(lista_tuplas)
            parser.parse(caminho_saida)


ler_arquivos_saida(dir_files)