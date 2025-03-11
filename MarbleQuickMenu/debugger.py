import submodule_loader
import os 

PATH = os.path.join( os.path.dirname(__file__), "scripts"  )

def main():
    submodule_loader.submodule_loader(PATH).init_submodule()

main()