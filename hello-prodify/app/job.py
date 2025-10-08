# app/job.py
import os, time, datetime

def main():
    print("🚀 Prodify job starting")
    print("FIRESTORE_DB =", os.getenv("FIRESTORE_DB", "(not set)"))
    print("UTC now:", datetime.datetime.utcnow().isoformat() + "Z")
    for i in range(3):
        print(f"tick {i+1}/3"); time.sleep(1)
    print("✅ Prodify job done")

if __name__ == "__main__":
    main()

