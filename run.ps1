# Makefile-like script for Windows
# Usage: .\run.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$VENV = "C:/Users/PC/Desktop/TheorieGraph_Drone/.venv/Scripts/python.exe"

switch ($Command) {
    "install" {
        Write-Host " Installation des dépendances..." -ForegroundColor Green
        pip install -r requirements.txt
    }
    
    "test" {
        Write-Host " Lancement des tests..." -ForegroundColor Green
        & $VENV tests/run_tests.py
    }
    
    "run" {
        Write-Host " Lancement de la simulation..." -ForegroundColor Green
        & $VENV src/main.py
    }
    
    "cli" {
        Write-Host " Lancement CLI..." -ForegroundColor Green
        $args = $args[1..($args.Length-1)]
        & $VENV src/cli.py $args
    }
    
    "quick" {
        Write-Host " Simulation rapide..." -ForegroundColor Green
        & $VENV src/cli.py --quick
    }
    
    "analyse" {
        Write-Host " Analyse comparative..." -ForegroundColor Green
        & $VENV src/analyse_comparative.py
    }
    
    "mesure" {
        Write-Host " Mesure formelle de convergence..." -ForegroundColor Green
        & $VENV src/mesure_formelle.py
    }
    
    "test-convergence" {
        Write-Host " Test rapide de convergence..." -ForegroundColor Green
        & $VENV src/test_rapide_convergence.py
    }
    
    "experiences" {
        Write-Host " Expériences cruciales (AVEC/SANS règle)..." -ForegroundColor Green
        & $VENV src/experiences_cruciales.py
    }
    
    "clean" {
        Write-Host " Nettoyage..." -ForegroundColor Green
        Remove-Item -Recurse -Force report/* -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force src/__pycache__ -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force tests/__pycache__ -ErrorAction SilentlyContinue
    }
    
    "help" {
        Write-Host @"
 RÉSEAU DE DRONES - Commandes disponibles

Installation:
  .\run.ps1 install          Installer les dépendances

Exécution:
  .\run.ps1 run             Lancer la simulation interactive
  .\run.ps1 cli [options]   Lancer avec la CLI
  .\run.ps1 quick           Simulation rapide (mode test)

Tests:
  .\run.ps1 test            Lancer tous les tests

Analyses:
  .\run.ps1 analyse         Analyses comparatives
  .\run.ps1 mesure          Mesure formelle de convergence
  .\run.ps1 test-convergence Test rapide de la nouvelle règle
  .\run.ps1 experiences      Expériences cruciales (AVEC/SANS règle)

Utilitaires:
  .\run.ps1 clean           Nettoyer les fichiers générés
  .\run.ps1 help            Afficher cette aide

Exemples CLI:
  .\run.ps1 cli --drones 30 --iterations 200
  .\run.ps1 cli --mode robustesse --no-viz
  .\run.ps1 cli --export json -o mes_resultats/
"@ -ForegroundColor Cyan
    }
    
    default {
        Write-Host "Commande inconnue: $Command" -ForegroundColor Red
        Write-Host "Utilisez '.\run.ps1 help' pour voir les commandes disponibles" -ForegroundColor Yellow
    }
}
