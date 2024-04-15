import re
import asyncio
import aiofiles
import os


# PRE palavra reservada
# IDE identificador
# CAC cadeia de caracteres
# NRO numero
# DEL delimitador 
# REL operador relacional
# LOG operador logico
# ART operador aritmetico

# CMF cadeia mal formada
# CoMF comentário mal formado
# NMF numero mal formado
# IMF identificador mal formado
# TMF token mal formado

TOKENS_REGEX = [
    # ('COMENTARIO_LINHA', r'//.*'),
    # ('COMENTARIO_BLOCO', r'/\*[\s\S]*?\*/'),
    #('PRE', r'\b(algoritmo|principal|variaveis|constantes|registro|funcao|retorno|vazio|se|senao|enquanto|leia|escreva|inteiro|real|booleano|char|cadeia|verdadeiro|falso)\b'),
    #('NRO', r'(-)?\d+(\.\d+)?'),
    # ('ART', r'\+\+|--|\+|-|\*|/'),
    # ('REL', r'!=|==|<=|>=|<|>|='),
    # ('LOG', r'!|&&|\|\|'),
    # ('DEL', r'[;,.()\[\]{}]'),
    #('CAC', r'"[ -!#-~]*"'),  
    #('IDE', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
]

DIR_FILES = 'files'

regex_numero = re.compile(r'^-?\d+(\.\d+)?$')

async def processar_comentarios(linha, posicao, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario, linha_num):
    if dentro_comentario_bloco:
        fim_comentario = linha.find('*/', posicao)
        if fim_comentario != -1:
            # Comentário em bloco fechado corretamente.
            dentro_comentario_bloco = False
            conteudo_comentario += linha[posicao:fim_comentario+2]  # Inclui o fim do comentário.
            return fim_comentario + 2, dentro_comentario_bloco, "", linha_inicio_comentario  # Limpa conteúdo do comentário.
        else:
            # Acumula o conteúdo do comentário se não encontrar o fim.
            conteudo_comentario += linha[posicao:]
            return len(linha), dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario

    # Início de um novo comentário em bloco.
    if not dentro_comentario_bloco and linha[posicao:posicao+2] == '/*':
        linha_inicio_comentario = linha_num  # Armazena a linha onde o comentário em bloco começou.
        comentario_mesma_linha = linha[posicao+2:].find('*/')
        if comentario_mesma_linha != -1:
            conteudo_comentario = linha[posicao+2:posicao+2+comentario_mesma_linha]
            return posicao + 2 + comentario_mesma_linha + 2, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario
        else:
            dentro_comentario_bloco = True
            conteudo_comentario = linha[posicao:]  # Começa a acumular o conteúdo do comentário.
            return len(linha), dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario
    elif not dentro_comentario_bloco and linha[posicao:posicao+2] == '//':
        return len(linha), dentro_comentario_bloco, "", linha_inicio_comentario

    return posicao, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario

async def processar_palavras_reservadas(linha, posicao, saida, linha_num):
    regex_palavras_reservadas = re.compile(r'\b(algoritmo|principal|variaveis|constantes|registro|funcao|retorno|vazio|se|senao|enquanto|leia|escreva|inteiro|real|booleano|char|cadeia|verdadeiro|falso)\b')
    match_palavras_reservadas = regex_palavras_reservadas.match(linha, pos=posicao)
    if match_palavras_reservadas:
        palavra_reservada = match_palavras_reservadas.group(0)
        await saida.write(f"{linha_num} PRE {palavra_reservada}\n")
        posicao += len(palavra_reservada)
    return posicao

async def processar_cadeias(linha: str, posicao: int, saida, linha_num: int, erro_encontrado: bool, lista_erros: list) -> (int, bool):

    inicio_cadeia = posicao
    posicao += 1  
    erro_local = False  
    prox_aspas = linha.find('"', posicao)
    quebra_linha = linha.find('\n', posicao)

    if 0 <= quebra_linha < prox_aspas or prox_aspas == -1:
        posicao = len(linha) if prox_aspas == -1 else quebra_linha
        erro_local = True
        conteudo = linha[inicio_cadeia:posicao]
    else:
        conteudo = linha[inicio_cadeia:prox_aspas+1]
        posicao = prox_aspas + 1  

        if any(ord(c) < 32 or ord(c) > 126 for c in conteudo):
            erro_local = True

    if erro_local:
        lista_erros.append(f"{linha_num} CMF {conteudo}\n")
        erro_encontrado = True  
    else:
        await saida.write(f"{linha_num} CAC {conteudo}\n")

    return posicao, erro_encontrado




