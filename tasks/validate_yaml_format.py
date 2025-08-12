# tasks/validate_yaml_format.py

"""
Teste la validité syntaxique d'un fichier YAML donné
Usage : python validate_yaml_format.py <chemin/vers/fichier.yaml>
"""

import sys
import yaml
import os

def validate_yaml_file(path):
    if not os.path.exists(path):
        print(f"❌ Fichier introuvable : {path}")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        print(f"✅ YAML valide : {path}")
    except yaml.YAMLError as e:
        print(f"❌ Erreur YAML dans {path} :\n{e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage : python validate_yaml_format.py <chemin/vers/fichier.yaml>")
    else:
        validate_yaml_file(sys.argv[1])
