class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []

    def current_token(self):
        return self.tokens[self.current_token_index] if self.current_token_index < len(self.tokens) else ('EOF', 'EOF', 'EOF')

    def advance(self):
        self.current_token_index += 1

    def match(self, expected_type, expected_value=None, first=True):
        token = self.current_token()
        if token[1] == expected_type and (expected_value is None or token[2] in expected_value):
            self.advance()
        else:
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


        if self.current_token()[2] == 'constantes':
            self.blocode_constantes()
        if self.current_token()[2] == 'variaveis':
            self.blocode_variaveis()
        if self.current_token()[2] == 'registro':
            self.bloco_registro
        if self.current_token()[2] == 'funcao':
            self.funcao()
        if self.current_token()[2] == 'principal':
            self.funcaoprincipal()
        else:
            pass

    def blocode_constantes(self):
        self.match('PRE', 'constantes')
        self.match('DEL', '{')
        while self.current_token()[2] != '}':
            # Implementar a análise das declarações de constantes aqui
            pass
        self.match('DEL', '}')

    def blocode_variaveis(self):
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

# Exemplo de uso:
tokens = [
    (1, 'PRE', 'algoritmo'), 
    (1, 'DEL', '{'), 
    (2, 'PRE', 'constantes'), 
    (2, 'DEL', '{'), 
    (2, 'DEL', '}'), 
    (3, 'PRE', 'variaveis'), 
    (3, 'DEL', '{'), 
    (3, 'DEL', '}'), 
    (4, 'PRE', 'principal'), 
    (4, 'DEL', '{'), 
    (4, 'DEL', '}'), 
    (5, 'DEL', '}')
]


parser = Parser(tokens)
parser.parse()
