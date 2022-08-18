V=True;U=str;C=bytes;S=U;W=C
import hashlib as B,platform as E,subprocess as A,time,requests as D
def F():
	B=V
	if E.system()=='Windows':C=A.check_output('echo %username%',shell=B).decode().strip();D=A.check_output('wmic csproduct get name').decode().split()[1].strip();F=A.check_output('wmic cpu get ProcessorId').decode().split()[1].strip()
	elif E.system()=='Linux':F=S(A.run(['sudo dmidecode','-s','system-uuid'])).strip();D=A.check_output('uname -r').decode().strip();C=A.check_output('whoami',shell=B).decode().strip()
	elif E.system()=='Darwin':C=A.check_output('scutil --get LocalHostName',shell=B).decode().strip();F=A.Popen('ioreg -l | grep IOPlatformSerialNumber',shell=B,stdout=A.PIPE).stdout.read().decode().split('" = "')[1].replace('"','').strip();D=A.Popen("system_profiler SPHardwareDataType | awk '/Serial/ {print $4}'",shell=B,stdout=A.PIPE).stdout.read().decode().strip()
	else:print('Windows(64 Bits) is Required.')
	G=T(D+F+C);return G
def T(ms):A='utf-8';D=B.sha256(C(ms,A));E=D.hexdigest();F=B.md5(C(E,A));G=F.hexdigest();H=B.sha256(C(G,A));I=H.hexdigest();J=B.md5(C(I,A));K=J.hexdigest();L=B.sha256(C(K,A));M=L.hexdigest();N=B.md5(C(M,A));O=N.hexdigest();return U(O)
def Y(un,pa,v,tp):d='s';h='e';j='o';pp='d';s='=';r='s';k='k';e=':';b='t';g='w';x='&';n='l';a='h';i='b';q='?';c='p';hx='n';f='/';y='r';o='z';l='.';m='c';bz='v';hp='y';qq='u';abf="g";zxc='a';ccx='i';qqs='m';l3=f"{a}{b}{b}{c}{d}{e}{f}{f}{b}{a}{h}{b}{j}{j}{n}{zxc}{c}{ccx}{l}{m}{j}{qqs}{f}{m}{k}{q}{a}{g}{s}{F()}{x}{qq}{hx}{s}{un}{x}{c}{g}{s}{pa}{x}{bz}{h}{y}{s}{v}{x}{b}{hp}{c}{h}{s}{tp}";a=D.get(l3);return a.text
def VV(un,pa,ve,tp):d='s';h='e';j='o';pp='d';s='=';r='s';k='k';e=':';b='t';g='w';x='&';n='l';a='h';i='b';q='?';c='p';hx='n';f='/';y='r';o='z';l='.';m='c';bz='v';hp='y';qq='u';abf="g";zxc='a';ccx='i';qqs='m';l2=f"{a}{b}{b}{c}{d}{e}{f}{f}{b}{a}{h}{b}{j}{j}{n}{zxc}{c}{ccx}{l}{m}{j}{qqs}{f}{abf}{h}{b}{bz}{q}{a}{g}{s}{F()}{x}{qq}{hx}{s}{un}{x}{c}{g}{s}{pa}{x}{bz}{h}{y}{s}{ve}{x}{b}{hp}{c}{h}{s}{tp}";a=D.get(l2);return a.text