import os
import hashlib
import csv

hash_cache_file = {}
hash_cache_folder = {}

# def print_size(size:int) -> str:
#     str_size = str(size)
#     if len(str_size) <= 3 :
#         return str_size + " o"
#     elif len(str_size) <= 6 :
#         return str_size[:-3] + "Ko"
#     elif len(str_size) <= 9 :
#         return str_size[:-6] + " Mo"
#     else :
#         return str_size[:-9] + " Go"

def print_size(size: int) -> str:
    if size < 1_000:
        return f"{size} o"
    elif size < 1_000_000:
        return f"{size // 1_000} Ko"
    elif size < 1_000_000_000:
        return f"{size // 1_000_000} Mo"
    else:
        return f"{size // 1_000_000_000} Go"

def is_hidden(path):
    return os.path.basename(path).startswith(".")

def hash_file(path):
    if path in hash_cache_file:
        return hash_cache_file[path]

    if os.path.getsize(path) == 0:
            return None  # Ignorer les fichiers de 0 octet
    hasher = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
    except Exception as e:
        print(f"Erreur lors du hachage de {path} : {e}")
        return None

    digest = hasher.hexdigest()
    hash_cache_file[path] = digest
    return digest

def hash_folder_strict(path):
    if path in hash_cache_folder:
        return hash_cache_folder[path]

    if not os.path.isdir(path):
        return hash_file(path)

    try:
        items = sorted(os.listdir(path))
    except Exception as e:
        print(f"Erreur d'accès à {path} : {e}")
        return None

    hash_elements = []

    for item in items:
        if is_hidden(item):
            continue

        item_path = os.path.join(path, item)

        if os.path.isdir(item_path):
            sub_hash = hash_folder_strict(item_path)
            if sub_hash is None:
                return None
            hash_elements.append(f"dir:{item}:{sub_hash}")
        else:
            file_hash = hash_file(item_path)
            if file_hash is None or file_hash not in hash_cache_file.values():
                return None  # fichier non déjà vu ailleurs
            hash_elements.append(f"file:{item}:{file_hash}")

    hasher = hashlib.sha256()
    for element in hash_elements:
        hasher.update(element.encode())

    digest = hasher.hexdigest()
    hash_cache_folder[path] = digest
    return digest

def recursive_scan_double_hash(rootpath, known_folder_hashes=None):
    if known_folder_hashes is None:
        known_folder_hashes = set()

    if is_hidden(rootpath):
        return {}

    double_fifo = {}

    try:
        children = [child for child in os.listdir(rootpath) if not is_hidden(child)]
    except Exception as e:
        print(f"Erreur d'accès à {rootpath} : {e}")
        return {}

    folder_hash = hash_folder_strict(rootpath)
    if folder_hash in known_folder_hashes:
        return {}

    if folder_hash:
        for other_path, h in hash_cache_folder.items():
            if h == folder_hash and other_path != rootpath:
                double_fifo[rootpath] = other_path
                known_folder_hashes.add(folder_hash)
                return double_fifo  # on ne descend pas dans ce dossier

    for child in children:
        full_path = os.path.join(rootpath, child)

        if os.path.isdir(full_path):
            child_doublons = recursive_scan_double_hash(full_path, known_folder_hashes)
            double_fifo.update(child_doublons)
        else:
            file_hash = hash_file(full_path)
            if file_hash is None:
                continue

            for other_path, h in hash_cache_file.items():
                if h == file_hash and other_path != full_path:
                    double_fifo[full_path] = other_path
                    break

    return double_fifo

# def export_csv(doublons: dict, output_file: str = "output.csv"):
#     try:
#         with open(output_file, mode="w", newline="") as f:
#             writer = csv.writer(f)
#             writer.writerow(["Doublon", "Original"])
#             for doublon, original in doublons.items():
#                 writer.writerow([doublon, original])
#         print(f"Fichier CSV généré : {output_file}")
#     except Exception as e:
#         print(f"Erreur lors de la génération du fichier CSV : {e}")
def export_csv(doublons: dict, output_file: str = "output.csv"):
    try:
        with open(output_file, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Doublon", "Original", "Taille (octets)"])
            for doublon, original in doublons.items():
                try:
                    size = os.path.getsize(doublon)
                except Exception as e:
                    print(f"Erreur pour obtenir la taille de {doublon} : {e}")
                    size = "?"
                writer.writerow([doublon, original, print_size(size)])
        print(f"Fichier CSV généré : {output_file}")
    except Exception as e:
        print(f"Erreur lors de la génération du fichier CSV : {e}")

def scan_double_hash(rootpath):
    print(f"Scan en cours sur : {rootpath}")
    doublons = recursive_scan_double_hash(rootpath)
    for doublon, original in doublons.items():
        print(f"Doublon trouvé : {doublon} (identique à {original})")
    print(f"Scan terminé. {len(doublons)} doublon(s) trouvé(s).")
    export_csv(doublons)

if __name__ == "__main__":
    import sys
    compt_methode = input("Méthode de comparaison : (new) : ").strip()
    if compt_methode != "new":
        print("Seule la méthode 'new' est prise en charge.")
        sys.exit(1)

    if len(sys.argv) > 1:
        rootpath = sys.argv[1]
    else:
        rootpath = input("Chemin du dossier à scanner : ").strip()

    scan_double_hash(rootpath)

