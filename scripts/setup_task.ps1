$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"C:\Users\GranT\OneDrive\Masaüstü\tradepanel\scripts\run_worker.bat`""
$Trigger = New-ScheduledTaskTrigger -Daily -At "00:00"
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "SovereignNodeWorker" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Daily run of the Sovereign Node trading engine at midnight TRT" -Force

Write-Host "Task 'SovereignNodeWorker' successfully registered in Windows Task Scheduler."
Write-Host "It will run every night at 00:00."
