import asyncio
import aiofiles
import os
import logging

DIR_FILES = 'files'


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def processar_linha(linha, numero_linha, arquivo_saida):
    async with aiofiles.open(arquivo_saida, 'a', encoding='utf-8') as saida:
        for palavra in linha.strip().split():
            caracteres = ' '.join(caractere for caractere in palavra if caractere.isalnum())  # Filtra apenas alfanuméricos
            await saida.write(f"{caracteres} - {palavra} - linha {numero_linha}\n")

async def processar_arquivo(arquivo):
    nome_arquivo_saida = f"{arquivo[:-4]}-saida.txt"
    caminho_completo_origem = os.path.join(DIR_FILES, arquivo)
    caminho_completo_saida = os.path.join(DIR_FILES, nome_arquivo_saida)

    logging.info(f"Iniciando processamento do arquivo {arquivo}")
   
    async with aiofiles.open(caminho_completo_saida, 'w', encoding='utf-8') as saida:
        await saida.write('') 

    async with aiofiles.open(caminho_completo_origem, 'r', encoding='utf-8') as origem:
        numero_linha = 1
        async for linha in origem:
            await processar_linha(linha, numero_linha, caminho_completo_saida)
            numero_linha += 1
    logging.info(f"Finalizado processamento do arquivo {arquivo}")

async def main():
    if not os.path.isdir(DIR_FILES):
        raise FileNotFoundError(f"O diretório especificado não foi encontrado: {DIR_FILES}")

    tarefas = []
    for arquivo in os.listdir(DIR_FILES):
        if arquivo.endswith('.txt') and not arquivo.endswith('-saida.txt'):
            tarefa = processar_arquivo(arquivo)
            tarefas.append(tarefa)

    await asyncio.gather(*tarefas)

if __name__ == '__main__':
    asyncio.run(main())
