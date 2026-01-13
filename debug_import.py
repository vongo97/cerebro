import sys
import os

print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"CWD: {os.getcwd()}")
sys.path.append(os.getcwd())

try:
    print("Intentando importar api_cerebro...")
    import api_cerebro
    print("Ok")
except Exception as e:
    print(f"Fallo api_cerebro: {e}")

try:
    print("Intentando importar api_cerebro.main...")
    from api_cerebro import main
    print("Ok")
    print(f"Atributos en main: {dir(main)}")
except Exception as e:
    print(f"Fallo api_cerebro.main: {e}")
    import traceback
    traceback.print_exc()
