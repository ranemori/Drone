#!/usr/bin/env python3
"""
Script pour telecharger des donnees reelles CRAWDAD pour drones/WSN
Datasets disponibles:
- dartmouth/campus: Mobilite WiFi sur campus
- UCSD: Traces de mobilite wireless
- Intel Berkeley Lab: Reseau de capteurs
"""

import os
import urllib.request
import tarfile
import zipfile
import json
from pathlib import Path

CRAWDAD_DATASETS = {
    "intel-berkeley": {
        "name": "Intel Berkeley Research Lab Sensor Network",
        "url": "http://db.csail.mit.edu/labdata/data.txt.gz",
        "description": "54 capteurs sur 4 jours, donnees temperature/humidite/luminosite",
        "type": "sensor-network",
        "format": "txt.gz"
    }
}


def download_file(url, dest_path):
    """Telecharge un fichier depuis une URL"""
    print(f"[DOWNLOAD] {url}")
    print(f"[SAVE TO] {dest_path}")
    
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"[OK] Fichier telecharge: {os.path.getsize(dest_path)} bytes")
        return True
    except Exception as e:
        print(f"[ERROR] Echec telechargement: {e}")
        return False


def extract_archive(archive_path, extract_to):
    """Extrait une archive tar.gz, zip, ou décompresse un .gz simple"""
    print(f"[EXTRACT] {archive_path}")
    try:
        if archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz'):
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_to)
        elif archive_path.endswith('.gz'):
            import gzip
            import shutil
            output_path = os.path.join(extract_to, os.path.basename(archive_path)[:-3])
            with gzip.open(archive_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"[OK] Fichier décompressé: {output_path}")
            return True
        elif archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        print(f"[OK] Archive extraite vers {extract_to}")
        return True
    except Exception as e:
        print(f"[ERROR] Echec extraction: {e}")
        return False


def download_dataset(dataset_key):
    """Telecharge un dataset CRAWDAD"""
    if dataset_key not in CRAWDAD_DATASETS:
        print(f"[ERROR] Dataset inconnu: {dataset_key}")
        print(f"[INFO] Datasets disponibles: {', '.join(CRAWDAD_DATASETS.keys())}")
        return False
    
    dataset = CRAWDAD_DATASETS[dataset_key]
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Dataset: {dataset['name']}")
    print(f"Description: {dataset['description']}")
    print(f"Type: {dataset['type']}")
    print(f"{'='*60}\n")
    
    # Nom du fichier de destination
    filename = f"{dataset_key}.{dataset['format']}"
    dest_path = data_dir / filename
    
    # Telecharger
    if not download_file(dataset['url'], str(dest_path)):
        return False
    
    # Extraire si archive
    if dest_path.suffix in ['.gz', '.zip', '.tgz']:
        if not extract_archive(str(dest_path), str(data_dir)):
            return False
    
    # Creer metadata
    metadata = {
        "dataset": dataset_key,
        "name": dataset['name'],
        "description": dataset['description'],
        "type": dataset['type'],
        "source": "CRAWDAD",
        "url": dataset['url'],
        "downloaded": True
    }
    
    metadata_path = data_dir / f"{dataset_key}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n[SUCCESS] Dataset {dataset_key} telecharge avec succes")
    print(f"[INFO] Fichiers dans {data_dir}")
    
    return True


def main():
    """Menu principal"""
    print("\n" + "="*60)
    print("CRAWDAD Dataset Downloader - Donnees Reelles WSN/Drones")
    print("="*60 + "\n")
    
    print("Datasets disponibles:\n")
    for i, (key, info) in enumerate(CRAWDAD_DATASETS.items(), 1):
        print(f"{i}. {key}")
        print(f"   {info['name']}")
        print(f"   {info['description']}\n")
    
    print("Entrez le numero du dataset a telecharger (ou 'all' pour tout):")
    choice = input("> ").strip()
    
    if choice.lower() == 'all':
        for key in CRAWDAD_DATASETS.keys():
            download_dataset(key)
    else:
        try:
            idx = int(choice) - 1
            keys = list(CRAWDAD_DATASETS.keys())
            if 0 <= idx < len(keys):
                download_dataset(keys[idx])
            else:
                print("[ERROR] Choix invalide")
        except ValueError:
            # Peut-etre le nom direct
            if choice in CRAWDAD_DATASETS:
                download_dataset(choice)
            else:
                print("[ERROR] Choix invalide")


if __name__ == '__main__':
    main()
