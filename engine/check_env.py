import importlib.util
import sys

def check_package(name):
    spec = importlib.util.find_spec(name)
    return spec is not None

def main():
    required = ["openpyxl", "docling", "pandas"]
    missing = []
    
    print("🔍 Performing Pre-flight Environment Check...")
    for pkg in required:
        if check_package(pkg):
            print(f"✅ {pkg} is installed.")
        else:
            missing.append(pkg)
            print(f"❌ {pkg} is MISSING.")
            
    if missing:
        print("\n⚠️  Environment not ready!")
        print(f"Please run the following command to install missing dependencies:")
        print(f"pip install {' '.join(missing)}")
        sys.exit(1)
    else:
        print("\n🚀 Environment is ready for reimbursement processing.")
        sys.exit(0)

if __name__ == "__main__":
    main()
