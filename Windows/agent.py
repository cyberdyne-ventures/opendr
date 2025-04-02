import subprocess
import concurrent.futures

def execute_scripts(script):
    print(script)
    result = subprocess.run(['python', script], capture_output=True, text=True)
    return script, result.stdout, result.stderr

def run():
  # this section governs local vs database mode - default is local
  generators = ['processlog.py', 'softwareinventorylog.py', 'endpointinfolog.py', 'networklog.py', 'windowsserviceslog.py']
  # this generator is for database mode
  # generators = ['softwareinventorylog.py', 'endpointinfolog.py', 'userinfolog.py', 'processlog.py', 'networklog.py', 'windowsserviceslog.py', 'dboperations.py']
  print('Starting Generators')
  with concurrent.futures.ThreadPoolExecutor(len(generators)) as executor:
    results = executor.map(execute_scripts, generators)
    for script, stdout, stderr in results:
      print(f"Results from {script}:")
      print(stdout)
      if(stderr):
        print(f"Errors from {script}:")
        print(stderr)

run()