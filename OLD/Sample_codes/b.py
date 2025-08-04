a=14.812490474044374
b=14.048152191979261
c=12.791093177913064
print((a+b+c)/30)



sources=[]
dest=[]
def find_source_dest_pair(prev,n,nxt,trx_amt):
    global sources,dest
    # Source identification
    l=nx.shortest_path(G,target=nxt,weight=lambda u,v,d:edge_cost(u,v,d,trx_amt))
    for i in l.values():
        txt="".join(map(str,i))
        f="".join(map(str,[prev,n,nxt]))
        if f in txt:
            sources.append(i[0])
    # Destination finding
    l=nx.shortest_path(G,source=prev,weight=lambda u,v,d:edge_cost(u,v,d,trx_amt))
    for i in l.values():
        txt="".join(map(str,i))
        f="".join(map(str,[prev,n,nxt]))
        if f in txt:
            dest.append(i[-1])
    s=0
    l_src={}
    l_dest={}
    for i in sources:
        for j in dest:
            sp=nx.shortest_path(G,source=i,target=j,weight=lambda u,v,d:edge_cost(u,v,d,trx_amt))
            txt="".join(map(str,sp))
            f="".join(map(str,[prev,n,nxt]))
            if f in txt:
                if i not in l_src:
                    l_src[i]=1
                else:
                    l_src[i]+=1
                if j not in l_dest:
                    l_dest[j]=1
                else:
                    l_dest[j]+=1
                s+=1
    max=0
    src=""
    dest=''
    for i in l_src:
        if l_src[i]>max:
            max=l_src[i]
            src=i
        print(f"probability of Source {i} ",l_src[i]/s)
    max=0
    for i in l_dest:
        if l_dest[i]>max:
            max=l_dest[i]
            dest=i
        print(f"probability of Dest {i} ",l_dest[i]/s)
    print(f"Source - {src}  Dest - {dest} ")
 
    print("Entropy analysis")
    H=0
    print("P(Bi|A)=P(A|Bi)/sum(P(A|Bk))")
    for i in sources:
        a=list(nx.shortest_path(G,source=i,weight=lambda u,v,d:edge_cost(u,v,d,trx_amt)))
        u=0
        for i in a:
            if n in i:
                if n !=i[-1]:
                    u+=1
        print(f"P(A|Bi)= {u/len(a)}")
        pabi=u/len(a)
        s=0
        for j in sources:
            b=list(nx.shortest_path(G,source=j,weight=lambda u,v,d:edge_cost(u,v,d,trx_amt)))
            u=0
            for i in b:
                if n in i:
                    if n !=i[-1]:
                        u+=1
            s+=u/len(b)
        H+=((pabi/s)*math.log2(pabi/s))
    print(-1*H)


    