async def processar_numeros(linha, posicao, saida, linha_num, erro_encontrado, lista_erros):
    if linha[posicao] == '-' and (posicao + 1 >= len(linha) or not linha[posicao + 1].isdigit() or (posicao > 0 and linha[posicao - 1].isalnum())):
        # Trata caso de hífen que não é parte de um número negativo
        return posicao, erro_encontrado

    inicio_numero = posicao
    posicao += 1
    ponto_ocorrencia = 0
    mal_formado = False
    while posicao < len(linha):
        if (linha[posicao].isdigit() or linha[posicao] == '.' or linha[posicao].isalpha()):
            if linha[posicao] == '.':
                if ponto_ocorrencia == 1:
                    erro_encontrado = True
                    mal_formado = True
                if ponto_ocorrencia == 2:
                    break
                ponto_ocorrencia += 1
        elif  (linha[posicao].isspace() or linha[posicao] in ';,()[]{}+-*/=!&|"\'\n'):
            break
        elif ord(linha[posicao]) < 32 or ord(linha[posicao]) > 126:
            erro_encontrado = True
            mal_formado = True
        posicao += 1

    possivel_numero = linha[inicio_numero:posicao]

    if re.match(r'^-?\d+(\.\d+)?$', possivel_numero) and not mal_formado:
        await saida.write(f"{linha_num} NRO {possivel_numero}\n")
    else:
        lista_erros.append(f"{linha_num} NMF {possivel_numero}\n")
        erro_encontrado = True

    return posicao, erro_encontrado

async def processar_identificadores(linha, posicao, saida, linha_num, erro_encontrado, lista_erros):
    inicio_identificador = posicao
    while posicao < len(linha) and (linha[posicao].isalnum() or linha[posicao] == '_' or linha[posicao] in '&|'):
        # Verifica se & ou | são seguidos por eles mesmos; se não, quebra o loop
        if linha[posicao] in '&|' and  (posicao + 1 < len(linha) and linha[posicao] == linha[posicao + 1]):
            break
        posicao += 1

    possivel_identificador = linha[inicio_identificador:posicao]

    # Verifica se o próximo caractere invalida o identificador
    if posicao < len(linha) and not (linha[posicao].isspace() or linha[posicao] in ';,.()[]{}+-*/=!&|"\'\n'):
        while posicao < len(linha) and not linha[posicao].isspace() and not linha[posicao] in ';,.()[]{}+-*/=!&|"\'\n':
            posicao += 1
        token_malformado = linha[inicio_identificador:posicao]
        lista_erros.append(f"{linha_num} IMF {token_malformado}\n")
        erro_encontrado = True
    elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', possivel_identificador):
        await saida.write(f"{linha_num} IDE {possivel_identificador}\n")
    else:
        lista_erros.append(f"{linha_num} IMF {possivel_identificador}\n")
        erro_encontrado = True

    return posicao, erro_encontrado

async def processar_operadores_aritmeticos(linha, posicao, saida, linha_num):
    if posicao + 1 < len(linha):
        if linha[posicao] == '+' and linha[posicao + 1] == '+':
            await saida.write(f"{linha_num} ART {linha[posicao:posicao+2]}\n")
            posicao += 2
        elif linha[posicao] == '-' and linha[posicao + 1] == '-':
            await saida.write(f"{linha_num} ART {linha[posicao:posicao+2]}\n")
            posicao += 2
        else:
            await saida.write(f"{linha_num} ART {linha[posicao]}\n")
            posicao += 1
    else:
        await saida.write(f"{linha_num} ART {linha[posicao]}\n")
        posicao += 1
    return posicao

async def processar_operadores_logicos(linha, posicao, saida, linha_num, erro_encontrado, lista_erros):
    if posicao + 1 < len(linha):  
        if linha[posicao] == '&' and linha[posicao + 1] == '&':
            await saida.write(f"{linha_num} LOG {linha[posicao:posicao+2]}\n")
            posicao += 2
        elif linha[posicao] == '|' and linha[posicao + 1] == '|':
            await saida.write(f"{linha_num} LOG {linha[posicao:posicao+2]}\n")
            posicao += 2
        elif linha[posicao] == '!' and linha[posicao + 1] != '=':
            await saida.write(f"{linha_num} LOG {linha[posicao]}\n")
            posicao += 1
        elif linha[posicao] == '!' and linha[posicao +1] == '=':
            await saida.write(f"{linha_num} REL {linha[posicao:posicao+2]}\n")
            posicao += 2
        else:
            posicao, erro_encontrado = await token_malformado(linha, posicao, saida, linha_num, erro_encontrado, lista_erros)
    else:
        if linha[posicao] == '!':
            await saida.write(f"{linha_num} LOG {linha[posicao]}\n")
            posicao += 1
        else:
            posicao, erro_encontrado = await token_malformado(linha, posicao, saida, linha_num, erro_encontrado, lista_erros)

    return posicao, erro_encontrado

