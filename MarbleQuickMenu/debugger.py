import MarbleQuickMenu.SubmoduleDatabaseCore as SubmoduleDatabaseCore
import os 

PATH = os.path.join( os.path.dirname(__file__), "scripts"  )

def main():
    SubmoduleDatabaseCore.submodule_loader(PATH).init_submodule()

main()