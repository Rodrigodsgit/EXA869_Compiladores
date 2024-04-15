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

TOKENS_ERROS = re.compile(r'\b(IMF|NMF|CMF|TMF)\b')

async def processar_comentarios(linha, posicao, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario, linha_num):
    if dentro_comentario_bloco:
        fim_comentario = linha.find('*/', posicao)
        if fim_comentario != -1:
            dentro_comentario_bloco = False
            conteudo_comentario += linha[posicao:fim_comentario+2] 
            return fim_comentario + 2, dentro_comentario_bloco, "", linha_inicio_comentario  
        else:
            conteudo_comentario += linha[posicao:]
            return len(linha), dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario

    if not dentro_comentario_bloco and linha[posicao:posicao+2] == '/*':
        linha_inicio_comentario = linha_num  
        comentario_mesma_linha = linha[posicao+2:].find('*/')
        if comentario_mesma_linha != -1:
            conteudo_comentario = linha[posicao+2:posicao+2+comentario_mesma_linha]
            return posicao + 2 + comentario_mesma_linha + 2, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario
        else:
            dentro_comentario_bloco = True
            conteudo_comentario = linha[posicao:]  
            return len(linha), dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario
    elif not dentro_comentario_bloco and linha[posicao:posicao+2] == '//':
        return len(linha), dentro_comentario_bloco, "", linha_inicio_comentario

    return posicao, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario

async def processar_palavras_reservadas(linha, posicao, saida, linha_num, token_atual):
    regex_palavras_reservadas = re.compile(r'\b(algoritmo|principal|variaveis|constantes|registro|funcao|retorno|vazio|se|senao|enquanto|leia|escreva|inteiro|real|booleano|char|cadeia|verdadeiro|falso)\b')
    match_palavras_reservadas = regex_palavras_reservadas.match(linha, pos=posicao)
    if match_palavras_reservadas:
        palavra_reservada = match_palavras_reservadas.group(0)
        await saida.write(f"{linha_num} PRE {palavra_reservada}\n")
        token_atual = "PRE"
        posicao += len(palavra_reservada)
    return posicao, token_atual

async def processar_cadeias(linha, posicao, saida, linha_num, erro_encontrado, lista_erros, token_atual):
    inicio_cadeia = posicao
    posicao += 1
    ascci_out = False
    while posicao < len(linha) and linha[posicao] != '"':
        if ord(linha[posicao]) < 32 or ord(linha[posicao]) > 126:
            ascci_out = True
            erro_encontrado = True
        if linha[posicao] == '\n':
            erro_encontrado = True
            break
        posicao += 1

    try:
        if linha[posicao] != '"' or ascci_out:  
            if linha[posicao] == '"':
                lista_erros.append(f"{linha_num} CMF {linha[inicio_cadeia:posicao+1]}\n")
                token_atual = "CMF"
                posicao += 1
            else:
                lista_erros.append(f"{linha_num} CMF {linha[inicio_cadeia:posicao]}\n")
                token_atual = "CMF"
            erro_encontrado = True
        else:
            await saida.write(f"{linha_num} CAC {linha[inicio_cadeia:posicao+1]}\n")
            token_atual = "CAC"
            posicao += 1

    except IndexError:
        await lista_erros.append(f"{linha_num} CMF {linha[inicio_cadeia:posicao]}\n")
        token_atual = "CMF"
        erro_encontrado = True

    return posicao, erro_encontrado, token_atual

