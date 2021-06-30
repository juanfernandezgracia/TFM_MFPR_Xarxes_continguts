# %%
import networkx as nx
import pandas as pd
import os
from random import sample
import time
# %%
def read_data(fname=None):
    """
    Reads the data that we have already. It can read the data from a file that is given (from a previous run of the program).
    Also reads which connections have been checked. It looks if a file named checked.dat exists. If it exists, it contains 1 line with id1:id2 separated by commas.
    """
    if fname==None:
        if os.path.exists('darreres_dades.csv'):
            fname = 'darreres_dades.csv'
        else:
            fname = 'xarxa_FIS_MAT_QUI_BAT.csv'
    df_continguts = pd.read_csv(fname,sep=';')
    if os.path.exists('checked.dat'):
        fin = open('checked.dat')
        checked = fin.readline().split(',')
    else: 
        checked = []
    timestr = time.strftime("%Y%m%d-%H%M%S")
    df_continguts.to_csv('copia_dades_'+timestr+'.csv',index=False)
    fout=open('copia_checked_'+timestr+'.dat','w')
    fout.write(','.join(checked))
    fout.close()
    return df_continguts, checked
# %%
def missing_connections(materia_1, materia_2,df_continguts,checked):
    """
    Create a list with the connections still to check
    """
    connect_list = []
    if materia_1 == materia_2:
        c_list = list(df_continguts[df_continguts['Matèria']==materia_1]['Id'])
        for i in range(len(c_list)-1):
            for j in range(i+1,len(c_list)):
                connect_list.append(':'.join([c_list[i],c_list[j]]))
    else:
        c1_list = list(df_continguts[df_continguts['Matèria']==materia_1]['Id'])
        c2_list = list(df_continguts[df_continguts['Matèria']==materia_2]['Id'])
        for c1 in c1_list:
            for c2 in c2_list:
                connect_list.append(':'.join([c1,c2]))
    to_check = set(connect_list)-set(checked)
    return to_check
# %%
def dir_network(df):
    """
    create the directed network from the data
    """
    g_dir = nx.DiGraph()
    for index,row in df.iterrows():
        if not pd.isnull(row['Necessari per']):
            neighbors = row['Necessari per'].split(',')
            for neigh in neighbors:
                g_dir.add_edge(row['Id'],neigh)
    return g_dir
# %%
def undir_network(df):
    """
    create the undirected network from the data
    """
    g_dir = nx.Graph()
    for index,row in df.iterrows():
        if not pd.isnull(row['Relacionat amb']):
            neighbors = row['Relacionat amb'].split(',')
            for neigh in neighbors:
                g_dir.add_edge(row['Id'],neigh)
    return g_dir
# %%
def full_undir_network(df):
    """
    create the undirected network from the data taking into account directed and undirected relations and putting them all as undirected
    """
    g_dir = nx.Graph()
    for index,row in df.iterrows():
        if not pd.isnull(row['Relacionat amb']):
            neighbors = row['Relacionat amb'].split(',')
            for neigh in neighbors:
                g_dir.add_edge(row['Id'],neigh)
        if not pd.isnull(row['Necessari per']):
            neighbors = row['Necessari per'].split(',')
            for neigh in neighbors:
                g_dir.add_edge(row['Id'],neigh)
    return g_dir
# %%
def escollir_materies():
    materia_dict ={1:'Física',
                   2:'Matemàtiques I',
                   3:'Matemàtiques II',
                   4:'Física i Química',
                   5:'Química'}
    print("Hola! Gràcies per voler contribuïr a recollir les relacions entre continguts del curriculum.\n Et demanaré un parell de dades primer per veure quines dades recollim.\n Hauràs d'escollir dues matèries (poden ser la mateixa) per a trobar relacions entre la primera i la segona.\n Quina vols que sigui la primera?\n1-Física 2n BAT\n2-Matemàtiques 1r BAT\n3-Matemàtiques 2n BAT\n4-Física i Química 1r BAT\n5-Química 2n BAT\n")
    i_1 = int(input('--> '))
    print("Quina vols que sigui la segona?\n1-Física 2n BAT\n2-Matemàtiques 1r BAT\n3-Matemàtiques 2n BAT\n4-Física i Química 1r BAT\n5-Química 2n BAT\n")
    i_2 = int(input('--> '))
    materia_1 = materia_dict[i_1]
    materia_2 = materia_dict[i_2]
    return materia_1,materia_2
