"""Projeyi buradan çalıştırın: python main.py"""
import sys
import os

# src klasörünü import path'e ekle
sys.path.insert(0, os.path.dirname(__file__))

from src.app import run

if __name__ == "__main__":
    run()