# %%
import populate_network as pn
import pandas as pd
import networkx as nx
from infomap import Infomap
# %%
df_continguts = pd.read_csv('darreres_dades.csv',sep=';')
print(df_continguts.head())
# materia = ['Física']
# materia = ['Matemàtiques II']
materia = ['Física','Matemàtiques II']
# %%
df_fisica = df_continguts[df_continguts['Matèria'].isin(materia)]
df_fisica.head()
# %%
g_fisica = pn.full_undir_network(df_fisica)
# %%
# nodes = list(g_fisica.nodes())
# for node in nodes:
#     mat = node.split('.')[0]
#     if mat == 'F':
#         g_fisica.remove_node(node)
# %%
bloc_dict = dict()
mat_dict = dict()
cont_dict = dict()
for node in g_fisica.nodes():
    # print(node,list(df_fisica[df_fisica['Id']==node]['Bloc']))
    bloc_dict[node] = list(df_fisica[df_fisica['Id']==node]['Bloc'])[0]
    mat_dict[node] = list(df_fisica[df_fisica['Id']==node]['Matèria'])[0]
    cont_dict[node] = list(df_fisica[df_fisica['Id']==node]['Contingut'])[0]
bloc_list = list(set(bloc_dict.values()))
color_dict = dict()
clist = []
for node in g_fisica.nodes():
    color_dict[node] = bloc_list.index(bloc_dict[node])
    clist.append(bloc_list.index(bloc_dict[node])) 
nx.set_node_attributes(g_fisica,bloc_dict,name='Bloc')
nx.set_node_attributes(g_fisica,mat_dict,name='Materia')
nx.set_node_attributes(g_fisica,cont_dict,name='Contingut')
nx.set_node_attributes(g_fisica,color_dict,name='color')
# %% 
# compute centralities and give top 10
# nodes = list(g_fisica.nodes())
# for node in nodes:
#     mat = node.split('.')[1]
#     if mat == '1':
#         g_fisica.remove_node(node)
# degree 
deg = dict(nx.degree(g_fisica))
df_centralities = pd.DataFrame.from_dict({
    'node': list(deg.keys()),
    'degree': list(deg.values())
})
# closeness
cc = nx.closeness_centrality(g_fisica)
df_centralities['closeness'] = df_centralities['node'].map(cc)
# betweenness
bc = nx.betweenness_centrality(g_fisica)
df_centralities['betweenness'] = df_centralities['node'].map(bc)

df_centralities = df_centralities.sort_values('degree', ascending=False)
df_centralities.head(10)
# %%
fout = open('table_degree_'+'_'.join(materia)+'.tex','w')
fout.write("Identificador & Matèria & Bloc & Contingut & Grau & Proximitat & Intermediació\\\\ \hline \n")
i=0
for index,row in df_centralities.iterrows():
    if i < 10:
        node = row['node']
        mat = mat_dict[node]
        bloc = bloc_dict[node]
        cont = cont_dict[node]
        fout.write(node+" & "+mat+" & "+bloc+" & "+cont+" & " +str(row['degree'])+" & "+str(round(row['closeness'],3))+" & "+str(round(row['betweenness'],3))+" \\\\ \hline \n")
        i+=1

fout.close()

# %%
import matplotlib.pyplot as plt
plt.scatter(list(df_centralities['degree']), list(df_centralities['closeness']), label='Proximitat')
plt.scatter(list(df_centralities['degree']), list(df_centralities['betweenness']), label='Intermediació')
# plt.scatter(list(df_centralities['closeness']), list(df_centralities['betweenness']))
# plt.xscale('log')
plt.yscale('log')
# plt.xlim(3,100)
# # plt.xlim(0.5,1.1)
# plt.ylim(4e-1,1.1)
plt.xlabel('Grau', fontsize=25)
plt.ylabel('Centralitat', fontsize=25)
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.legend(fontsize = 20)
plt.savefig('centralitats_'+'_'.join(materia)+'.png',bbox_inches='tight')
# plt.show()
# # %%
# int_type = dict()
# for edge in g_fisica.edges():
#     mat1 = edge[0].split('.')[0]
#     mat2 = edge[1].split('.')[0]
#     if mat1 != mat2:
#         int_type[edge] = 'FM'
#     elif mat1 == 'F':
#         int_type[edge] = 'FF'
#     else:
#         int_type[edge] = 'MM'
# nx.set_edge_attributes(g_fisica,int_type,name='inter')


# %%
# nx.draw(g_fisica, with_labels=True, node_color = clist)



# %%
# c = list(nx.algorithms.community.greedy_modularity_communities(g_fisica))
# print(len(c))
# clist_modules = []
# for node in g_fisica.nodes():
#     for i in range(3):
#         if node in c[i]:
#             clist_modules.append(i)
# nx.draw(g_fisica, with_labels=True, node_color = clist_modules)
# %% estructura de comunitats amb infomap i excluint els blocs 1

g_copy = g_fisica.copy()

nodes = list(g_copy.nodes())
for node in nodes:
    mat = node.split('.')[1]
    if mat == '1':
        g_copy.remove_node(node)


node_num = dict()
inv_num = dict()
i = 0
for node in g_copy.nodes():
    node_num[node] = i
    inv_num[i] = node
    i += 1

im = Infomap()
for edge in g_copy.edges():
    im.add_link(node_num[edge[0]],node_num[edge[1]])
im.run()
print(f"Found {im.num_top_modules} modules with codelength: {im.codelength}")

print("Result")
print("\n#node module")


# print('F.4.10' in g_copy.nodes())
# print('F.4.10' in g_fisica.nodes())
# print('F.4.10' in inv_num.keys())
# print('F.4.10' in mat_dict.keys())
# print('F.4.10' in bloc_dict.keys())
# print('F.4.10' in cont_dict.keys())

fout = open('modules_'+"_".join(materia)+'.dat','w')
fout.write('Mòdul & Identificador & Matèria & Bloc & Contingut\\\\ \hline \n')
module_dict_im = dict()
for node in im.tree:
    if node.is_leaf:
        print(node.node_id, node.module_id)
        node_good = inv_num[node.node_id]
        module_dict_im[node_good] = node.module_id
        fout.write(str(node.module_id)+' & '+node_good+' & '+mat_dict[node_good]+' & '+bloc_dict[node_good]+' & '+cont_dict[node_good]+' \\ \n')
fout.close()

for node in g_fisica.nodes():
    if node not in g_copy.nodes():
        module_dict_im[node] = -1

nx.set_node_attributes(g_fisica,module_dict_im,name='module')

nx.write_gml(g_fisica, "_".join(materia)+".gml")

# clist_im = []
# for node in g_fisica.nodes():
#     clist_im.append(color_dict_im[node])

# nx.draw(g_fisica, with_labels=True, node_color = clist_im)
