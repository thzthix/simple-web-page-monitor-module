# PowerShell 스케줄링 스크립트
# 이 스크립트를 실행하면 매일 오전 9시에 모니터링이 실행됩니다

$Action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 monitor.py" -WorkingDirectory "C:\Users\KICO\web_page_monitor"
$Trigger = New-ScheduledTaskTrigger -Daily -At 9AM
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName "웹페이지 모니터링" -Action $Action -Trigger $Trigger -Principal $Principal -Description "매일 웹페이지 변경사항 모니터링"

Write-Host "작업이 성공적으로 등록되었습니다!"
Write-Host "작업 스케줄러에서 '웹페이지 모니터링' 작업을 확인하세요." 