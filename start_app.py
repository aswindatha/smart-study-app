import sys
import subprocess
import os
import platform
import time
import signal
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10.7"""
    required_version = (3, 10, 7)
    current_version = sys.version_info[:3]
    
    if current_version != required_version:
        print(f"❌ Error: Python {'.'.join(map(str, required_version))} is required, but you have {sys.version.split()[0]}")
        return False
    print(f"✓ Python version {'.'.join(map(str, required_version))} detected")
    return True

def check_requirements(venv_pip):
    """Check if all required packages are installed"""
    requirements_path = Path('smart_study_app/requirements.txt')
    if not requirements_path.exists():
        print(f"❌ Error: {requirements_path} not found")
        return False
    
    try:
        result = subprocess.run(
            [venv_pip, 'freeze'],
            capture_output=True,
            text=True,
            check=True
        )
        installed_packages = {line.split('==')[0].lower() for line in result.stdout.splitlines()}
        
        with open(requirements_path) as f:
            required_packages = {line.split('==')[0].lower() for line in f if line.strip() and not line.startswith('#')}
        
        missing = required_packages - installed_packages
        if missing:
            print(f"❌ Missing packages: {', '.join(missing)}")
            return False
            
        print("✓ All required packages are installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking installed packages: {e.stderr}")
        return False

def setup_venv(project_dir):
    """Set up and activate virtual environment"""
    venv_dir = os.path.join(project_dir, 'venv')
    venv_pip = os.path.join(venv_dir, 'Scripts', 'python') if platform.system() == 'Windows' else os.path.join(venv_dir, 'bin', 'python')
    pip_cmd = [venv_pip, '-m', 'pip']
    
    # Check if venv already exists
    if not os.path.exists(venv_dir):
        print("🔄 Creating virtual environment...")
        try:
            # Create new venv
            subprocess.run(
                [sys.executable, '-m', 'venv', 'venv'],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True
            )
            # Upgrade pip in the new venv
            print("🆙 Upgrading pip in the new environment...")
            subprocess.run(
                [*pip_cmd, 'install', '--upgrade', 'pip'],
                cwd=project_dir,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to set up virtual environment: {e.stderr}")
            return False
    else:
        print("✅ Using existing virtual environment")
    
    # Install/update requirements
    print("📦 Checking/installing requirements...")
    requirements_path = os.path.join(project_dir, 'requirements.txt')
    try:
        subprocess.run(
            [*pip_cmd, 'install', '-r', requirements_path],
            cwd=project_dir,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e.stderr}")
        return False

def is_port_in_use(port):
    """Check if a port is already in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def start_servers(project_dir):
    """Start Flask backend and Streamlit frontend"""
    from utils.network_utils import get_local_ip
    
    # Get local IP address
    local_ip = get_local_ip()
    
    # Check if ports are available
    if is_port_in_use(5000):
        print("❌ Port 5000 is already in use. Please close any other applications using this port.")
        return False
    if is_port_in_use(8501):
        print("❌ Port 8501 is already in use. Please close any other applications using this port.")
        return False
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['API_BASE_URL'] = f'http://{local_ip}:5000'
    
    try:
        # Start Flask backend
        print("🚀 Starting Flask backend...")
        flask_process = subprocess.Popen(
            [os.path.join('venv', 'Scripts', 'python'), 'app.py'],
            cwd=os.path.join(project_dir, 'smart_study_app'),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Wait for Flask to start
        time.sleep(3)
        
        # Verify Flask is running
        try:
            import requests
            response = requests.get(f'http://{local_ip}:5000/health', timeout=5)
            if response.status_code != 200:
                raise Exception("Flask did not start correctly")
        except Exception as e:
            print(f"❌ Failed to start Flask: {str(e)}")
            flask_process.terminate()
            return False
        
        # Start Streamlit frontend
        print("🚀 Starting Streamlit frontend...")
        streamlit_cmd = [
            os.path.join('venv', 'Scripts', 'streamlit'),
            'run',
            'app.py',
            '--server.port=8501',
            '--server.address=0.0.0.0',
            '--server.enableCORS=true',
            '--server.enableXsrfProtection=false'
        ]
        
        streamlit_process = subprocess.Popen(
            streamlit_cmd,
            cwd=os.path.join(project_dir, 'smart_study_app'),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print("\n✅ Application started successfully!")
        print(f"🌐 Local Network Access:")
        print(f"   Frontend: http://{local_ip}:8501")
        print(f"   Backend API: http://{local_ip}:5000")
        print("\n📱 Access from other devices on the same network using the IP addresses above")
        print("🛑 Press Ctrl+C to stop the application")
        
        def signal_handler(sig, frame):
            print("\n🛑 Stopping servers...")
            flask_process.terminate()
            streamlit_process.terminate()
            print("✅ Servers stopped")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()
        
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        if 'flask_process' in locals():
            flask_process.terminate()
        if 'streamlit_process' in locals():
            streamlit_process.terminate()
        return False
    
    return True

def main():
    # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set project_dir to smart_study_app if not already in it
    if os.path.basename(current_dir) != 'smart_study_app':
        project_dir = os.path.join(current_dir, 'smart_study_app')
    else:
        project_dir = current_dir
    
    print(f"📂 Using project directory: {project_dir}")
    print("🔍 Checking system requirements...\n")
    
    if not check_python_version():
        return
    
    try:
        if not setup_venv(project_dir):
            return
        
        start_servers(project_dir)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error details: {e.stderr}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Command output: {e.stderr}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}")
    finally:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
