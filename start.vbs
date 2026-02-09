Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(".")
shell.Run "cmd /c cd corque-ui && npm start", 0, False
