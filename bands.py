import numpy as np, scipy.io.wavfile as w, scipy.signal as ss
def sp(fn,a,b):
    sr,x=w.read(fn); x=x.astype(float)/32768; y=x[int(a*sr):int(b*sr)]
    f,P=ss.welch(y,sr,nperseg=2048); return f,P
bands=[200,300,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000]
for nm,o,s in [('bombtail',('seg/s2.wav',4.2,7.6),('out/s2.wav',4.3,7.6)),('bombtone',('seg/s2.wav',1.0,3.5),('out/s2.wav',1.0,3.5)),('mgun',('seg/s5.wav',0.1,0.75),('out/s5.wav',0.05,0.7)),('siren',('seg/s7.wav',0.1,1.2),('out/s7.wav',0.1,1.2))]:
    f,Po=sp(*o); _,Ps=sp(*s)
    row=[]
    for c in bands:
        m=(f>c/1.12)&(f<c*1.12); row.append(10*np.log10(Po[m].mean()/Ps[m].mean()))
    row=np.array(row); row-=row[bands.index(2500)]
    print(nm.ljust(9),' '.join('%d:%+.0f'%(c,r) for c,r in zip(bands,row)))
