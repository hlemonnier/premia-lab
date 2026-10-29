"""Published-characteristic nearest peers; no outcomes or future dates."""
from __future__ import annotations
import numpy as np
from scipy.sparse import csr_matrix
from model_f import engine as E

class PeerGraph:
    def __init__(self):
        self.anchor=None;self.matrix=None
        self.diagnostics=dict(max_self_weight=0.,max_row_error=0.,updates=0,min_degree=None,max_degree=0)
    def at(self,X,s):
        anchor=(int(s)//21)*21
        if anchor==self.anchor:return self.matrix
        z=np.ascontiguousarray(E.basis(X[anchor],4.)[:,:13]);n=len(z)
        if n==1:
            a=csr_matrix((1,1),dtype=np.float64);degree=np.zeros(1)
        else:
            norm=np.sum(z*z,axis=1)
            dist=np.maximum(norm[:,None]+norm[None,:]-2.*(z@z.T),0.)
            np.fill_diagonal(dist,np.inf);k=min(32,n-1)
            threshold=np.partition(dist,k-1,axis=1)[:,k-1]
            links=dist<=threshold[:,None]+1e-12;np.fill_diagonal(links,False)
            degree=links.sum(1);i,j=np.nonzero(links)
            a=csr_matrix((1./degree[i],(i,j)),shape=(n,n))
        dg=self.diagnostics
        dg['max_self_weight']=max(dg['max_self_weight'],float(np.max(np.abs(a.diagonal()),initial=0.)))
        expected=np.ones(n) if n>1 else np.zeros(n)
        dg['max_row_error']=max(dg['max_row_error'],float(np.max(np.abs(np.asarray(a.sum(1)).ravel()-expected),initial=0.)))
        dg['min_degree']=int(degree.min()) if dg['min_degree'] is None else min(dg['min_degree'],int(degree.min()))
        dg['max_degree']=max(dg['max_degree'],int(degree.max()));dg['updates']+=1
        self.anchor=anchor;self.matrix=a
        return a
