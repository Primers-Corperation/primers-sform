import requests
import os

URL = "http://localhost:8000"

print("--- Testing Vercel Status ---")
try:
    r = requests.get(f"{URL}/")
    print(f"Status: {r.status_code}")
    print(f"Payload: {r.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Testing Vercel Compliance ---")
try:
    r = requests.get(f"{URL}/compliance")
    print(f"Status: {r.status_code}")
    print(f"Payload: {r.text}")
except Exception as e:
    print(f"Error: {e}")
