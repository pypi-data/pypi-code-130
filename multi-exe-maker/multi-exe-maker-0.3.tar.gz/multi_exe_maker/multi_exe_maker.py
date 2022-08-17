import multiprocessing
from multiprocessing import Process
import PySimpleGUI as sg
from pathlib import Path
import time
import requests
import os 

def convert(seconds): 
    """
    Funcao responsavel para calcular o tempo de excecucao do processo
    - seconds: segundos enviados que sera retornado como h:min:seg
    """
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

def gerar_exe( file_name, download_directory):

    print(f"Transformando o arquivo {file_name} para exe\nSalvando no {download_directory}")
    os.system(f'pyinstaller --onefile "{file_name}" --distpath "{download_directory}"')

def layout():

    layout = [
        [sg.Image(data=image_to_data('https://i.ibb.co/t8zxNmx/logo.png'), size=(500,200), background_color='#222526')],

        [sg.Text("Exe Files:", size=(8, 1), background_color='#222526',text_color='White'), 
        sg.Input(key="python_file_in", text_color='white', background_color='#283B5B',disabled=False,size=(46,4)),
        sg.Button(key="python_file",size=(5, 1), border_width=0,image_data=image_to_data('https://i.ibb.co/m9dkDqf/browse-button.png'), button_color='#222526')],

        [sg.Text("Output folder:", size=(9, 1), background_color='#222526',text_color='White'), 
        sg.Input(key="python_file_out_input", text_color='white', background_color='#283B5B',disabled=False,size=(45,4)),
        sg.Button(key="python_file_out",size=(5, 1), border_width=0,image_data=image_to_data('https://i.ibb.co/m9dkDqf/browse-button.png'), button_color='#222526')],


        [sg.Multiline("", size=(68, 15), key='output', autoscroll=True,no_scrollbar=False, enable_events=True,auto_refresh=True, disabled=True, background_color='#283B5B', text_color='white')],

        [sg.Button("", size=(1000,101),disabled_button_color='Black',enable_events=True, key='run', image_data=image_to_data('https://i.ibb.co/wyt21Rr/button-run.png'),  border_width=0)],

    ]

    return layout

def createDir(path):

    """
    Função que cria o diretorio, se ele não existir 
    path: caminho do diretorio que sera criado 
    """
    if os.path.isdir(path):
        #Se não, apenas limpa o diretorio
        print("Diretorio ja existe\nLimpando Diretorio")
        cleanDir(path)
        
    else:
        #Se o dirertorio não existir, cria
        os.mkdir(path)

    return path    

def cleanDir(path):

    """
    Função que limpa todos os arquivos do diretorio selecionado 
    - path: caminho do diretorio que sera limpado por completo
    """
    print("Limpando arquivos gerais")
    if (os.path.exists(path)):
        
        #Loop dentro do diretorio passado
        for file in os.listdir(path):
            
            #Se for apenas arquivo, apaga
            if os.path.isfile(path + '\\' + file):
                os.remove(path + '\\' + file)
                print(file + " removido com sucesso.")

            #Se for um diretorio, chama a função novamente para limpar os arquivos dentro do diretorio 
            elif os.path.isdir(path + '\\' + file):
                cleanDir(path=path + '\\' + file)

def run():
    start = time.time()

    sg.theme('DarkBlue1')
    window = sg.Window("Multi Exe Maker", layout=layout(), background_color='#222526', titlebar_background_color='#222526')

    output = window.find_element('output')

    files = []

    while True:

        event, values = window.read()
        print(event, values)

        if event == 'Exit' or event == sg.WIN_CLOSED:
            break

        if event == 'python_file':
            
            file = sg.popup_get_file('', no_window=True, multiple_files=True) 
            
            window['python_file_in'].update(file)

            files.append(file)
            print("Python File: ", files)

            if(len(files)==1 and type(files[0]) is tuple):
                files = list(files[0])

        if event == 'python_file_out':

            download_path = sg.popup_get_folder('', no_window=True) 
            window['python_file_out_input'].update(download_path)

        #Quando clicar em run
        if event == 'run':
            
            #Pedido para o usuario desligar o spes
            #sg.popup(f"AVISO !\nPara iniciar a processo por favor desligue o serviço de VPN", title='ERRO!',background_color='#222526')

            #criandoAmbienteVirtual(path_download=os.getcwd(), requirements=(relative_to_assets('requirements.txt')))
            
            #Mostrando para o usuario os arquivos que serão transformados em exe
            output.update(f'\n*********** Quantidade de arquivos a serem transformados {len(files)} ***********\n', append = True)
            x = 1
            for file in files:
                output.update(f'\n{x}: {file}\n', append = True)
                x+=1

            output.update("\n\nTransformando os arquivos para exe", append = True)
            processos = []

            
            for file in files:
                p = Process(target=gerar_exe, args=(str(file),download_path,))    
                p.start()
                processos.append(p)
            
            for processo in processos:
                processo.join()

            #Tenpo final do processo
            end = time.time()
            final = end - start
            print(final)
            final = convert(final)
            print(final)
            output.update(f"\n\nOs arquivos criados foram salvos nesse diretório: {download_path}", append = True)
            output.update(f"\n\nProcesso finalizado em: {final}", append = True)
            
            #Zerando os inputs
            window['python_file_in'].update("")
            files = []

def image_to_data(url):
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    return response.raw.read()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    run()