# %%
def ask_relation(to_check, df_continguts, checked):
    check = sample(to_check,1)[0]
    id1 = check.split(':')[0]
    id2 = check.split(':')[1]
    c1 = list(df_continguts[df_continguts['Id']==id1]['Contingut'])[0]
    c2 = list(df_continguts[df_continguts['Id']==id2]['Contingut'])[0]
    # print(c1,c2)
    print("Volem comprobar la relació entre els següents continguts:\n \n 1-"+c1+"\n\n 2-"+c2+"\n\n Veus alguna relació entre els continguts?\n   1- 1 és necessari per a 2.\n   2- 2 és necessari per a 1.\n   3- Estan relacionats però no son requisits l'un de l'altre.\n   4- No ténen cap relació.\n   5- Passo.\n")
    kk = input('--> ')
    if kk in ['1','2','3','4']:
        if kk == '1':
            # 1->2
            if list(pd.isnull(df_continguts[df_continguts['Id']==id1]['Necessari per']))[0]:
                nec_list = []
            else:
                nec_list = list(df_continguts[df_continguts['Id']==id1]['Necessari per'])[0].split(',')
            nec_list.append(id2)
            ind = list(df_continguts.index[df_continguts['Id']==id1])[0]
            df_continguts.loc[ind,'Necessari per'] = ','.join(nec_list)
        elif kk == '2':
            # 2->1
            if list(pd.isnull(df_continguts[df_continguts['Id']==id2]['Necessari per']))[0]:
                nec_list = []
            else:
                nec_list = list(df_continguts[df_continguts['Id']==id2]['Necessari per'])[0].split(',')
            nec_list.append(id1)
            ind = list(df_continguts.index[df_continguts['Id']==id2])[0]
            df_continguts.loc[ind,'Necessari per'] = ','.join(nec_list)
        elif kk == '3':
            # 1--2
            if list(pd.isnull(df_continguts[df_continguts['Id']==id1]['Relacionat amb']))[0]:
                rel_list = []
            else:
                rel_list = list(df_continguts[df_continguts['Id']==id1]['Relacionat amb'])[0].split(',')
            rel_list.append(id2)
            ind = list(df_continguts.index[df_continguts['Id']==id1])[0]
            df_continguts.loc[ind,'Relacionat amb'] = ','.join(rel_list)
            if list(pd.isnull(df_continguts[df_continguts['Id']==id2]['Relacionat amb']))[0]:
                rel_list = []
            else:
                rel_list = list(df_continguts[df_continguts['Id']==id2]['Relacionat amb'])[0].split(',')
            rel_list.append(id1)
            ind = list(df_continguts.index[df_continguts['Id']==id2])[0]
            df_continguts.loc[ind,'Relacionat amb'] = ','.join(rel_list)
        to_check.remove(check)
        checked.append(':'.join([id1,id2]))
        checked.append(':'.join([id2,id1]))

    print("Vols respondre una altra relació? (S/n)")
    resposta = input('--> ')
    return resposta, checked, to_check, df_continguts
# %%
def exit_program(df_continguts,checked,to_check):
    fname = 'darreres_dades.csv'
    df_continguts.to_csv(fname,sep=';',index=False)
    fout = open('checked.dat','w')
    fout.write(','.join(checked))
    fout.close()
    print("Ja només quedaven "+str(len(to_check))+" relacions per comprobar. Adéu!!")
    return
# %%
def main():
    """
    Here I write the program for gathering the information about the connections among contents in the curricula
    """
    resposta = 'N'
    while resposta not in ['S','s','']:
        materia_1,materia_2 = escollir_materies()
        print(' '.join(["Has escollit",materia_1,'i',materia_2]))
        print("Estàs d'acord? (S/n)")
        resposta = input('--> ')
    print("Nom del fitxer de dades amb dades prèvies? (deixar en blanc per agafar les darreres dades guardades)")
    fname = input('--> ')
    if len(fname)==0:
        fname = None
    df_continguts,checked = read_data(fname)
    to_check = missing_connections(materia_1, materia_2,df_continguts,checked)
    print("Tenim "+str(len(to_check))+" relacions per comprobar... Comencem!\n")
    # print(df_continguts.head())
    resposta = 's'
    while resposta in ['s','S',''] and len(to_check) > 0:
        resposta,checked,to_check,df_continguts = ask_relation(to_check, df_continguts, checked)
        print("Tenim "+str(len(to_check))+" relacions per comprobar...\n")
    exit_program(df_continguts,checked,to_check)

# %%
if __name__=='__main__':
    main()