async def processar_numeros(linha, posicao, saida, linha_num, erro_encontrado, lista_erros, token_atual):
    if  linha[posicao] == '-' :
        if  posicao + 1 < len(linha):    
            if linha[posicao + 1].isdigit():
                if not posicao == 0:
                    if linha[posicao - 1].isalnum() or token_atual == "IDE" or token_atual == "NRO":
                        return posicao, erro_encontrado, token_atual
            else:
                return posicao, erro_encontrado, token_atual
        else:
            return posicao, erro_encontrado, token_atual

    inicio_numero = posicao
    posicao += 1
    ponto_ocorrencia = 0
    mal_formado = False
    while posicao < len(linha):
        if (linha[posicao].isdigit() or linha[posicao] == '.' or linha[posicao].isalpha()):
            if linha[posicao] == '.':
                if ponto_ocorrencia == 0 and posicao + 1 < len(linha) and not linha[posicao + 1].isdigit():
                    erro_encontrado = True
                    mal_formado = True
                    posicao += 1
                elif ponto_ocorrencia == 1:
                    if not re.match(r'^-?\d+(\.\d+)?$',linha[inicio_numero:posicao]):
                        break
                    else:
                        erro_encontrado = True
                        mal_formado = True
                elif ponto_ocorrencia == 2:
                    break
                ponto_ocorrencia += 1
        elif  (linha[posicao].isspace() or (linha[posicao] in ';,()[]{}+-*/=!&|"\'\n')):
            if posicao + 1 < len(linha):
                if (linha[posicao] == "&" and linha[posicao +1] == "&") or (linha[posicao] == "|" and linha[posicao +1] == "|"):
                    break
                elif (linha[posicao] == "&" and linha[posicao +1] != "&") or (linha[posicao] == "|" and linha[posicao +1] != "|"):
                    erro_encontrado = True
                    mal_formado = True
                else:
                    break

        elif ord(linha[posicao]) < 32 or ord(linha[posicao]) > 126:
            erro_encontrado = True
            mal_formado = True
        posicao += 1

    possivel_numero = linha[inicio_numero:posicao]

    if re.match(r'^-?\d+(\.\d+)?$', possivel_numero) and not mal_formado:
        possivel_numero = possivel_numero.replace("\n", "")
        await saida.write(f"{linha_num} NRO {possivel_numero}\n")
        token_atual = "NRO"
    else:
        possivel_numero = possivel_numero.replace("\n", "")
        lista_erros.append(f"{linha_num} NMF {possivel_numero}\n")
        token_atual = "NMF"
        erro_encontrado = True

    return posicao, erro_encontrado, token_atual

async def processar_identificadores(linha, posicao, saida, linha_num, erro_encontrado, lista_erros, token_atual):
    inicio_identificador = posicao
    while posicao < len(linha) and (linha[posicao].isalnum() or linha[posicao] == '_' or linha[posicao] in '&|'):
        if linha[posicao] in '&|' and  (posicao + 1 < len(linha) and linha[posicao] == linha[posicao + 1]):
            break
        posicao += 1

    possivel_identificador = linha[inicio_identificador:posicao]

    if posicao < len(linha) and not (linha[posicao].isspace() or linha[posicao] in ';,.()[]{}+-*/=!&|"\'\n'):
        while posicao < len(linha) and not linha[posicao].isspace() and not linha[posicao] in ';,.()[]{}+-*/=!&|"\'\n':
            posicao += 1
        token_malformado = linha[inicio_identificador:posicao]
        lista_erros.append(f"{linha_num} IMF {token_malformado}\n")
        token_atual = "IMF"
        erro_encontrado = True
    elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', possivel_identificador):
        await saida.write(f"{linha_num} IDE {possivel_identificador}\n")
        token_atual = "IDE"
    else:
        lista_erros.append(f"{linha_num} IMF {possivel_identificador}\n")
        token_atual = "IMF"
        erro_encontrado = True

    return posicao, erro_encontrado, token_atual

async def processar_operadores_aritmeticos(linha, posicao, saida, linha_num, token_atual):
    if posicao + 1 < len(linha):
        if linha[posicao] == '+' and linha[posicao + 1] == '+':
            await saida.write(f"{linha_num} ART {linha[posicao:posicao+2]}\n")
            posicao += 2
        elif linha[posicao] == '-' and linha[posicao + 1] == '-':
            await saida.write(f"{linha_num} ART {linha[posicao:posicao+2]}\n")
            posicao += 2
        else:
            if linha[posicao] == '-':
                if not (TOKENS_ERROS.match(token_atual) and linha[posicao + 1].isdigit()):
                    await saida.write(f"{linha_num} ART {linha[posicao]}\n")
                    posicao += 1
                else:
                    return posicao, token_atual
            else:
                await saida.write(f"{linha_num} ART {linha[posicao]}\n")
                posicao += 1
    else:
        await saida.write(f"{linha_num} ART {linha[posicao]}\n")
        posicao += 1
    token_atual = "ART"
    return posicao, token_atual

