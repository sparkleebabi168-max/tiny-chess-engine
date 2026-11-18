import os,sys,json,urllib.request
P,N,B,R,Q,K=1,2,3,4,5,6
V=[0,100,310,320,500,900,20000]
ND=(-33,-31,-18,-14,14,18,31,33)
BD=(-17,-15,15,17)
RD=(-16,-1,1,16)
QD=BD+RD

class E:
  def __init__(s):s.reset()
  def reset(s):
    s.b=[0]*128
    r=[R,N,B,Q,K,B,N,R]
    for c in range(8):s.b[c],s.b[16+c],s.b[96+c],s.b[112+c]=r[c],P,-P,-r[c]
    s.side=1
  def s2u(s,p):return chr(97+(p&7))+str(8-(p>>4))
  def u2s(s,u):return(8-int(u[1]))*16+ord(u[0])-97
  def gen(s):
    m=[]
    for q in range(128):
      if q&0x88:continue
      p=s.b[q]
      if p*s.side<=0:continue
      t=abs(p)
      if t==P:
        f=q-16*s.side
        if not(f&0x88) and not s.b[f]:
          m.append((q,f,0))
          d=q-32*s.side
          if((s.side==1 and(q>>4)==6)or(s.side==-1 and(q>>4)==1))and not s.b[d]:m.append((q,d,0))
        for c in(q-16*s.side-1,q-16*s.side+1):
          if not(c&0x88) and s.b[c]*s.side<0:m.append((q,c,abs(s.b[c])))
      elif t in(N,K):
        for d in(ND if t==N else QD):
          x=q+d
          if not(x&0x88) and s.b[x]*s.side<=0:m.append((q,x,abs(s.b[x])))
      else:
        for d in(BD if t==B else(RD if t==R else QD)):
          x=q+d
          while not(x&0x88):
            v=s.b[x]
            if not v:m.append((q,x,0))
            elif v*s.side<0:m.append((q,x,abs(v)));break
            else:break
            x+=d
    m.sort(key=lambda x:x[2],reverse=True)
    return m
  def move(s,f,t):
    p,cap=s.b[f],s.b[t]
    s.b[t],s.b[f]=p,0
    if abs(p)==P and(t>>4)in(0,7):s.b[t]=Q*(1 if p>0 else-1)
    s.side=-s.side
    return cap
  def unmove(s,f,t,p,cap):
    s.b[f],s.b[t]=p,cap
    s.side=-s.side
  def evaluate(s):
    v=0
    for q in range(128):
      if q&0x88:continue
      p=s.b[q]
      if not p:continue
      g=1 if p>0 else-1
      w=V[abs(p)]+(3.5-abs((q&7)-3.5))*6
      if abs(p)==P:w+=(7-(q>>4)if g==1 else(q>>4))*8
      v+=g*w
    return v*s.side
  def search(s,d,a,b):
    if d<=0:return s.evaluate()
    ms=s.gen()
    if not ms:return-10000
    best=-30000
    for f,t,_ in ms:
      o,c=s.b[f],s.move(f,t)
      sc=-s.search(d-1,-b,-a)
      s.unmove(f,t,o,c)
      if sc>best:best=sc
      if sc>a:a=sc
      if a>=b:break
    return best
  def best(s,d=3):
    ms=s.gen()
    if not ms:return '0000'
    bsc,bm=-30000,ms[0]
    for f,t,_ in ms:
      o,c=s.b[f],s.move(f,t)
      sc=-s.search(d-1,-30000,30000)
      s.unmove(f,t,o,c)
      if sc>bsc:bsc,bm=sc,(f,t)
    return s.s2u(bm[0])+s.s2u(bm[1])

def run_env(e,u):
  while 1:
    try:
      with urllib.request.urlopen(f'{u}/game',timeout=10) as r:g=json.loads(r.read())
      if g.get('status')in('finished','adjudicated'):break
      e.reset()
      for m in g.get('moves',[]):e.move(e.u2s(m[:2]),e.u2s(m[2:4]))
      p=urllib.request.Request(f'{u}/move',data=json.dumps({'move':e.best()}).encode(),headers={'Content-Type':'application/json'})
      urllib.request.urlopen(p,timeout=10)
    except Exception:break

def main():
  e=E()
  env=os.environ.get('MAKEFUN_ENV_URL')
  if env:return run_env(e,env)
  while 1:
    l=sys.stdin.readline()
    if not l:break
    w=l.strip().split()
    if not w:continue
    c=w[0]
    if c=='uci':print('id name TinyChess\nid author Antigravity\nuciok',flush=True)
    elif c=='isready':print('readyok',flush=True)
    elif c=='ucinewgame':e.reset()
    elif c=='position':
      e.reset()
      if 'moves' in w:
        for m in w[w.index('moves')+1:]:e.move(e.u2s(m[:2]),e.u2s(m[2:4]))
    elif c=='go':print(f'bestmove {e.best()}',flush=True)
    elif c=='quit':break

if __name__=='__main__':main()
