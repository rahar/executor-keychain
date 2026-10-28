import numpy as np, scipy.io.wavfile as w, scipy.signal as ss, scipy.optimize as so
sr,x=w.read('post.wav'); x=x.astype(float)/32768
K=32335.0; fc=K/5
y=x[int(7.6*sr):int(11.3*sr)]
fq,P=ss.welch(y,sr,nperseg=2048)
m=(fq>200)&(fq<9000); fq=fq[m]; P=P[m]
# LFSR NRZ spectrum envelope sinc^2(f/fc)
env=np.sinc(fq/fc)**2+1e-4
meas=10*np.log10(P/env); 
# smooth over 1/12 oct
sm=np.array([meas[(fq>f/1.03)&(fq<f*1.03)].mean() for f in fq])
def model(p,f):
    fs,Qs,fh,Qh,g,ph,fl,G=p
    s=2j*np.pi*f
    ws=2*np.pi*fs; wh=2*np.pi*fh; wl=2*np.pi*fl
    cone=s*s/(s*s+s*ws/Qs+ws*ws)/(1+s/wl)
    cav=wh*wh/(s*s+s*wh/Qh+wh*wh)
    H=cone*((1-g)+g*np.exp(1j*ph)*cav)
    return 20*np.log10(np.abs(H)+1e-9)+G
def err(p): return model(p,fq)-sm
p0=[700,1.2,2450,5,0.6,0.0,4000,0]
lb=[200,0.3,1800,1,0,-np.pi,1500,-80]; ub=[1500,5,3200,30,1,np.pi,20000,80]
r=so.least_squares(err,p0,bounds=(lb,ub))
print('params fs,Qs,fh,Qh,g,ph,fl,G =',np.round(r.x,3).tolist(),'rms dB',round(np.sqrt(np.mean(r.fun**2)),2))
for f in [300,500,700,1000,1500,2000,2450,3000,3500,4000,5000,6000,8000]:
    i=np.argmin(abs(fq-f)); print(f,'meas %.1f model %.1f'%(sm[i]-sm.max(),model(r.x,fq[i:i+1])[0]-sm.max()))
