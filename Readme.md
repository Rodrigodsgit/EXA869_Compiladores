# Analisador Léxico em Python

Este é um analisador léxico desenvolvido em Python que identifica tokens em um código fonte.

## Como Executar

### Pré-requisitos

- Python 3.x instalado
- Ambiente virtual (`virtualenv` ou `venv`)

### Instalação

1. Clone o repositório:

```bash
git clone https://github.com/Rodrigodsgit/EXA869_Compiladores
```

2. Navegue até o diretório do projeto:

```bash
cd nome-do-repositorio/PBL01
```

3. Crie um ambiente virtual:

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

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

### Execução

1. Coloque os arquivos de entrada na pasta `files`.

2. Execute o arquivo `AnalisadorLexico.py`:

```bash
python AnalisadorLexico.py
```

## Descrição

O analisador léxico é a primeira etapa de um compilador, responsável por identificar tokens no código fonte. Ele reconhece palavras-chave, identificadores, números, operadores e delimitadores, entre outros elementos da linguagem.

Este analisador léxico foi implementado em Python e segue uma abordagem modular, com diferentes funções para processar cada tipo de token. O código está estruturado de forma organizada, facilitando a compreensão e manutenção.

## Sobre o Projeto

Este projeto faz parte de uma disciplina de EXA869 MI COMPILADORES e tem como objetivo implementar um analisador léxico funcional em Python. A escolha da linguagem Python foi feita devido à sua simplicidade e expressividade, o que permite um desenvolvimento rápido e eficiente.

O analisador léxico aqui desenvolvido é capaz de lidar com uma variedade de construções da linguagem, incluindo operadores aritméticos, operadores lógicos, cadeias de caracteres, números, palavras-chave e delimitadores.

## Autores

- [Rodrigo Damasceno](https://github.com/Rodrigodsgit)
- [Paulo Queiroz](https://github.com/PauloQueirozC)


