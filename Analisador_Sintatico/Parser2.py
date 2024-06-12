class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []

    def current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        else:
            return None  # Fim dos tokens

    def advance(self):
        self.current_token_index += 1

    def expect(self, expected_token_type):
        token = self.current_token()
        if token and token[1] == expected_token_type:
            self.advance()
        else:
            self.errors.append(f"Erro: Esperado {expected_token_type} na linha {token[0]}, encontrado {token[1]}")

    def parse_algoritmo(self):
        self.expect("PRE")  # algoritmo
        self.expect("DEL")  # {
        self.parse_bloco_constantes()
        self.parse_bloco_variaveis()
        self.parse_funcao_principal()
        self.expect("DEL")  # }

    def parse_bloco_constantes(self):
        token = self.current_token()
        if token and token[2] == "constantes":
            self.expect("PRE")  # constantes
            self.expect("DEL")  # {
            self.expect("DEL")  # }
    
    def parse_bloco_variaveis(self):
        token = self.current_token()
        if token and token[2] == "variaveis":
            self.expect("PRE")  # variaveis
            self.expect("DEL")  # {
            self.expect("DEL")  # }

    def parse_funcao_principal(self):
        token = self.current_token()
        if token and token[2] == "principal":
            self.expect("PRE")  # principal
            self.expect("DEL")  # {
            self.expect("DEL")  # }

    def parse(self):
        self.parse_algoritmo()
        if self.errors:
            print("Erros encontrados durante a análise:")
            for error in self.errors:
                print(error)
        else:
            print("Análise concluída com sucesso, sem erros.")

# Exemplo de uso
tokens = [
    (1, 'PRE', 'algoritmo'), (1, 'DEL', '{'), 
    (2, 'PRE', 'constantes'), (2, 'DEL', '{'), (3, 'DEL', '}'), 
    (4, 'PRE', 'variaveis'), (4, 'DEL', '{'), (5, 'DEL', '}'), 
    (6, 'PRE', 'principal'), (6, 'DEL', '{'), (7, 'DEL', '}'), 
    (8, 'DEL', '}')
]

parser = Parser(tokens)
parser.parse()
