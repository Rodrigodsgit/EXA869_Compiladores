# Analisador Léxico em Python

Este é um analisador léxico e sintático desenvolvido em Python que identifica tokens em um código fonte.

## Como Executar

### Pré-requisitos

- Python 3.x instalado
- Ambiente virtual (`virtualenv` ou `venv`)

### Instalação

1. Clone o repositório:

```bash
git clone https://github.com/Rodrigodsgit/EXA869_Compiladores
```

2. Crie um ambiente virtual:

Também é possível ignorar esse passo e baixar diretamente na sua máquina, basta pular para o tópico 4. Mas é recomendado utilizar uma virtual env.

Para Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Para Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Navegue até o diretório do projeto:

```bash
cd nome-do-repositorio/Analisador_Sintatico

```

### Execução

1. Coloque os arquivos de entrada na pasta `files`.

2. Execute o arquivo `Parser.py`:

```bash
python Parser.py
```

## Descrição

Este projeto implementa um analisador léxico e sintático em Python, formando as primeiras etapas de um compilador. O analisador léxico identifica e categoriza tokens no código fonte, reconhecendo elementos como palavras-chave, identificadores, números, operadores e delimitadores. O analisador sintático utiliza esses tokens para verificar a estrutura gramatical do código fonte, garantindo que ele siga as regras da linguagem especificada.

O código está estruturado de forma modular, com diferentes funções para processar cada tipo de token e para analisar a estrutura gramatical. Isso facilita a compreensão, manutenção e expansão do projeto.

## Sobre o Projeto

Este projeto é parte da disciplina EXA869 MI COMPILADORES e tem como objetivo implementar um analisador léxico e sintático funcional em Python. A escolha de Python foi motivada por sua simplicidade e expressividade, que permitem um desenvolvimento rápido e eficiente.

### Analisador Léxico

O analisador léxico é responsável por:

- Identificar tokens no código fonte.
- Reconhecer palavras-chave, identificadores, números, operadores aritméticos, operadores lógicos, cadeias de caracteres, e delimitadores.
- Processar cada tipo de token de maneira modular e organizada.

### Analisador Sintático

O analisador sintático é responsável por:

- Ler os tokens gerados pelo analisador léxico.
- Verificar a estrutura gramatical do código fonte.
- Garantir que o código siga as regras da linguagem especificada.

### Execução do Projeto

Ao rodar o arquivo `Parser.py`, o analisador léxico é executado primeiro, gerando tokens a partir do código fonte. Esses tokens são então utilizados pelo analisador sintático para verificar a estrutura do código. Os resultados da análise são exibidos ao final da execução, indicando quaisquer erros encontrados.


## Estrutura do Código

- **Analisador Léxico:** Implementado para identificar e categorizar tokens.
- **Analisador Sintático:** Utiliza os tokens para verificar a estrutura gramatical do código.
- **Parser.py:** Script principal que executa o analisador léxico e depois o sintático.


## Autores

- [Rodrigo Damasceno](https://github.com/Rodrigodsgit)
- [Paulo Queiroz](https://github.com/PauloQueirozC)


