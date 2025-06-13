import os
import hashlib


hash_cache_file = {}
hash_cache_folder = {}

def hash_file(path):
    if path in hash_cache_file:
        return hash_cache_file[path]
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    hash_cache_file[path] = digest
    return digest


def hash_folder(path):
    if path in hash_cache_folder:
        return hash_cache_folder[path]

    if not os.path.isdir(path):
        return hash_file(path)

    hash_elements = []
    for item in sorted(os.listdir(path)):  # sort for fix issues
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            hash_elements.append(f"dir:{item}:{hash_folder(item_path)}")
        else:
            hash_elements.append(f"file:{item}:{hash_file(item_path)}")

    hasher = hashlib.sha256()
    for element in hash_elements:
        hasher.update(element.encode())
    digest = hasher.hexdigest()
    hash_cache_folder[path] = digest
    return digest

def scan_double_hash(rootpath:str) :
    doublons = _scan_double_hash(rootpath)

    print("found : " + str(len(doublons)) + " doublon(s)")


def _scan_double_hash(rootpath:str) -> dict[str, str] :
    '''
    arg :
        rootpath : (str) the path of the folder scaned
    return :
        doublons : {str:str}
        doublons : {path of the duplicate file : path of the original file}


    '''
    if os.path.basename(rootpath)[0] == "." :
        return ({}) # do not go in hidden folder
    double_files_in_the_folder = 0
    double_fifo = {}
    children = os.listdir(rootpath)
    for child in children:
        full_path = os.path.join(rootpath, child)

        if not os.path.isdir(full_path):
            file_hash = hash_file(full_path)
            if (file_hash in hash_cache_file) :
                double_files_in_the_folder +=1
                double_fifo[full_path] = hash_cache_file[file_hash]

        else :
            chid_doublons = _scan_double_hash(full_path)
            folder_hash = hash_folder(full_path)
            if (folder_hash in hash_cache_folder) :
                double_files_in_the_folder +=1
                double_fifo[full_path] = hash_cache_folder[folder_hash]

            double_fifo |= chid_doublons

    if (len(children) == double_files_in_the_folder) :
        return {}

    return double_fifo

def scan_double_name_legacy(rootpath) :
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

def scan_double_hash_legacy(rootpath) :
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


def scan_double_folder_hash(racine):
    hash_to_paths = {}
    for root, dirs, _ in os.walk(racine):
        for d in dirs:
            chemin = os.path.join(root, d)
            h = hash_folder(chemin)
            if h in hash_to_paths:
                print(f"Dossier en double trouvé : {chemin} == {hash_to_paths[h]}")
            else:
                hash_to_paths[h] = chemin

if __name__ == "__main__":
    compt_methode = input("Methode de comparaison : (lname) ou (lbin) ou (folder) ou (new) : ")
    rootpath = "/home/ogama/documents/Laligue38/arbo_test/"
    if (compt_methode == "lname") :
        scan_double_name_legacy(rootpath)
    elif (compt_methode == "lbin") :
        scan_double_hash_legacy(rootpath)
    elif (compt_methode == "folder") :
        scan_double_folder_hash(rootpath)
    elif (compt_methode == "new") :
        scan_double_hash(rootpath)
