#!/usr/bin/env python3
"""
extraction.py

Chama, em sequência, os três scripts:
 1. acidentes.py
 2. geo_rod.py
 3. meteorologico.py (pesada)
"""

import acidentes
import geo_rod 
import meteorologico

def main():
    # executa o pipeline de acidentes
    acidentes.main()
    # executa o segundo script (DNIT, geoloc)
    geo_rod.main()
    # executa o pipeline meteorológico
    meteorologico.main()

if __name__ == "__main__":
    main()