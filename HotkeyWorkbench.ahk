#Requires AutoHotkey v2.0
#SingleInstance Force
#MaxThreadsPerHotkey 1
; AutoHotkey v2 port of the original Python/pynput sequences.
Target := "ahk_exe left4dead2.exe"
Paused := false
Busy := false
Generation := 0
LastRun := -1000
Preview := true
LogLines := []
Sequences := Map(
    "q", [["{WheelDown 2}", 31], ["{WheelUp 2}", 32]],
    "t", [["{LButton}", 100], ["{RButton}", 0]],
    "1", [["{LButton}", 10], ["{RButton}", 10], ["{Space}", 20]]
)

if A_Args.Length && A_Args[1] = "--self-test" {
    if Sequences.Count != 3 || Sequences["1"].Length != 3
        ExitApp(1)
    FileAppend("AutoHotkey v2 configuration loaded successfully`n", "*")
    ExitApp(0)
}

Panel := Gui(, "Hotkey Workbench")
Panel.SetFont("s11", "Segoe UI")
Panel.AddText("w560", "Hotkey Workbench — Q / T / 1")
Panel.AddText("w560", "Preview logs actions. Live mode only sends to Left 4 Dead 2.")
PreviewBox := Panel.AddCheckbox("Checked", "Preview only (no mouse or keyboard output)")
PreviewBox.OnEvent("Click", ChangeMode)
for key in ["q", "t", "1"] {
    button := Panel.AddButton("w170 " (key = "q" ? "" : "yp x+10"), "Preview " StrUpper(key))
    button.OnEvent("Click", RunSequence.Bind(key, true))
}
Panel.AddButton("xm w170", "Pause / Resume (F8)").OnEvent("Click", TogglePause)
Panel.AddButton("yp x+10 w170", "Exit (Alt+F5)").OnEvent("Click", (*) => ExitApp())
Status := Panel.AddText("xm w560", "Ready · Preview")
Console := Panel.AddEdit("w560 r12 ReadOnly", "")
Panel.OnEvent("Close", (*) => ExitApp())
Panel.Show()

#HotIf WinActive(Panel.Hwnd)
$q::RunAndWait("q", true)
$t::RunAndWait("t", true)
$1::RunAndWait("1", true)
F8::TogglePause()
!F5::ExitApp()
#HotIf !Preview && WinActive(Target)
$q::RunAndWait("q", false)
$t::RunAndWait("t", false)
$1::RunAndWait("1", false)
F8::TogglePause()
!F5::ExitApp()
#HotIf

RunAndWait(key, demo) {
    RunSequence(key, demo)
    KeyWait(key)
}

ChangeMode(*) {
    global Preview, Generation, Busy
    Generation += 1
    Busy := false
    Preview := !!PreviewBox.Value
    Status.Text := Preview ? "Ready · Preview" : "Ready · Live (game foreground only)"
}

TogglePause(*) {
    global Paused, Generation, Busy
    Paused := !Paused
    Generation += 1
    Busy := false
    Status.Text := Paused ? "Paused" : (Preview ? "Ready · Preview" : "Ready · Live")
}

RunSequence(key, demo, *) {
    global Busy, LastRun, Generation
    if Paused || Busy || A_TickCount - LastRun < 300
        return
    if !demo && (Preview || !WinActive(Target))
        return
    Busy := true
    LastRun := A_TickCount
    Generation += 1
    token := Generation
    Log("Start " StrUpper(key) (demo ? " · preview" : " · live"))
    NextStep(key, demo, token, 1)
}

NextStep(key, demo, token, index) {
    global Busy
    if token != Generation
        return
    if Paused || (!demo && (Preview || !WinActive(Target))) {
        Busy := false
        Log("Cancelled: pause or target lost focus")
        return
    }
    if index > Sequences[key].Length {
        Busy := false
        Log("Complete")
        return
    }
    step := Sequences[key][index]
    if !demo
        SendEvent(step[1])
    Log(step[1] " · wait " step[2] " ms")
    SetTimer(NextStep.Bind(key, demo, token, index + 1), -Max(1, step[2]))
}

Log(message) {
    LogLines.Push(FormatTime(, "HH:mm:ss") "  " message)
    if LogLines.Length > 80
        LogLines.RemoveAt(1)
    text := ""
    for line in LogLines
        text .= line "`r`n"
    Console.Value := text
}
