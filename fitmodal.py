import numpy as np, scipy.io.wavfile as w, scipy.signal as ss, scipy.optimize as so, json
sr,x=w.read('post.wav'); x=x.astype(float)/32768
K=32335.0; fc=K/5
segs=[(7.6,11.3)]
fq,P=ss.welch(x[int(7.6*sr):int(11.3*sr)],sr,nperseg=2048)
m=(fq>150)&(fq<10000); fq=fq[m]; P=P[m]
env=np.sinc(fq/fc)**2+3e-3
meas=10*np.log10(P/env)
sm=np.array([meas[(fq>f/1.025)&(fq<f*1.025)].mean() for f in fq]); sm-=sm.max()
M=5
def H(p,f):
    s=2j*np.pi*f; fs,Qs=p[0],p[1]; ws=2*np.pi*fs
    hp=s*s/(s*s+s*ws/Qs+ws*ws)
    tot=0
    for i in range(M):
        fi,Qi,gi=p[2+3*i:5+3*i]; wi=2*np.pi*fi
        tot=tot+gi*(s*wi/Qi)/(s*s+s*wi/Qi+wi*wi)
    return hp*tot
def mdl(p,f): return 20*np.log10(np.abs(H(p,f))+1e-9)+p[-1]
best=None
rng=np.random.default_rng(1)
for trial in range(40):
    fi0=np.sort(rng.uniform(500,7000,M)) if trial else np.array([800,1600,2500,3000,4600])
    p0=[400,0.8]; lb=[100,0.3]; ub=[1500,3]
    for f in fi0: p0+= [f,3,rng.uniform(-1,1)]; lb+=[300,0.5,-5]; ub+=[9000,30,5]
    p0+=[0]; lb+=[-60]; ub+=[60]
    try:
        r=so.least_squares(lambda p: mdl(p,fq)-sm,p0,bounds=(lb,ub),max_nfev=4000)
    except Exception as e: continue
    e=np.sqrt(np.mean(r.fun**2))
    if best is None or e<best[0]: best=(e,r.x)
e,p=best; print('rms dB',round(e,2))
print('hp',np.round(p[:2],2).tolist())
for i in range(M): print('mode',np.round(p[2+3*i:5+3*i],3).tolist())
print('G',round(p[-1],2))
for f in [200,300,500,700,1000,1500,2000,2450,3000,3500,4000,5000,6000,8000]:
    i=np.argmin(abs(fq-f)); print(f,'meas %.1f model %.1f'%(sm[i],mdl(p,fq[i:i+1])[0]))
json.dump({'hp':p[:2].tolist(),'modes':[p[2+3*i:5+3*i].tolist() for i in range(M)],'G':p[-1]},open('speaker_fit.json','w'))
