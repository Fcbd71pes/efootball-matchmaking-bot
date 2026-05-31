Set WshShell = CreateObject("WScript.Shell")
Dim pyCmd
pyCmd = "python"

' Check if python is available in PATH, if not fallback to py
On Error Resume Next
WshShell.Run "python --version", 0, True
If Err.Number <> 0 Then
    pyCmd = "py"
End If
On Error GoTo 0

' Run the Telegram Bot and the Admin Panel completely hidden (window style = 0)
WshShell.Run pyCmd & " main.py", 0, False
WshShell.Run pyCmd & " admin_panel.py", 0, False
