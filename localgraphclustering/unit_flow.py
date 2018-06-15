# import Queue as queue
import queue

def push(A,f,f_v,v,u,l,ex,U,n,w,degree):
    
    pushed = 0
    
    # !! Number of nodes ??
    if v < u:
        idx = v*n - v*(v+1)/2 + (n-1 - (n-u))-v
        same_dir = 1
    else:
        idx = u*n - u*(u+1)/2 + (n-1 - (n-v))-u
        same_dir = -1
    
    if idx not in f:
        f[idx] = 0
    
    r = min(l[v], U) - same_dir * f[idx]
    
    if (r > 0) and (l[v] > l[u]):
        if u not in f_v:
            f_v[u] = 0
        
        if u not in degree:
            degree[u] = A.get_degree(u)
            TOUCH.add(u)
        
        degree_val = degree[u]
        psi = min(ex[v], r, w * degree_val - f_v[u])
        f[idx] += same_dir * psi
        f_v[v] -= psi
        f_v[u] += psi
        pushed = 1
        
    return pushed

def relabel(v,l):
    l[v] += 1
    
def push_relabel(A,f,f_v,U,v,current_v,ex,l,n,w,degree):
    
    index      = (current_v[v])[0]
    num_neigh  = (current_v[v])[1]
    neighbors  = (current_v[v])[2]
    u          = neighbors[index]
    if u not in l:
        l[u] = 0
    
    pushed = push(A,f,f_v,v,u,l,ex,U,n,w,degree)
    
    relabelled = 0
    
    if 1-pushed:
        if index < num_neigh-1:
            current_v[v] = [index+1,num_neigh,neighbors]
        else:
            relabel(v,l)
            relabelled = 1
            current_v[v] = [0,num_neigh,neighbors]
            
    return pushed,relabelled,u 
            
def update_excess(A,f_v,v,ex,degree):
    if v not in degree:
        degree[v] = A.get_degree(v)
        TOUCH.add(v)
    
    degree_val = degree[v]
    
    ex_ = max(f_v[v] - degree_val,0)
    if (v not in ex) and (ex_ == 0):
        return
    
    ex[v] = ex_

def add_in_Q(v,l,Q,A,current_v):
    Q.put([l[v],v])
    neighbors = A.get_neighbors(v)
    TOUCH.add(v)
    current_v[v] = [0,len(neighbors),neighbors]
    
def remove_from_Q(v,Q):
    Q.get()
    
def shift_from_Q(v,l,Q): 
    Q.get()
    Q.put([l[v],v])

def unit_flow(A, delta, U, h, w, degree):
    
    # Assumption on edge directions: based on two loops to read A.
    # Outer loop is rows and inner loop is columns. The variables for the algorithm
    # correspond to edges based on the direction imposed by reading A this way.
    
    # Dimensions
    n = A.shape[0]
    N = n * (n-1) / 2
    
    # Variables and parameters
    f         = {}
    l         = {}
    ex        = {}
    f_v       = {}
    current_v = {}
    
    Q = queue.PriorityQueue()
    
    for i in delta:
        f_v[i] = delta[i]
        l[i] = 0
        if i not in degree:
            degree[i] = A.get_degree(i)
        
        if delta[i] > degree[i]:
            l[i] = 1
            Q.put([1, i])
            ex[i] = delta[i] - degree[i]
            neighbors = A.get_neighbors(i)
            current_v[i] = [0, len(neighbors), neighbors]
    
    while Q.qsize() > 0:
        
        v = (Q.queue[0])[1]
        
        pushed,relabelled,u = push_relabel(A,f,f_v,U,v,current_v,ex,l,n,w,degree)
        
        if pushed:
            update_excess(A,f_v,u,ex,degree)
            update_excess(A,f_v,v,ex,degree)
                
            if ex[v] == 0:
                remove_from_Q(v,Q)
            if (u in ex) and (ex[u] > 0):
                add_in_Q(u,l,Q,A,current_v)
                
        if relabelled:
            if l[v] < h:
                shift_from_Q(v,l,Q)
            else:
                remove_from_Q(v,Q)
               
    return l,f_v,ex