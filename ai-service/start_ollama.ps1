$port = 11434
$pid = (netstat -ano | findstr ":$port" | Select-Object -First 1).Split()[-1]
if ($pid) {
    Write-Host "Killing process $pid on port $port"
    taskkill /f /pid $pid
}
Write-Host "Starting ollama serve"
ollama serve