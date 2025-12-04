"""
Quick Launcher for UPI Fraud Detection UI
Easily launch either Streamlit or Gradio dashboard
"""

import sys
import subprocess

def print_banner():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        💸 UPI Fraud Detection System 💸              ║
    ║                                                       ║
    ║           Choose Your Dashboard Interface            ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

def main():
    print_banner()
    
    print("\n🎨 Available UI Options:\n")
    print("  1. 💎 Streamlit Dashboard (Recommended)")
    print("     - Modern gradient design")
    print("     - Interactive charts & animations")
    print("     - Professional styling")
    print()
    print("  2. 🚀 Gradio Dashboard (Alternative)")
    print("     - Clean & simple interface")
    print("     - Quick testing")
    print("     - Easy sharing")
    print()
    print("  3. ❌ Exit")
    print()
    
    choice = input("👉 Select an option (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Launching Streamlit Dashboard...")
        print("📍 URL: http://localhost:8501")
        print("⏸️  Press Ctrl+C to stop\n")
        try:
            subprocess.run(["streamlit", "run", "src/ui/dashboard.py"])
        except KeyboardInterrupt:
            print("\n\n✅ Dashboard stopped.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure Streamlit is installed:")
            print("  pip install streamlit")
    
    elif choice == "2":
        print("\n🚀 Launching Gradio Dashboard...")
        print("📍 URL: http://localhost:7860")
        print("⏸️  Press Ctrl+C to stop\n")
        try:
            subprocess.run([sys.executable, "src/ui/gradio_dashboard.py"])
        except KeyboardInterrupt:
            print("\n\n✅ Dashboard stopped.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure Gradio is installed:")
            print("  pip install gradio")
    
    elif choice == "3":
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid choice. Please select 1, 2, or 3.\n")
        main()

if __name__ == "__main__":
    main()
