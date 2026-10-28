import numpy as np, scipy.io.wavfile as w
sr,x=w.read('post.wav'); x=x.astype(float)/32768
K=32335.
f,R=np.load('resp.npy')
y=x[int(1.32*sr):int(1.67*sr)]; n=int(0.008*sr); h=int(0.0025*sr); Z=8*int(0.016*sr)
Ri=np.interp(np.fft.rfftfreq(Z,1/sr),f,R)
out=[]
for i in range(0,len(y)-n,h):
    sp=np.abs(np.fft.rfft(y[i:i+n]*np.hanning(n),Z))/Ri; fq=np.fft.rfftfreq(Z,1/sr)
    m=(fq>450)&(fq<3500); j=np.argmax(sp*m); out.append(K/fq[j])
print(' '.join('%.0f'%q for q in out))