async def processar_operadores_relacionais(linha, posicao, saida, linha_num):
    if posicao + 1 < len(linha):
        if linha[posicao] == '=' and linha[posicao + 1] == '=':
            await saida.write(f"{linha_num} REL {linha[posicao:posicao+2]}\n")
            posicao += 2
        elif linha[posicao] == '!' and linha[posicao + 1] == '=':
            await saida.write(f"{linha_num} REL {linha[posicao:posicao+2]}\n")
            posicao += 2
        elif linha[posicao] == '<' and linha[posicao + 1] == '=':
            await saida.write(f"{linha_num} REL {linha[posicao:posicao+2]}\n")
            posicao += 2
        elif linha[posicao] == '>' and linha[posicao + 1] == '=':
            await saida.write(f"{linha_num} REL {linha[posicao:posicao+2]}\n")
            posicao += 2
        else:
            await saida.write(f"{linha_num} REL {linha[posicao]}\n")
            posicao += 1
    else:
        await saida.write(f"{linha_num} REL {linha[posicao]}\n")
        posicao += 1

    return posicao

async def processar_delimitadores(linha, posicao, saida, linha_num):
    if re.match( r'[;,.()\[\]{}]', linha[posicao]):
        await saida.write(f"{linha_num} DEL {linha[posicao]}\n")
        posicao += 1
    return posicao

async def token_malformado(linha, posicao,linha_num, erro_encontrado, lista_erros):
    if linha[posicao].isspace():
        return posicao + 1, erro_encontrado
    else:
        lista_erros.append(f"{linha_num} TMF {linha[posicao]}\n")
        return posicao + 1, erro_encontrado
    
async def analisar_lexicamente(caminho_arquivo, caminho_saida):
    async with aiofiles.open(caminho_arquivo, 'r', encoding='utf-8') as arquivo, aiofiles.open(caminho_saida, 'w', encoding='utf-8') as saida:
        dentro_comentario_bloco = False
        conteudo_comentario = ""
        linha_inicio_comentario = None
        linha_num = 1
        erro_encontrado = False
        lista_erros = []
        async for linha in arquivo:
            posicao = 0
            controle = 0
           
            while posicao < len(linha):
                try:  
                    posicao, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario = await processar_comentarios(
                        linha, posicao, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario, linha_num)
                    if not dentro_comentario_bloco:
                        posicao  = await processar_palavras_reservadas(linha, posicao, saida, linha_num)
                    if not dentro_comentario_bloco and linha[posicao] == '"':
                        posicao, erro_encontrado = await processar_cadeias(linha, posicao, saida, linha_num, erro_encontrado, lista_erros)
                        controle = 0
                    if not dentro_comentario_bloco and (linha[posicao].isdigit() or linha[posicao] == '-' ):

                        posicao, erro_encontrado = await processar_numeros(linha, posicao, saida, linha_num, erro_encontrado, lista_erros)
                        controle = 0
                    if not dentro_comentario_bloco and linha[posicao].isalpha() :
                        posicao, erro_encontrado = await processar_identificadores(linha, posicao, saida, linha_num, erro_encontrado, lista_erros)
                        controle = 0
                    if not dentro_comentario_bloco and re.match(r'\+\+|--|\+|-|\*|/', linha[posicao]) and not linha[posicao:posicao+2].isdigit():
                        posicao = await processar_operadores_aritmeticos(linha, posicao, saida, linha_num)
                        controle = 0
                    if not dentro_comentario_bloco and re.match(r'!|&|\|', linha[posicao]):
                        posicao, erro_encontrado = await processar_operadores_logicos(linha, posicao, saida, linha_num, erro_encontrado, lista_erros)
                        controle = 0
                    if not dentro_comentario_bloco and re.match(r'==|!=|<=|>=|<|>|=', linha[posicao]):
                        posicao = await processar_operadores_relacionais(linha, posicao, saida, linha_num)
                        controle = 0
                    if not dentro_comentario_bloco and re.match( r'[;,.()\[\]{}]', linha[posicao]):
                        posicao = await processar_delimitadores(linha, posicao, saida, linha_num)
                        controle = 0
                    if controle == 1:
                        posicao, erro_encontrado = await token_malformado(linha, posicao, linha_num, erro_encontrado, lista_erros)
                    controle = 1
                except IndexError:
                    break
            linha_num += 1

        if dentro_comentario_bloco:
            lista_erros.append(f"{linha_inicio_comentario} CoMF {conteudo_comentario}")
            erro_encontrado = True

        if erro_encontrado:
            await saida.write("\n")
            for erro in lista_erros:
                await saida.write(erro)
        else:
            await saida.write("Sucesso")

async def processar_arquivos():
    tarefas = []
    for arquivo in os.listdir(DIR_FILES):
        if arquivo.endswith('.txt') and not arquivo.endswith('-saida.txt'):
            caminho_completo = os.path.join(DIR_FILES, arquivo)
            caminho_saida = os.path.join(DIR_FILES, f"{arquivo[:-4]}-saida.txt")
            tarefa = analisar_lexicamente(caminho_completo, caminho_saida)
            tarefas.append(tarefa)
    await asyncio.gather(*tarefas)

if __name__ == '__main__':
    asyncio.run(processar_arquivos())