async def processar_operadores_logicos(linha, posicao, saida, linha_num, erro_encontrado, lista_erros, token_atual):
    if posicao + 1 < len(linha):  
        if linha[posicao] == '&' and linha[posicao + 1] == '&':
            await saida.write(f"{linha_num} LOG {linha[posicao:posicao+2]}\n")
            token_atual = "LOG"
            posicao += 2
        elif linha[posicao] == '|' and linha[posicao + 1] == '|':
            await saida.write(f"{linha_num} LOG {linha[posicao:posicao+2]}\n")
            token_atual = "LOG"
            posicao += 2
        elif linha[posicao] == '!' and linha[posicao + 1] != '=':
            await saida.write(f"{linha_num} LOG {linha[posicao]}\n")
            token_atual = "LOG"
            posicao += 1
        elif linha[posicao] == '!' and linha[posicao +1] == '=':
            await saida.write(f"{linha_num} REL {linha[posicao:posicao+2]}\n")
            token_atual = "REL"
            posicao += 2
        else:
            posicao, erro_encontrado = await token_malformado(linha, posicao, linha_num, erro_encontrado, lista_erros)
    else:
        if linha[posicao] == '!':
            await saida.write(f"{linha_num} LOG {linha[posicao]}\n")
            token_atual = "LOG"
            posicao += 1
        else:
            posicao, erro_encontrado = await token_malformado(linha, posicao, linha_num, erro_encontrado, lista_erros, token_atual)

    return posicao, erro_encontrado, token_atual

async def processar_operadores_relacionais(linha, posicao, saida, linha_num, token_atual):
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

    token_atual = "REL"
    return posicao, token_atual

async def processar_delimitadores(linha, posicao, saida, linha_num, token_atual):
    if re.match( r'[;,.()\[\]{}]', linha[posicao]):
        await saida.write(f"{linha_num} DEL {linha[posicao]}\n")
        token_atual = "DEL"
        posicao += 1
    return posicao, token_atual

async def token_malformado(linha, posicao,linha_num, erro_encontrado, lista_erros, token_atual):
    if linha[posicao].isspace():
        return posicao + 1, erro_encontrado, token_atual
    else:
        lista_erros.append(f"{linha_num} TMF {linha[posicao]}\n")
        token_atual = "TMF"
        return posicao + 1, True, token_atual
    
async def analisar_lexicamente(caminho_arquivo, caminho_saida):
    async with aiofiles.open(caminho_arquivo, 'r', encoding='utf-8') as arquivo, aiofiles.open(caminho_saida, 'w', encoding='utf-8') as saida:
        dentro_comentario_bloco = False
        conteudo_comentario = ""
        linha_inicio_comentario = None
        linha_num = 1
        erro_encontrado = False
        lista_erros = []
        token_atual = ""
        async for linha in arquivo:
            posicao = 0
            controle = 0
           
            while posicao < len(linha):
                try:  
                    posicao, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario = await processar_comentarios(
                        linha, posicao, dentro_comentario_bloco, conteudo_comentario, linha_inicio_comentario, linha_num)
                    if not dentro_comentario_bloco:
                        posicao, token_atual  = await processar_palavras_reservadas(linha, posicao, saida, linha_num, token_atual)
                    if not dentro_comentario_bloco and linha[posicao] == '"':
                        posicao, erro_encontrado, token_atual = await processar_cadeias(linha, posicao, saida, linha_num, erro_encontrado, lista_erros, token_atual)
                        controle = 0
                    if not dentro_comentario_bloco and (linha[posicao].isdigit() or linha[posicao] == '-' ):
                        posicao, erro_encontrado, token_atual = await processar_numeros(linha, posicao, saida, linha_num, erro_encontrado, lista_erros, token_atual)
                        controle = 0
                    if not dentro_comentario_bloco and linha[posicao].isalpha() :
                        posicao, erro_encontrado, token_atual = await processar_identificadores(linha, posicao, saida, linha_num, erro_encontrado, lista_erros, token_atual)
                        controle = 0
                    if not dentro_comentario_bloco and re.match(r'\+\+|--|\+|-|\*|/', linha[posicao]) and not linha[posicao:posicao+2].isdigit():
                        posicao, token_atual = await processar_operadores_aritmeticos(linha, posicao, saida, linha_num, token_atual)
                        controle = 0
                    if not dentro_comentario_bloco and re.match(r'!|&|\|', linha[posicao]):
                        posicao, erro_encontrado, token_atual = await processar_operadores_logicos(linha, posicao, saida, linha_num, erro_encontrado, lista_erros, token_atual)
                        controle = 0
                    if not dentro_comentario_bloco and re.match(r'==|!=|<=|>=|<|>|=', linha[posicao]):
                        posicao, token_atual = await processar_operadores_relacionais(linha, posicao, saida, linha_num, token_atual)
                        controle = 0
                    if not dentro_comentario_bloco and re.match( r'[;,.()\[\]{}]', linha[posicao]):
                        posicao, token_atual = await processar_delimitadores(linha, posicao, saida, linha_num, token_atual)
                        controle = 0
                    if controle == 1:
                        posicao, erro_encontrado, token_atual = await token_malformado(linha, posicao, linha_num, erro_encontrado, lista_erros, token_atual)
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
