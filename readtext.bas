ReDim recstr(0) As String   ' fixed size is no good!
ReDim recstr2(0) as String  

Function Recall(fname As String, recstr() As String, recstr2() As String) As Integer
	Dim As Integer ct=0
	Dim a as string
	Dim k as long
	If Open(fname For Binary Access Read As #1) = 0 Then
		While Not Eof(1)
			ReDim Preserve recstr(ct)
			ReDim Preserve recstr2(ct)
			Line Input #1, recstr(ct)
			a = recstr(ct)
			k = instr(a,"ipynb:")
			a = trim(right(a,len(a) - k -6))

			recstr2(ct) = a
			ct=ct+1
		Wend
		Close #1
	Else
		Print "Error opening file"
	End If
	Return ct
End Function

Dim As Double tickssec=Timer
Dim As Integer ticks, records
dim k as long
dim first as string
dim i as long
dim middle as string
'Print "loading ";Command$(1);" took ";
records=Recall(Command$(1), recstr(),recstr2())
open Command(2) for output as #2

'ticks=(Timer-tickssec)*1000
'Print ticks;" ms"


i = 0
Do While i < records 

'For i As Integer=0 To records-1
k = instr(recstr(i),"ipynb:") + 6
first = trim(left(recstr(i),k))
print first
	if left(recstr2(i),5) = "sage:" and left(recstr2(i+1),5) = "sage:"  then
		print #2,  first & "   " & recstr2(i)

	else
	middle = recstr2(i)

 	i = i + 1

Do while left(recstr2(i),5) = "....:"

	middle =  middle & "   " &recstr2(i)
	i = i + 1
Loop
	print #2, first &"   "& middle

	i = i - 1

endif
'	If i<5 Or i>records-5 Then
	'	Print recstr2(i)', recstr2(i)
'	ElseIf i=5 Then
'		Print "..."first = trim(left(recstr(i),k))

i = i + 1 
Loop

'Sleep

