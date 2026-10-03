
sub header()
	print #2,"{"
	print #2," "&chr(34)&"cells"&chr(34)&": ["
end sub
sub footer()
print #2,"],"
print #2,chr(34)&"metadata"&chr(34)&": {"
print #2," "&chr(34)&"kernelspec"&chr(34)&": {"
print #2,"  "&chr(34)&"display_name"&chr(34)&": "&chr(34)&"SageMath 10.6"&chr(34)&","
print #2,"  "&chr(34)&"language"&chr(34)&": "&chr(34)&"sage"&chr(34)&","
print #2,"  "&chr(34)&"name"&chr(34)&": "&chr(34)&"sagemath"&chr(34)
print #2," },"
print #2," "&chr(34)&"language_info"&chr(34)&": {"
print #2,"  "&chr(34)&"codemirror_mode"&chr(34)&": {"
print #2,"   "&chr(34)&"name"&chr(34)&": "&chr(34)&"ipython"&chr(34)&","
print #2,"   "&chr(34)&"version"&chr(34)&": 3"
print #2,"   },"
print #2,"   "&chr(34)&"file_extension"&chr(34)&": "&chr(34)&".py"&chr(34)&","
print #2,"   "&chr(34)&"mimetype"&chr(34)&": "&chr(34)&"text/x-python"&chr(34)&","
print #2,"   "&chr(34)&"name"&chr(34)&": "&chr(34)&"python"&chr(34)&","
print #2,"   "&chr(34)&"nbconvert_exporter"&chr(34)&": "&chr(34)&"python"&chr(34)&","
print #2,"   "&chr(34)&"pygments_lexer"&chr(34)&": "&chr(34)&"ipython3"&chr(34)&","
print #2,"   "&chr(34)&"version"&chr(34)&": "&chr(34)&"3.13.3"&chr(34)
print #2,"  }"
print #2," },"
print #2," "&chr(34)&"nbformat"&chr(34)&": 4,"
print #2," "&chr(34)&"nbformat_minor"&chr(34)&": 5"
print #2,"}"

end sub

Function  replace(byval s as String, s1 as String, s2 as string) as string 
var position = Instr(s,s1),lens1=len(s1),lens2=len(s2)
While position > 0 
	s = Mid(s,1,position-1) & s2 & mid(s,position+Lens1)
	position = Instr(position+Lens2,s,s1)
Wend
replace = s
end function

Sub parseString(ByRef inputString as String, ByRef delimiter as String, result() as String)
Dim as Integer i, startPos, endPos, count = 0
'count the number of delimiters to size the array
	startPos = 1
	Do
		endPos = Instr(startPos, inputString, delimiter)
		if endPos > 0 then
			count +=1
			startPos = endPos + len(delimiter)
		Else
			Exit Do
		end if
	loop

'redim the array
	Redim result(count)
	'parse the string
	startPos = 1
	for i = 0 to count
		endPos = Instr(startPos,inputString,delimiter)
		if endPos > 0 then
			result(i) = Mid(inputString,startPos,endPos - startPos)
			startPos = endPos + Len(delimiter)
		Else
			result(i) = Mid(inputString,startPos)
		end if
	next i
end sub

'Things start here!!!


PRINT "Pass1 Editor"
dim a as string, b as string
dim filename as string
dim filenamea as string
dim filenameb as string
dim filenameold as string
dim cmdline as string
dim delim as string
dim parta as string, partb as string, partc as string
dim repairdel as string
dim myArray() as string
dim k1 as long
dim k as long
dim l as long
dim l1 as long
dim f1 as string, f2 as string
delim = "....:"
 

filenameold =""

Open Command(1) for input as #1
Open Command(2) for output as #2

Do Until EOF(1)

line input #1, a
line input #1, b

if instr(b,delim) > 0 then
 stop	
else
print #2, a
print #2, b
line input #1, a,
goto myloopend	
end if


#print a
k = instr(a,":")
filenamea = left(a,k-1)

f1 = "/" 
f2 = "_"
filenamea = replace(filenamea,f1,f2)

k = instr(b,":")
filenameb = left(b,k-1)

f1 = "/" 
f2 = "_"
filenameb = replace(filenameb,f1,f2)





a =  right(a,len(a)-k-1)
print a
if filenameold <> filename then
	print #2,"  {"	
	print #2,"   "&chr(34)&"cell_type"&chr(34)&": "&chr(34)&"code"&chr(34)&","
	print #2,"   "&chr(34)&"execution_count"&chr(34)&": null,"
	print #2,"   "&chr(34)&"id"&chr(34)&": null,"
	print #2,"   "&chr(34)&"metadata"&chr(34)&": {},"
	print #2,"   "&chr(34)&"outputs"&chr(34)&": [],"
	print #2,"   "&chr(34)&"source"&chr(34)&": ["
	print #2,"    "&chr(34)&" "&chr(34)
	print #2,"   ]"
	print #2,"  }"
	footer()
	close #2
	open filename for output as #2
	filenameold = filename
	header()
end if

print filename
k1 = instr(a,"sage:")
cmdline = rtrim(right(a,len(a)-k1-5))
'print cmdline


' need to change any quoted string "   " in cmdline with  \"   \"
if instr(cmdline,chr(34)) > 0 then
	f1 = chr(34)
	f2 = "\"&chr(34)
cmdline =     replace(cmdline,f1,f2)

end if

	'print cmdline
	parseString(cmdline,delim,MyArray())


print #2,"  {"
print #2,"   "&chr(34)&"cell_type"&chr(34)&": "&chr(34)&"code"&chr(34)&","
print #2,"   "&chr(34)&"execution_count"&chr(34)&": null,"
print #2,"   "&chr(34)&"id"&chr(34)&": null,"
print #2,"   "&chr(34)&"metadata"&chr(34)&": {},"
print #2,"   "&chr(34)&"outputs"&chr(34)&": [],"
print #2,"   "&chr(34)&"source"&chr(34)&": ["

for i as integer = Lbound(MyArray) to Ubound(MyArray)

if Ubound(MyArray) = 0 then 
	print #2,"    "&chr(34); Rtrim(MyArray(i));chr(34) 
else
	if i < Ubound(MyArray) then 
		print #2,"    "&chr(34); Rtrim(MyArray(i));"\n"&chr(34)&","
	else
		print #2,"    "&chr(34); Rtrim(MyArray(i));"\n"&chr(34)
	end if
end if
next i

print #2,"   ]"
print #2,"  },"

'print #2,cmdline
myloopend:
Loop

close #1

end

