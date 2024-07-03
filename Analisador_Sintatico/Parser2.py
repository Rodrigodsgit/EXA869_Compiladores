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
        self.corpo()
        self.expect("DEL")  # }

    def parse_bloco_constantes(self):
        self.expect("PRE")  # constantes
        self.expect("DEL")  # {
        self.expect("DEL")  # }

    def parse_bloco_variaveis(self):
        self.expect("PRE")  # variaveis
        self.expect("DEL")  # {
        self.expect("DEL")  # }

    def parse_bloco_registro(self):
        self.expect("PRE")  # registro
        self.expect("DEL")  # {
        self.expect("DEL")  # }

    def parse_funcao(self):
        self.expect("PRE")  # funcao
        self.expect("DEL")  # {
        self.expect("DEL")  # }

    def parse_funcao_principal(self):
        self.expect("PRE")  # principal
        self.expect("DEL")  # {
        self.expect("DEL")  # }

    def corpo(self):
        expected_blocks = ['constantes', 'variaveis', 'registro', 'funcao', 'principal']
        found_principal = False

        while self.current_token() and not found_principal:
            token = self.current_token()
            if token[2] == 'principal':
                self.parse_funcao_principal()
                expected_blocks.remove('principal')
                found_principal = True
            elif token[2] in expected_blocks:
                if token[2] == 'constantes':
                    self.parse_bloco_constantes()
                elif token[2] == 'variaveis':
                    self.parse_bloco_variaveis()
                elif token[2] == 'registro':
                    self.parse_bloco_registro()
                elif token[2] == 'funcao':
                    self.parse_funcao()
                expected_blocks.remove(token[2])
            else:
                self.errors.append(f"Erro: Na linha {token[0]} esperava-se {' ou '.join(expected_blocks)} e foi encontrado {token[2]}")
                self.advance()  # Avança o token para continuar a análise

        # Verifica se há tokens após o bloco 'principal'
        if found_principal:
            while self.current_token():
                token = self.current_token()
                self.errors.append(f"Erro: Na linha {token[0]} não se esperava nenhum bloco após 'principal', mas encontrado {token[2]}")
                self.advance()

        # Verifica se o bloco 'principal' foi encontrado
        if 'principal' in expected_blocks:
            self.errors.append("Erro: Bloco 'principal' não encontrado, mas é obrigatório.")

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
