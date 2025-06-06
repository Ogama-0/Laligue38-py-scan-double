import os
import hashlib

def hash_file(path, block_size=65536):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            hasher.update(block)
    return hasher.hexdigest()


def scan_double_name(rootpath) :
    names = {}
    doublons = 0

    for root, _, files in os.walk(rootpath):
        for file_name in files:
            global_path = os.path.join(root, file_name)
            try :
                if file_name in names:
                    print(f"Doublon trouvé : {global_path} (identique à {names[file_name]})")
                    doublons += 1
                else:
                    names[file_name] = global_path
            except Exception as e:
                print(f"Erreur avec le fichier {global_path} : {e}")

    print(f"scan terminée. {doublons} doublon(s) trouvé(s).")

def scan_double_hash(rootpath) :
    hashes = {}
    doublons = 0
    for root, _, files in os.walk(rootpath):
        for file_name in files:
            global_path = os.path.join(root, file_name)
            try:
                file_hash = hash_file(global_path)
                if file_hash in hashes:
                    print(f"Doublon trouvé : {global_path} (identique à {hashes[file_hash]})")
                    doublons += 1
                else:
                    hashes[file_hash] = global_path
            except Exception as e:
                print(f"Erreur avec le fichier {global_path} : {e}")

    print(f"scan terminée. {doublons} doublon(s) trouvé(s).")


def scan_double_hash_name(rootpath) :
    hashes = {}
    doublons = 0
    for root, _, files in os.walk(rootpath):
        for file_name in files:
            global_path = os.path.join(root, file_name)
            try:
                file_hash = hash_file(global_path)
                if file_hash in hashes and file_name == os.path.basename(hashes[file_hash]):
                    print(f"Doublon trouvé : {global_path} (identique à {hashes[file_hash]})")
                    doublons += 1
                else:
                    hashes[file_hash] = global_path
            except Exception as e:
                print(f"Erreur avec le fichier {global_path} : {e}")

    print(f"scan terminée. {doublons} doublon(s) trouvé(s).")


if __name__ == "__main__":
    compt_methode = input("Methode de comparaison : (name) ou (bin) ou (both) : ")
    rootpath = "/home/ogama/documents/Laligue38/arbo_test"
    if (compt_methode == "name") :
        scan_double_name(rootpath)
    elif (compt_methode == "bin") :
        scan_double_hash(rootpath)
    elif (compt_methode == "both") :
        scan_double_hash_name(rootpath)
