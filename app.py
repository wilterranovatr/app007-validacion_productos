import sys
import argparse
from modules.modulo1 import Modulo1
from modules.modulo2 import Modulo2

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-modulo1',action ="store_true",help="Ejecutar el módulo 1 del aplicativo de validacion de productos")
    parser.add_argument('-modulo2',action ="store_true",help="Ejecutar el módulo 2 del aplicativo de validacion de productos")
    
    args = parser.parse_args()
    
    if args.modulo1:
        act = Modulo1()
        act.Start()
    elif args.modulo2:
        act = Modulo2()
        act.Start()
    else:
        print('Escriba una argumento: -modulo1 para Modulo1 o -modulo2 para Modulo2')

if __name__=='__main__':
    main()