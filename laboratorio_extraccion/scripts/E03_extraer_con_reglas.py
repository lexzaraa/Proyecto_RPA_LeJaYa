from comun import RAIZ, CASOS, guardar, extraer_reglas, sobre

def main():
    for caso in CASOS:
        texto = (RAIZ/'salidas'/'ocr'/f'{caso}.txt').read_text(encoding='utf-8')
        resultado = sobre(caso, 'reglas', 'real', extraer_reglas(texto))
        guardar(RAIZ/'salidas'/'reglas'/f'{caso}.json', resultado)
        print(caso, resultado['datos'])

if __name__ == '__main__':
    main()
